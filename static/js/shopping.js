const template = Handlebars.compile(document.querySelector('#list_template').innerHTML);
document.getElementById('deletebtn').disabled = true;

function checklistinput() {
    'use strict';
    document.getElementById('listaddbtn').disabled = true;
    let inputvalue = document.getElementById('listinput').value;
    if (inputvalue.length < 1) {
        document.getElementById('listinput').classList.remove('is-valid');
        document.getElementById('listinput').classList.add('is-invalid');
        document.getElementById('listaddbtn').disabled = true;
    } else {
        document.getElementById('listinput').classList.add('is-valid');
        document.getElementById('listinput').classList.remove('is-invalid');
        document.getElementById('listaddbtn').disabled = false;
    }
}

function updatelist(data) {
    let none = document.getElementById('none');
    if (none != null)
        none.style.display = 'none';
    const content = template({
    'id': data.id,
    'name': data.name,
    });
    document.querySelector('#list').innerHTML += content;
}

function addToList() {
    let a = document.getElementById('listinput').value;
    $.ajax({
        type: "POST",
        url: '/add-list',
        data: {
            'name': a
        },
        headers: {
            'X-CSRFToken':  document.getElementById('addToListform').firstElementChild.value
        },
    })
    .done(function (data) {
        document.getElementById('adderror').style.display = "none";
        document.getElementById('addsuccess').style.display = "block";
        setTimeout(() => {
        document.getElementById('addsuccess').style.display = "none";  
        }, 5000);
        updatelist(data);
        return;
    })
    .fail(function (data) {
        document.getElementById('adderror').innerHTML = data.responseJSON.message;
        document.getElementById('adderror').style.display = "block";
        setTimeout(() => {
           document.getElementById('adderror').style.display = "none";  
        }, 5000);
        return;
    })
}

function check() {
    document.getElementById('deletebtn').disabled = true;
    let b = document.getElementsByName('listitem[]');
    for (var i=0; i<b.length; i++) {
        if (b[i].checked == true)
            document.getElementById('deletebtn').disabled = false;
    }

}

function deletechecked(data) {
    document.getElementById('deletebtn').disabled = true;
    var len = data.ids.length
    for(var i=0; i<len; i++) {
        document.querySelector('#listitem'+data.ids[i]).remove();
    }
    let items  = document.getElementsByName('listitem[]');
    if (items.length == 0){
        let none = document.getElementById('none');
        if (none != null)
            none.style.display = 'block';
    }

}


function deleteList() {
    let d =[];
    let c =  document.getElementsByName('listitem[]');
    if (c.length > 1) {
        for (var i=0; i<c.length; i++) {
            if (c[i].checked == true)
                d.push(c[i].value);
        } 
    }
    else {
        d.push(c[0].value);
    }
    

    $.ajax({
        type: "POST",
        url: '/delete-list',
        data: {
            'names': d
        },
        headers: {
            'X-CSRFToken':  document.getElementById('deleteListform').firstElementChild.value
        },
    })
    .done(function (data) {
        document.getElementById('deleteerror').style.display = "none";
        document.getElementById('deletesuccess').style.display = "block";
        setTimeout(() => {
        document.getElementById('deletesuccess').style.display = "none";  
        }, 5000);
        deletechecked(data);
        return;
    })
    .fail(function (data) {
        document.getElementById('deleteerror').innerHTML = data.responseJSON.message;
        document.getElementById('deleteerror').style.display = "block";
        setTimeout(() => {
           document.getElementById('deleteerror').style.display = "none";  
        }, 5000);
        return;
    })
}