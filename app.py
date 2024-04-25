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
    "user" : username,
    "userid" : userid,
    "exp" : datetime.utcnow() + timedelta(seconds=15)
    },
    ENV["JWT_KEY"],algorithm='HS256')

    return token


def token_decode():
    def pop_token():
        try:
            for s in session:
                 session.pop(s)
        except:
            pass

    if(session.get("jwt")):   
        try:
            data = jwt.decode(session.get("jwt"),ENV["JWT_KEY"] ,algorithms=['HS256',])
            return [True,data]
        
        #jwt.exceptions.DecodeError
        #jwt.exceptions.ExpiredSignatureError
        except:
            pop_token()
    
    else:
         pop_token()


    return [False]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.errorhandler(404)
def notFound(e):
     return redirect("/")

@app.route("/")
def index():
    if(token_decode()[0]):
            return render_template("index.html",username=token_decode()[1]["user"]) 
    else:
        return redirect("/login")



@app.route("/shop",methods=['POST', 'GET'])
def shop():
    if request.method == "POST":
        f = list(request.form)[1]

        try:
            session[f] += 1

        except KeyError:
             session[f] = 1

        return redirect("/cart")

    else:
        if(token_decode()[0]):
            conn = db_connection("products")
            pr = conn.execute("SELECT * FROM products").fetchall()
            conn.close()

            return render_template("shop.html",products=pr,market=[get_price("BTC"),get_price("ETH")],give_rating=give_rating,round=round)
        else:
            return redirect("/login")


@app.route("/cart")
def cart():
    if(token_decode()[0]):
            conn = db_connection("products")

            cart = []

            subtotal = [0,0]

            atLeast = False

            for f in session:
                if f not in toExcept:     
                    atLeast = True 
                    for val in conn.execute("SELECT * FROM products WHERE id=?",(f,)).fetchall():
                        val = dict(val)

                        #prices
                        val["quantity"] = session[f]

                        val["btc"] = round(val["price"]/get_price("BTC"),4)
                        val["eth"] = round(val["price"]/get_price("ETH"),4)


                        subtotal[0]+= val["btc"] * val["quantity"]
                        subtotal[1]+= val["eth"] * val["quantity"]

                        for x in range(len(subtotal)):
                             subtotal[x] = round(subtotal[x],4)
                             
                        cart.append(val)

            conn.close()
            
            if(atLeast):
                return render_template("cart.html",cart=cart,subtotal=subtotal)
            
            else:
                 return redirect("/shop")

    else:
        return redirect("/login")



@app.route("/login",methods=["GET", "POST"])
def login():
        
    if(token_decode()[0]):

        return redirect("/")
    
    else:
        msg = []
        if request.method == "POST":
            msg = []
            form = request.form

            if(form["username"] and form["password"]):
                username = bleach.clean(form["username"])
                password = hash_password(form["password"])

                userid = 1

                conn = db_connection("users")
                dataUser = conn.execute("SELECT * FROM users WHERE username=?",(username,)).fetchall()

                if len(dataUser) == 1:
                    dataUser = dict(dataUser[0])

                    if(dataUser["password"] == password):
                        msg.append(False)
                        session["jwt"] = token_gen(dataUser['id'],username)

                        return redirect("/")

                    else:
                        msg.append(True)
                        msg.append("USERNAME or PASSWORD are NOT CORRECT !")


        return render_template("login.html",msg=msg)

@app.route("/register")
def register():
    if(token_decode()[0]):
        return redirect("/")
    
    else:
        return render_template("register.html")


@app.route("/faq")
def faq():
    if(token_decode()[0]):
            return render_template("faq.html") 
    else:
        return redirect("/login")