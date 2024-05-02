from flask import Flask, render_template, session, request, redirect
from flask_wtf import CSRFProtect
import jwt
import hashlib
from datetime import datetime,timedelta
import requests
import sqlite3
import bleach
from dotenv import dotenv_values

ENV = dotenv_values(".env")

app = Flask(__name__)
app.secret_key = ENV["SECRET_KEY"]
csrf = CSRFProtect(app)

toExcept = ["jwt","csrf_token"]

def db_connection(db_name):
    conn = sqlite3.connect(f"./db/{db_name}.db")
    conn.row_factory = sqlite3.Row
    
    return conn

def get_json(tJson):
     return float(tJson.json()["data"]["buy"])


def get_price(value):
    return get_json(requests.get(f"https://api.kucoin.com/api/v1/market/stats?symbol={value}-EUR"))

def give_rating(rating):
    c = 0
    h = 0
    if type(rating)!=int:
            h = 1
            c = int(rating-0.5)     
    else:
            c = rating
    
    return [c,h,5-(c+h)]

def token_gen(userid,username):
    token = jwt.encode({
    "username" : username,
    "userid" : userid,
    "exp" : datetime.utcnow() + timedelta(seconds=3600)
    },
    ENV["JWT_KEY"],algorithm='HS256')

    return token


def pop_session(toExcept):
    try:
        #it's horrible I know but I can't directly pop session vars :(
        values = []
        for s in session:
            if s not in toExcept:
                values.append(s)

        for val in values:
            session.pop(val)

    except:
        pass

def token_decode():
    if(session.get("jwt")):   
        try:
            data = jwt.decode(session.get("jwt"),ENV["JWT_KEY"] ,algorithms=['HS256',])
            return [True,data]
        
        #jwt.exceptions.DecodeError
        #jwt.exceptions.ExpiredSignatureError
        except:
            pop_session([])
    
    else:
         pop_session([])


    return [False]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def check_form(form,form_values):
    for f in form_values:
        if form[f] == False:
            return False
        
    return True


def check_reg(data,minD,maxD):
    return True if len(data) >= minD and len(data) <= maxD else False


def subtotal_count(price,pm,quantity):
    return rnd(rnd(price/get_price(pm))*quantity)

def subtotal_round(subtotal):
    for x in range(len(subtotal)):
        subtotal[x] = rnd(subtotal[x])

def rnd(number):
    return round(number,4)

@app.errorhandler(404)
def notFound(e):
    return redirect("/")
@app.errorhandler(400)
def bad(e):
    return redirect(request.path)

@app.route("/")
def index():
    if(token_decode()[0]):
            return render_template("index.html",username=token_decode()[1]["username"]) 
    else:
        return redirect("/login")



@app.route("/shop",methods=['POST', 'GET'])
def shop():
    if request.method == "POST":
        f = dict(request.form)["id"]

        try:
            session[f] += 1

        except KeyError:
             session[f] = 1

    if(token_decode()[0]):
        conn = db_connection("products")
        pr = conn.execute("SELECT * FROM products").fetchall()
        conn.close()

        return render_template("shop.html",products=pr,market=[get_price("BTC"),get_price("ETH")],give_rating=give_rating,rnd=rnd)
    else:
        return redirect("/login")


@app.route("/cart",methods=["GET", "POST"])
def cart():
    msg = [None]
    success = False

    if request.method == "POST":
        try:
            form = request.form
                
            if(len(form)==2): #item management
                form = dict(form)["id"]

                product_id = form[:len(form)-1] #10+ -> 10

                #form[len(form)-1] -> action => + | -
                if form[len(form)-1] == "+":
                    session[product_id] += 1
                
                elif form[len(form)-1] == "-":
                    session[product_id] -= 1
                    
                    if(session[product_id] == 0):
                        session.pop(product_id)
            
            elif(len(form)==4): #order save
                if(form['state'] in ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]):
                    zipcode = int(form["zipcode"])

                    conn = db_connection("orders")

                    items_string = ""
                    subtot = [0,0]

                    for f in session:
                        if f not in toExcept:

                            for val in db_connection("products").execute("SELECT * FROM products WHERE id=?",(f,)).fetchall():
                                val = dict(val)

                                items_string+= f"{val['name']} - x{session[f]}\n\n"

                                subtot[0] += subtotal_count(val['price'],"BTC",session[f])
                                subtot[1] += subtotal_count(val['price'],"ETH",session[f])

                                subtotal_round(subtot)

                    conn.execute("INSERT INTO `orders` (`id`,`username`, `items` ,`subtotal`  ,`ps_address`, `state`, `zipcode`, `paid`, `delivered`) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",(token_decode()[1]["username"], items_string, f"{subtot[0]} - {subtot[1]}",bleach.clean(form["ps_address"]), form["state"], zipcode, 0, 0,))
                    conn.commit()
                    conn.close()

                    pop_session(toExcept)

                    success = True

        except:
            #someone edit the form values (reject the request)
            pass
        
    if(token_decode()[0]):
            conn = db_connection("products")

            cart = []

            subtotal = [0,0]

            for f in session:
                if f not in toExcept:     
                    for val in conn.execute("SELECT * FROM products WHERE id=?",(f,)).fetchall():
                        val = dict(val)

                        #prices
                        val["quantity"] = session[f]

                        val["btc"] = rnd(val["price"]/get_price("BTC"))
                        val["eth"] = rnd(val["price"]/get_price("ETH"))


                        subtotal[0]+= subtotal_count(val['price'],"BTC",val['quantity'])
                        subtotal[1]+= subtotal_count(val['price'],"ETH",val['quantity'])
                        
                        subtotal_round(subtotal)

                        cart.append(val)

            conn.close()
            
            if(len(cart)==0 and success == False):
                msg[0] = "YOUR CART is EMPTY !"
            
            elif success:
                msg[0] = "S-ORDER SENT !"

            return render_template("cart.html",cart=cart,subtotal=subtotal,msg=msg)
    else:
        return redirect("/login")



@app.route("/login",methods=["GET", "POST"])
def login():
        
    if(token_decode()[0]):

        return redirect("/")
    
    else:
        msg = [None]

        if request.method == "POST":
            form_values = ["username", "password"]

            form = request.form

            error = False
            
            if(check_form(form,form_values)):
                if(check_reg(form["username"],6,12)):
                    username = bleach.clean(form["username"])

                    conn = db_connection("users")
                    dataUser = conn.execute("SELECT * FROM users WHERE username=?",(username,)).fetchall()

                    if len(dataUser) == 1:
                        dataUser = dict(dataUser[0])

                        if(dataUser["password"] == hash_password(form["password"])):
                            session["jwt"] = token_gen(dataUser['id'],username)

                            return redirect("/")

                        else:
                            msg[0] = "USERNAME or PASSWORD are NO CORRECT !"

                    else:
                        msg[0] = "USERNAME or PASSWORD are NO CORRECT !"

                else:
                    msg[0] = "USERNAME or PASSWORD are NO CORRECT !"

        return render_template("login.html",msg=msg)

@app.route("/register", methods=["GET","POST"])
def register():
    msg = [None]
    if(token_decode()[0]):
        return redirect("/")
    
    else:
        if request.method == "POST":
            form_values = ["username","email","password","confirm_password","age","gender"]
            form = request.form


            if(check_form(form,form_values)):
                if(check_reg(form["username"],6,12)):

                    if(check_reg(form["email"],6,50)):

                        if((check_reg(form["password"],6,30) and check_reg(form["confirm_password"],6,30)) and form["password"] == form["confirm_password"]):
                            
                            age = int(form["age"])
                            if(age >= 18 and age <= 100):

                                if(form["gender"] in ["Male","Female"]):
                                    username = bleach.clean(form["username"])
                                    conn = db_connection("users")

                                    s = conn.execute("SELECT * FROM users WHERE username=?",(username,)).fetchall()
                                    if len(s) == 0:
                                        conn.execute("INSERT INTO `users` (`id`,`username`, `password`, `email`, `age`, `gender`) VALUES (NULL, ?, ?, ?, ?, ?)",(username, hash_password(form["password"]), bleach.clean(form["email"]), age,1 if form["gender"] == "Male" else 0,))
                                        conn.commit()
                                        conn.close()
                                        return redirect("/login")

                                    else:
                                        msg[0] = "USERNAME already in USE !" 

                                else:
                                    msg[0] = "MMM..... GENDER????"
                        
                            else:
                                msg[0] = "TOO YOUNG OR TOO OLD BRUH !"
                        else:
                            msg[0] = "PASSWORDS DON'T MATCH !"

                    else:
                        msg[0] = "EMAIL INVALID !"
                
                else:
                    msg[0] = "USERNAME INVALID !"

        return render_template("register.html",msg=msg)


@app.route("/faq")
def faq():
    if(token_decode()[0]):
            conn = db_connection("faq")
            faqs = conn.execute("SELECT * FROM faq").fetchall()
            conn.close()
    
            return render_template("faq.html",faqs=faqs) 
    else:
        return redirect("/login")
    

@app.route("/logout")
def logout():
    if(token_decode()[0]):
        pop_session([])

    return redirect("/login")