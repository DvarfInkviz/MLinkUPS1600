document.addEventListener('DOMContentLoaded', function () {
    fetch('/index', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : 'start',
        })
    })
    .then(function (response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                if (response.connection === 'on') {
                    document.getElementById('version').textContent = 'ТрилайнСистемс ООО \u00A9 \u00AE, 2022, web_m.0.1, v.0.1 - ' + response.ipplc + ' - ' + response.login;
                }
            })
        }
    })
});