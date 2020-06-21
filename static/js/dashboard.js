function convertLocalDate() {
    var dates = document.getElementsByClassName('date');
    var open_dates = document.getElementsByClassName('date-open');
    var j;
    var olen = open_dates.length;
    var i;
    var len = dates.length;
    for (i = 0; i < len; i++) {
        var timestamp = dates[i].textContent;
        if (timestamp != 'No use-by or best-before date provided' 
            && timestamp != 'Not opened/ Not something that can be opened' 
            && timestamp != 'Not frozen/ Cannot be frozen'
            && timestamp.includes('Today') == false
            && timestamp.includes('Yesterday') == false) {
            var local = new Date(timestamp);
            var now = new Date();
            if (local.toDateString() == now.toDateString()) {
                var date = 'Today';
                dates[i].classList.add('today');

            }else if (local.getDate() < now.getDate()) {
                var date = local.toDateString();
                dates[i].classList.add('past');
            } else {
                 var date = local.toDateString();
            }  
            dates[i].innerText = date; 
        }    
    }
    for (j = 0; j < olen; j++) {
        var openstamp = open_dates[j].textContent;
        var olocal = new Date(openstamp);
        var onow = new Date();
        if (olocal.toDateString() == onow.toDateString()) {
            var odate = 'Today';
        } else {
            var odate = olocal.toDateString();
        }  
        open_dates[j].innerText = odate; 
    }

    return; 
}

function greeting() {
    let now_time = new Date();
    if (now_time.getHours() < 12)
        return "Morning"
    else if (now_time.getHours() >= 12 && now_time.getHours() < 17)
        return "Afternoon"
    else
        return "Evening"
}
document.addEventListener('DOMContentLoaded', () => {
    convertLocalDate();
    document.getElementById('greeting').innerText = greeting();
});