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

function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    var replacement = prefix + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}

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