function convertLocalDate() {
    var dates = document.getElementsByClassName('date');
    var i;
    var len = dates.length;
    for (i = 0; i < len; i++) {
        var timestamp = dates[i].textContent;
        if (timestamp != 'No use-by or best-before date provided' 
            && timestamp != 'Not opened/ Not something that can be opened' 
            && timestamp != 'Not frozen/ Cannot be frozen'
            && timestamp != 'Today'
            && timestamp != 'Yesterday') {
            var local = new Date(timestamp);
            var now = new Date();
            if (local.toDateString() == now.toDateString())
                var date = 'Today';
            else if (local.getDate() == (now.getDate() - 1))
                var date = 'Yesterday';
            else
                var date = local.toDateString();
            dates[i].innerText = date; 
        }
            
        
    } 
}

// General function convert timestamps into local time and date
function convertLocalTime() {
    var time = document.getElementsByClassName('time');
    var i;
    var len = time.length;
    for (i = 0; i < len; i++) {
        var timestamp = time[i].textContent;
        var local = new Date(timestamp);
        var now = new Date();
        if (local.toDateString() == now.toDateString())
            var date = 'Today';
        else if (local.getDate() == (now.getDate() - 1))
            var date = 'Yesterday';
        else
            var date = local.toDateString();
        time[i].innerText = date + ' ' + local.toLocaleTimeString();
    };
}

document.addEventListener('DOMContentLoaded', () => {
    let searchInput = document.querySelector('#searchinput');
    let addBtn = document.querySelector('#pantryadd');
    addBtn.disabled = true;
    let timeout = null;
    searchInput.addEventListener('input', () => {
        addBtn.disabled = true;
        clearTimeout(timeout);
            if (searchInput.value.length >= 3) {
            timeout = setTimeout(() => {   
                $.ajax({
                    type: "POST",
                    url: "/search_ingredients",
                    data: {
                        search_input: $('#searchinput').val(),
                        intolerance: $('#intolerance').val(),
                    },
                    headers: {
                        'X-CSRFToken': document.getElementById('addpantryform').firstElementChild.value
                    },
                })
                .done(function(data) {
                    $('#searchinput').autocomplete({source: data.json_list});
                    document.querySelector('.ui-menu').addEventListener('click', () => {
                        addBtn.disabled = false;
                        searchInput.classList.remove('is-invalid');
                        searchInput.classList.add('is-valid');
                        document.getElementById('searcherror').style.display = "none";
                    })
                    if (data.input_correct == true) {
                        addBtn.disabled = false;
                        searchInput.classList.remove('is-invalid');
                        searchInput.classList.add('is-valid');
                        document.getElementById('searcherror').style.display = "none";
                    }
                    else {
                        addBtn.disabled = true;
                        searchInput.classList.remove('is-valid');
                        searchInput.classList.add('is-invalid');
                    } 
                })
                .fail(function(data) {
                    addBtn.disabled = true;
                    searchInput.classList.remove('is-valid');
                    searchInput.classList.add('is-invalid');
                    document.getElementById('searcherror').style.display = "block";
                    console.log(data.message);
                })
            }, 500);
        }
        
    });

    
    convertLocalTime();

    let dateInputs = document.getElementsByClassName('inputdate');
    for(var i=0; i<dateInputs.length; i++) {
        dateInputs[i].min = new Date().toISOString().split("T")[0];
    }
    
    
    convertLocalDate();
    
   

});

function checkqty(data) {
    'use strict';
    let inputvalue = document.getElementById('inputqty'+data).value;
    if (inputvalue < 1) {
        document.getElementById('inputqty'+data).classList.remove('is-valid');
        document.getElementById('inputqty'+data).classList.add('is-invalid');
        document.getElementById('qtyerror'+data).style.display = "block";
    } else {
        document.getElementById('inputqty'+data).classList.add('is-valid');
        document.getElementById('inputqty'+data).classList.remove('is-invalid');
        document.getElementById('qtyerror'+data).style.display = "none";
    }
}
function checkuw(data) {
    'use strict';
    let inputvalue = document.getElementById('inputuw'+data).value;
    if (inputvalue.length < 1) {
        document.getElementById('inputuw'+data).classList.remove('is-valid');
        document.getElementById('inputuw'+data).classList.add('is-invalid');
    } else {
        document.getElementById('inputuw'+data).classList.add('is-valid');
        document.getElementById('inputuw'+data).classList.remove('is-invalid');
    }
}

function checkdate(data, name) {
    'use strict';
    let inputvalue = document.getElementById('input'+name+data).value;
    if (inputvalue < new Date().toISOString().split("T")[0]) {
        document.getElementById('input'+name+data).classList.remove('is-valid');
        document.getElementById('input'+name+data).classList.add('is-invalid');
        document.getElementById(name+'error'+data).style.display = "block";
    } else {
        document.getElementById('input'+name+data).classList.add('is-valid');
        document.getElementById('input'+name+data).classList.remove('is-invalid');
        document.getElementById(name+'error'+data).style.display = "none";
    }
}


function changeqty(data) {
    let newqty = document.getElementById('inputqty'+data).value;
    $.ajax({
        type: "POST",
        url: '/change-qty-pantry',
        data: {
            'usertopantry_id': data,
            'new_qty': newqty,
        },
        headers: {
            'X-CSRFToken':  document.getElementById('qtyform'+data).firstElementChild.value
        },
    })
    .done(function (data) {
        document.getElementById('qty'+data.id).innerHTML = data.new_qty;
        document.getElementById('inputqty'+data.id).classList.add('is-valid');
        document.getElementById('inputqty'+data.id).classList.remove('is-invalid');
        document.getElementById('qtyerror'+data.id).style.display = "none";
    })
    .fail(function (data) {
        document.getElementById('inputqty'+data.id).classList.remove('is-valid');
        document.getElementById('inputqty'+data.id).classList.add('is-invalid');
        document.getElementById('qtyerror'+data.id).style.display = "block";
    })
}

function diffDate(startDate, endDate) {
    var b = moment(startDate),
      a = moment(endDate),
      intervals = ['years', 'months', 'weeks', 'days'],
      out = {};
  
    for (var i = 0; i < intervals.length; i++) {
      var diff = a.diff(b, intervals[i]);
      b.add(diff, intervals[i]);
      out[intervals[i]] = diff;
    }
    console.log(out);
    return out;
  }
  
  function display(obj) {
    var str = '';
    for (key in obj) {
        if (obj[key] != 0)
            str = str + obj[key] + ' ' + key + ' ';
    }
    if (str == '')
        str = '0 days'
    console.log(str);
    return str;
  }



function addMonthDay(data) {
    let today = new Date();
    let usedate = document.getElementById('useref'+data);
    if (usedate != null) {
        let localusedate = new Date(usedate.value);
        let out1  = diffDate(today, localusedate);
        let countdownstr1 = display(out1);
        document.getElementById('usecountdown'+data).innerHTML = countdownstr1;
    }
    let opendate = document.getElementById('openref'+data);
    if (opendate != null) {
        let localopendate = new Date(opendate.value);
        let out2  = diffDate(today, localopendate);
        let countdownstr2 = display(out2);
        document.getElementById('opencountdown'+data).innerHTML = countdownstr2;
    }
    let frozendate = document.getElementById('frozenref'+data);
    if (frozendate != null) {
        let localfrozendate = new Date(frozendate.value);
        let out3  = diffDate(today, localfrozendate);
        let countdownstr3 = display(out3);
        document.getElementById('frozencountdown'+data).innerHTML = countdownstr3;
    }
    
}

function addtopsection(data, name) {
    let sectionrow = document.getElementById(name+'section'+data.id);
    if (sectionrow != null) {
        document.getElementById(name+'ref'+data.id).value = data.date;
        addMonthDay(data.id);
        if (data.datetext)
            document.getElementById('usetxt'+data.id).innerHTML = data.datetext;
    } else {
        let row = document.createElement('div');
        row.id = name+'section'+data.id;
        row.className = "row";
        let col = document.createElement('div');
        col.className = "col-lg";
        let h6 = document.createElement('h6');
        let spancountdown = document.createElement('span');
        spancountdown.id = name+'countdown'+data.id;
        spancountdown.className="countdown";
        let input = document.createElement('input');
        input.id = name+'ref'+data.id;
        input.value = data.date;
        input.style.display = "none";
        h6.appendChild(spancountdown);
        if (name == 'use'){
            let spantext = document.createElement('span');
            spantext.id = name+'txt'+data.id;
            spantext.innerHTML = ' until '+data.datetext+' date';
            h6.appendChild(spantext);
        }
        if (name == 'open')
            h6.append(' since opening item');
        if (name == 'frozen')
            h6.append(' since freezing item');
        h6.appendChild(input);
        col.appendChild(h6);
        row.appendChild(col);
        document.getElementById('topsection'+data.id).appendChild(row);
    }
}

function changeuseby(data) {
    let usetext = $("input[name='radiotext"+data+"']:checked").val();
    let usedate = document.getElementById('inputuse'+data).value;
    let t = "00:00:00.000Z"
    var utc = usedate + 'T' + t

    $.ajax({
        type: "POST",
        url: '/change-useby-pantry',
        data: {
            'usertopantry_id': data,
            'new_date': utc,
            'datetext': usetext,
        },
        headers: {
            'X-CSRFToken':  document.getElementById('useform'+data).firstElementChild.value
        },
    })
    .done(function (data) {
        document.getElementById('usetext'+data.id).innerHTML = data.datetext;
        document.getElementById('usedate'+data.id).innerHTML = data.date;
        convertLocalDate();
        let name = 'use';
        addtopsection(data, name);
        addMonthDay(data.id);
        document.getElementById('inputuse'+data.id).classList.add('is-valid');
        document.getElementById('inputuse'+data.id).classList.remove('is-invalid');
        document.getElementById('useerror'+data.id).style.display = "none";
    })
    .fail(function (data) {
        document.getElementById('inputuse'+data.id).classList.remove('is-valid');
        document.getElementById('inputuse'+data.id).classList.add('is-invalid');
        document.getElementById('useerror'+data.id).style.display = "block";
    })
}

function changeopen(data) {
    let usedate = document.getElementById('inputopen'+data).value;
    let t = "00:00:00.000Z"
    var utc = usedate + 'T' + t

    $.ajax({
        type: "POST",
        url: '/change-open-pantry',
        data: {
            'usertopantry_id': data,
            'new_date': utc,
        },
        headers: {
            'X-CSRFToken':  document.getElementById('openform'+data).firstElementChild.value
        },
    }).done(function (data) {
        document.getElementById('opendate'+data.id).innerHTML = data.date;
        convertLocalDate();
        let name = 'open';
        addtopsection(data, name);
        addMonthDay(data.id);
        document.getElementById('inputopen'+data.id).classList.add('is-valid');
        document.getElementById('inputopen'+data.id).classList.remove('is-invalid');
        document.getElementById('openerror'+data.id).style.display = "none";
    })
    .fail(function (data) {
        document.getElementById('inputopen'+data.id).classList.remove('is-valid');
        document.getElementById('inputopen'+data.id).classList.add('is-invalid');
        document.getElementById('openerror'+data.id).style.display = "block";
    })
}

function changefrozen(data) {
    let usedate = document.getElementById('inputfrozen'+data).value;
    let t = "00:00:00.000Z"
    var utc = usedate + 'T' + t

    $.ajax({
        type: "POST",
        url: '/change-frozen-pantry',
        data: {
            'usertopantry_id': data,
            'new_date': utc,
        },
        headers: {
            'X-CSRFToken':  document.getElementById('frozenform'+data).firstElementChild.value
        },
    }).done(function (data) {
        document.getElementById('frozendate'+data.id).innerHTML = data.date;
        convertLocalDate();
        let name = 'frozen';
        addtopsection(data, name);
        addMonthDay(data.id);
        document.getElementById('inputfrozen'+data.id).classList.add('is-valid');
        document.getElementById('inputfrozen'+data.id).classList.remove('is-invalid');
        document.getElementById('frozenerror'+data.id).style.display = "none";
    })
    .fail(function (data) {
        document.getElementById('inputfrozen'+data.id).classList.remove('is-valid');
        document.getElementById('inputfrozen'+data.id).classList.add('is-invalid');
        document.getElementById('frozenerror'+data.id).style.display = "block";
    })
}

function changeuw(data) {
    let uw = document.getElementById('inputuw'+data).value;

    $.ajax({
        type: "POST",
        url: '/change-uw-pantry',
        data: {
            'usertopantry_id': data,
            'uw': uw,
        },
        headers: {
            'X-CSRFToken':  document.getElementById('uwform'+data).firstElementChild.value
        },
    }).done(function (data) {
        document.getElementById('uw'+data.id).innerHTML = data.uw;
    });
}

function deleteitem(data) {
    $.ajax({
        type: "POST",
        url: '/delete-pantry-item',
        data: {
            'usertopantry_id': data,
        },
        headers: {
            'X-CSRFToken':  document.getElementById('deleteform'+data).firstElementChild.value
        },
    }).done(function (data) {
        $('#modal'+data.id).modal('hide');
        document.getElementById('item'+data.id).remove();
    });
}

