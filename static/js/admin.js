function init_data(){
    formData = new FormData();
    formData.set("csrf_token",document.getElementById("csrf_token").value)

    return formData
}


function get_section(element){
    let j = document.getElementById(element);
    for(let i=0;i<8;i++){
        j=j.parentElement
    }
    return j.id;
}


function input_system(el){
    if(el.type == "checkbox"){
       return [el.id,el.checked ? "1" : "0"]
    }

    else if(el.type == "file"){
        if(el.files.length == 1){
            return [el.id,document.getElementById(el.id).files[0]]
        }

        return null
    }
    else{
        return [el.id,el.value]
    }
}



let isEdit = false;
let isAdd = false;

function disable_buttons(id){
    let buttons = new Array(document.getElementsByClassName("btn btn-warning"), document.getElementsByClassName("btn btn-danger"))
    for(let i=0;i<buttons.length;i++){
        for(let j=0;j<buttons[i].length;j++){
            if(buttons[i][j].id != id){
                let element = document.getElementById(buttons[i][j].id)
                if(isEdit){
                    element.setAttribute("disabled","")
                }
                else{
                    element.removeAttribute("disabled")
                }
            }
        }
    }

    let saveButton = document.getElementById(id.replace("-e","-s"))
    if(isEdit){
        saveButton.removeAttribute("disabled")
    }
    else{
        saveButton.setAttribute("disabled","")
    }

    let editButton = document.getElementById(id)
    editButton.className = isEdit ? "btn btn-primary" : "btn btn-warning"
    editButton.innerText = isEdit ? "CANCEL" : "EDIT"
}

function edit(id){
    isEdit = !isEdit

    /*UNAME same for:
        [+] EDIT BUTTON (uname-id-e)
        [+] SAVE BUTTON (uname-id-s)
        [+] INPUT FOR EDIT (td name= uname > input id="paid")
        [+] DATABASE ELEMENT EDIT (uname-h)
    */
    let uname = id.split("-")[0];

    //same length
    let toHide = document.getElementsByName(`${uname}-h`)
    let toShow = document.getElementsByName(uname)

    for(let i=0;i<toHide.length;i++){
        toHide[i].style.display = isEdit ? "none" : "table-cell";
    }

    for(let i=0;i<toShow.length;i++){
        toShow[i].style.display = isEdit ? "table-cell" : "none";
    }


    disable_buttons(id)
}



function save(id){
    const formData = init_data()

    let uname = id.split("-")[0];

    let values = document.getElementsByName(uname)

    formData.set("path", get_section(id))
    formData.set("id", id.split("-")[1])

    for(let i=0; i<values.length; i++){
        let el = values[i].children[0]

        let resp = input_system(el)

        if(resp != null){
            formData.set(resp[0],resp[1])
        }
    }

    const xhr = new XMLHttpRequest();
    xhr.open('PUT', '/admin', true);

    xhr.onload = function () {
        if (xhr.status === 200) {
            document.body.innerHTML = xhr.responseText;

            let accordion = document.getElementById(formData.get("path"))
            accordion.children[0].children[0].className = "accordion-button"
            accordion.children[1].className = "accordion-collapse collapse show"

            isEdit = false
        }
    };
    xhr.send(formData);
}


function add(id){
    const formData = init_data()

    isAdd = !isAdd

    if(isAdd){
        document.getElementById(id).innerText = "ADD RECORD"

        document.getElementById(id.replace("add","cancelAdd")).style = ""
        document.getElementById(id.replace("add","addFields")).style = ""
    }

    else{
        if(id.includes("cancelAdd")){
            document.getElementById(id.replace("cancelAdd","add")).innerText = "+"
            document.getElementById(id).style = "display: none !important"
            document.getElementById(id.replace("cancelAdd","addFields")).style = "display: none !important"
        }

        else{
            formData.set("path",document.getElementById(id).parentElement.parentElement.id)

            let el = document.getElementById(id.replace("add","addFields")).children

            for(let i=0;i<el.length;i++){
                let resp = input_system(el[i])
                formData.set(resp[0],resp[1])
            }

            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/admin', true);

            xhr.onload = function () {
                if (xhr.status === 200) {
                    document.body.innerHTML = xhr.responseText;

                    let accordion = document.getElementById(formData.get("path"))
                    accordion.children[0].children[0].className = "accordion-button"
                    accordion.children[1].className = "accordion-collapse collapse show"
                }
            };
            xhr.send(formData);
        }
    }
}


function del(id){
    const formData = init_data()

    del_button = document.getElementById("confirm_delete")
    new bootstrap.Modal("#delModal").show();


    del_button.addEventListener("click", function(){

        formData.set("path",get_section(id))
        formData.set("id",id.split("-")[1])

        const xhr = new XMLHttpRequest();
        xhr.open('DELETE', '/admin', true);

        xhr.onload = function () {
            if (xhr.status === 200) {
                document.body.innerHTML = xhr.responseText;

                let accordion = document.getElementById(formData.get("path"))
                accordion.children[0].children[0].className = "accordion-button"
                accordion.children[1].className = "accordion-collapse collapse show"

                document.getElementsByClassName("modal-open")[0].style=""
            }
        };
        xhr.send(formData);
    })
}