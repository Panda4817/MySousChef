function addtoliked(data) {
    $.ajax({
        type: "POST",
        url: '/recipe/'+data,
        data: {
            'api_id': data
        },
        headers: {
            'X-CSRFToken':  document.getElementById('addtolikedform').firstElementChild.value
        },
    })
    .done(function (data) {
        console.log(data.message);
        document.getElementById('addsuccess').style.display = "block";
        setTimeout(() => {
        document.getElementById('addsuccess').style.display = "none";  
        }, 5000);
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