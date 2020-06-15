const template = Handlebars.compile(document.querySelector('#result_template').innerHTML);

function updateresults(data) {
    let x = document.querySelector('#results').querySelectorAll('div');
    for (var i=0; i<x.length; i++){
        x[i].remove();
    }
    for (var i=0; i<data.recipes.length; i++) {
        if (data.recipes[i]['credit'] == null) {
            data.recipes[i]['credit'] = "Source";
        }
    }
    for (var i=0; i<data.recipes.length; i++) {
        const content = template({
        'id': data.recipes[i]['id'],
        'image': data.recipes[i]['image'],
        'title': data.recipes[i]['title'],
        'serves': data.recipes[i]['serves'],
        'time': data.recipes[i]['time'],
        'health': data.recipes[i]['health'],
        'url': data.recipes[i]['url'],
        'credit': data.recipes[i]['credit'],
        'likes': data.recipes[i]['likes']
        });
        document.querySelector('#results').innerHTML += content;
    }   
}

function checkInput() {
    'use strict';
    document.getElementById('advancedbtn').disabled = true;
    let inputvalue = document.getElementById('queryInput').value;
    if (inputvalue.length < 1) {
        document.getElementById('queryInput').classList.remove('is-valid');
        document.getElementById('queryInput').classList.add('is-invalid');
        document.getElementById('advancedbtn').disabled = true;
    } else {
        document.getElementById('queryInput').classList.add('is-valid');
        document.getElementById('queryInput').classList.remove('is-invalid');
        document.getElementById('advancedbtn').disabled = false;
    }
}

function simplesearch() {
    $.ajax({
        type: "POST",
        url: '/search-simple',
        headers: {
            'X-CSRFToken':  document.getElementById('onlyingredientsform').firstElementChild.value
        },
    })
    .done(function (data) {
        if (data.message) {
            document.getElementById('searcherror').innerHTML = data.message;
            document.getElementById('searcherror').style.display = "block";
            setTimeout(() => {
            document.getElementById('searcherror').style.display = "none";  
            }, 5000);
        }
        updateresults(data);
        y = document.getElementById('results').getBoundingClientRect().top + window.pageYOffset - 100;
        window.scrollTo({ top: y, behavior: 'smooth' });
        return;
    })
    .fail(function (data) {
        document.getElementById('searcherror').innerHTML = data.responseJSON.message;
        document.getElementById('searcherror').style.display = "block";
        setTimeout(() => {
           document.getElementById('searcherror').style.display = "none";  
        }, 5000);
        return;
    })
}

function advancedsearch() {
    query = document.getElementById('queryInput').value;
    let a = document.querySelector('select[name="intolerance"]').selectedOptions;
    let b = [];
    for(var i=0; i<a.length; i++) {
        b.push(a[i].value);
    }
    let c = document.querySelector('select[name="cuisine"]').selectedOptions;
    let d = [];
    for(var i=0; i<c.length; i++) {
        d.push(c[i].value);
    }
    let e = document.querySelector('select[name="diet"]').value;
    let f = document.querySelector('select[name="meal_type"]').value;
    let g = document.querySelectorAll('input[name="sortOptions"]');
    let j='';
    for(var i=0; i<g.length; i++) {
        if (g[i].checked == true)
            j = g[i].value;
    }
    let h = document.querySelectorAll('input[name="ingredients"]');
    let k='';
    for(var i=0; i<h.length; i++) {
        if (h[i].checked == true)
            k = h[i].value;
    }
    $.ajax({
        type: "POST",
        url: '/search-advanced',
        data: {
            'query': query,
            'intolerance': b,
            'cuisine': d,
            'diet': e,
            'meal_type': f,
            'sort': j,
            'ingredients': k

        },
        headers: {
            'X-CSRFToken':  document.getElementById('advancedform').firstElementChild.value
        },
    })
    .done(function (data) {
        if (data.message) {
            document.getElementById('advancederror').innerHTML = data.message;
            document.getElementById('advancederror').style.display = "block";
            setTimeout(() => {
            document.getElementById('advancederror').style.display = "none";  
            }, 5000);
        }
        updateresults(data);
        $('#collapse').collapse('hide')
        y = document.getElementById('results').getBoundingClientRect().top + window.pageYOffset - 50;
        window.scrollTo({ top: y, behavior: 'smooth' });
        return;
    })
    .fail(function (data) {
        document.getElementById('advancederror').innerHTML = data.responseJSON.message;
        document.getElementById('advancederror').style.display = "block";
        setTimeout(() => {
           document.getElementById('advancederror').style.display = "none";  
        }, 5000);
        return;
    })
}