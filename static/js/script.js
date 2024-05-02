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
            const addCartModal = new bootstrap.Modal("#addCartModal");
            addCartModal.show();

            spinner.style.display = "none"
        }
    })
}

function login(){
    let username = $("#username").val()
    let password = $("#password").val()

    $.ajax({
        url: "/login",
        type: "post",
        data: {
            "csrf_token" : $("#csrf_token").val(),
            "username" : username,
            "password" : password
        },
        success: function(response){
            document.body.innerHTML = response;

            document.getElementById("username").value = username;
            document.getElementById("password").value = password;
        }
    })
}