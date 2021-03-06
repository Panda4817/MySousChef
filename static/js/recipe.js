// Function to add recipe to liked list using ajax call
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

// Function used to dynamically generate form from formset
function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    var replacement = prefix + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}

// Function used to dynamically generate form from formset
function cloneMore(selector, prefix, name) {
    var newElement = $(selector).clone(true);
    var total = $('#id_' + prefix + '-TOTAL_FORMS').val();
    newElement.find(':input:not([type=button]):not([type=submit]):not([type=reset])').each(function() {
        var name = $(this).attr('name').replace('-' + (total-1) + '-', '-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    newElement.find('label').each(function() {
        var forValue = $(this).attr('for');
        if (forValue) {
          forValue = forValue.replace('-' + (total-1) + '-', '-' + total + '-');
          $(this).attr({'for': forValue});
        }
    });
    total++;
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
    var conditionRow = $('.'+name+'-row:not(:last)');
    conditionRow.find('.btn.add-'+name+'-row')
    .removeClass('btn-success').addClass('btn-danger')
    .removeClass('add-'+name+'-row').addClass('remove-'+name+'-row')
    .html('-');
    return false;
}

// Function used to dynamically generate form from formset
function deleteForm(prefix, btn, name) {
    var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    if (total > 1){
        btn.closest('.'+name+'-row').remove();
        var forms = $('.'+name+'-row');
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        for (var i=0, formCount=forms.length; i<formCount; i++) {
            $(forms.get(i)).find(':input').each(function() {
                updateElementIndex(this, prefix, i);
            });
        }
    }
    return false;
}

// Check text input fields are filled in correctly
function checktext(data) {
    'use strict';
    let inputvalue = document.getElementById(data).value;
    if (inputvalue.length < 1) {
        document.getElementById(data).classList.remove('is-valid');
        document.getElementById(data).classList.add('is-invalid');
    } else {
        document.getElementById(data).classList.add('is-valid');
        document.getElementById(data).classList.remove('is-invalid');
    }
}

// Check number input fields are filled in correctly
function checknumber(data) {
    'use strict';
    let inputvalue = document.getElementById(data).value;
    if (inputvalue < 1) {
        document.getElementById(data).classList.remove('is-valid');
        document.getElementById(data).classList.add('is-invalid');
    } else {
        document.getElementById(data).classList.add('is-valid');
        document.getElementById(data).classList.remove('is-invalid');
    }
}

// When close cliked when extra info on ingredients is open on recipe page
function closeinfo(data) {
    let div = document.getElementById('extra'+data);
    div.style.display = "none";
}

// Ajax call to display extra info about ingredients on recipe page
function extrainfo(data) {
    let name = document.getElementById('name'+data).innerText;
    let amount = document.getElementById('amount'+data).innerText;
    let unit = document.getElementById('unit'+data);
    if (unit == null)
        unit = "None";
    else 
        unit = document.getElementById('unit'+data).innerText;
    $.ajax({
        type: "POST",
        url: '/extra-ingredient-info',
        data: {
            'name': name,
            'amount': amount,
            'unit': unit,
            'id': data
        },
        headers: {
            'X-CSRFToken':  document.getElementById('addtolikedform').firstElementChild.value
        },
    })
    .done(function (data) {
        console.log(data);
        const template = Handlebars.compile(document.querySelector('#extra_template').innerHTML);
        const content = template({
            'subs': data.subs,
            'imperial': data.imperial,
            'id': data.id
        });
        console.log(content);
        document.querySelector('#extra'+data.id).innerHTML = content;
        document.querySelector('#extra'+data.id).style.display = "block";
    });
}

// Ajax call delete liked recipes
function deleteliked(data) {
    $.ajax({
        type: "POST",
        url: '/delete-liked',
        data: {
            'id': data
        },
        headers: {
            'X-CSRFToken':  document.getElementById('addmyrecipeform').firstElementChild.value
        },
    })
    .done(function (data) {
        document.querySelector('#liked'+data.id).remove();
    });
}


// When dom loads fully, click events are put in place for dynamically generated forms
document.addEventListener('DOMContentLoaded', () => {
    $(document).on('click', '.add-ingform-row', function(e){
        e.preventDefault();
        cloneMore('.ingform-row:last', 'ingform', 'ingform');
        return false;
    });
    $(document).on('click', '.remove-ingform-row', function(e){
        e.preventDefault();
        deleteForm('ingform', $(this), 'ingform');
        return false;
    });
    $(document).on('click', '.add-instrform-row', function(e){
        e.preventDefault();
        cloneMore('.instrform-row:last', 'instrform', 'instrform');
        return false;
    });
    $(document).on('click', '.remove-instrform-row', function(e){
        e.preventDefault();
        deleteForm('instrform', $(this), 'instrform');
        return false;
    });

});

