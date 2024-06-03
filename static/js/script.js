if(window.location.href.split("/")[window.location.href.split("/").length-1] == "login"){
    prompt("! WARNING: THIS IS A FAKE WEBSITE, CREATED ONLY FOR EDUCATIONAL PURPOSES !")
}

function item_managment(id){
    document.getElementById(`${id.substr(0, id.length-1)}-color`).className = `spinner-border text-${id.substr(id.length-1,id.length) == "+" ? "success" : "danger"}`
    document.getElementById(`${id.substr(0, id.length-1)}-spinner`).style.display = "block"

    const formData = new FormData();
    formData.set("csrf_token", document.getElementById("csrf_token").value);
    formData.set("id", id)

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/cart', true);

    xhr.onload = function () {
        if (xhr.status === 200) {
            document.body.innerHTML = xhr.responseText;
        }
    };
    xhr.send(formData);
}

function shop_to_cart(id){
    let spinner = document.getElementById(`${id}-spinner`)

    spinner.style.display = "block"

    const formData = new FormData();
    formData.set("csrf_token", document.getElementById("csrf_token").value);
    formData.set("id", id)
    
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/shop', true);

    xhr.onload = function () {
        if (xhr.status === 200) {
            document.body.innerHTML = xhr.responseText;
        }
    };
    xhr.send(formData);
}

function basic(arr,endpoint){
    const formData = new FormData();
    
    for(let i=0;i<arr.length;i++){
        formData.set(arr[i], document.getElementById(arr[i]).value)
    }
    
    const xhr = new XMLHttpRequest();
    xhr.open('POST', `/${endpoint}`, true);

    xhr.onload = function () {
        if (xhr.status != 200) {
            document.body.innerHTML = xhr.responseText;
                
            for(let i=0;i<arr.length;i++){
                if(arr[i] != "csrf_token"){
                document.getElementById(arr[i]).value = data[arr[i]];
                }
            }
        }

        else{
            window.location = "/"
        }
    };
    xhr.send(formData);
}

function login(){
    basic(["csrf_token", "username", "password"],"login")
}

function register(){
    basic(["csrf_token", "username","email", "password", "confirm_password", "age", "gender"],"register")
}
