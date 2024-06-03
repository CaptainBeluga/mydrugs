if(window.location.href.split("/")[window.location.href.split("/").length-1] == "login"){
    prompt("! WARNING: THIS IS A FAKE WEBSITE, CREATED ONLY FOR EDUCATIONAL PURPOSES !")
}

function item_managment(id){
    document.getElementById(`${id.substr(0, id.length-1)}-color`).className = `spinner-border text-${id.substr(id.length-1,id.length) == "+" ? "success" : "danger"}`
    document.getElementById(`${id.substr(0, id.length-1)}-spinner`).style.display = "block"

    $.ajax({
        url: "/cart",
        type: "post",
        data: {
            "csrf_token" : $("#csrf_token").val(),
            id : id
        },
        success: function(response){
            document.body.innerHTML = response;
        }
    })
}

function shop_to_cart(id){
    let spinner = document.getElementById(`${id}-spinner`)

    spinner.style.display = "block"

    $.ajax({
        url: "/shop",
        type: "post",
        data: {
            "csrf_token" : $("#csrf_token").val(),
            id : id
        },
        success: function(){
            new bootstrap.Modal("#addCartModal").show();

            spinner.style.display = "none"
        }
    })
}

function basic(arr,endpoint){
    data = {}
    for(let i=0;i<arr.length;i++){
        data[arr[i]] = $(`#${arr[i]}`).val();
    }

    $.ajax({
        url: `/${endpoint}`,
        type: "post",
        data: data,
        success: function(response){
            if(response != "200"){
                document.body.innerHTML = response;
                
                for(let i=0;i<arr.length;i++){
                    if(arr[i] != "csrf_token"){
                    document.getElementById(arr[i]).value = data[arr[i]];
                    }
                }
            }

            else{
                window.location = "/"
            }
        }
    })
}

function login(){
    basic(["csrf_token", "username", "password"],"login")
}

function register(){
    basic(["csrf_token", "username","email", "password", "confirm_password", "age", "gender"],"register")
}
