var bcrypt = dcodeIO.bcrypt;
window.addEventListener(`resize`, event => {
    var h = document.getElementById('login-box').clientHeight;
    var full_h = document.documentElement.clientHeight;
    var t = (full_h - h) / 4;
    document.getElementById('login-img').setAttribute('style', 'top: ' + t + 'px;')
}, false);

// START //
document.addEventListener('DOMContentLoaded', function () {
    var h = document.getElementById('login-box').clientHeight;
    var full_h = document.documentElement.clientHeight;
    var t = (full_h - h) / 4;
    document.getElementById('login-img').setAttribute('style', 'top: ' + t + 'px;')
});
// ----- //
// SUBMIT //
function log_in() {
    fetch('/login', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : 'submit',
            'login' : document.getElementById('login').value,
        })
    })
    .then(function (response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                if (response.connection == 'on') {
                    console.log(response.pwd)
                    if (bcrypt.hashSync(document.getElementById('pwd').value, response.pwd.slice(0,29)) == response.pwd) {
                        url = response.url
                        fetch('/login', {
                            headers : {
                                'Content-Type' : 'application/json'
                            },
                            method : 'POST',
                            body : JSON.stringify( {
                                'action' : 'submit_ok',
                            })
                        })
                        setTimeout(function(){document.location.href = '/' + url;},500);
                    }
                    else {console.log('Password not equal!')}
                }
            });
        }
        else {
            throw Error('Something went wrong');
        }
    })
}
// ----- //