var bcrypt = dcodeIO.bcrypt;
// START //
document.addEventListener('DOMContentLoaded', function () {
    fetch('/system', {
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
                if (response.connection == 'on') {
                    User_list.init(response.users);
                }
            })
        }
    })
});
// ----- //
// VALIDATE //
document.addEventListener('DOMContentLoaded', () => {setInterval(request_validate, 9999);});
function request_validate() {
    fetch('/system', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : 'validate',
        })
    })
    .then(function (response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                if (response.status == 'logout') {
                    window.location = 'logout'
                }
            });
        }
        else {
            throw Error('Something went wrong');
        }
    })
    .catch(function(error) {
        console.log(error);
    });
}
// ----- //
// SET TIME //
document.addEventListener('DOMContentLoaded', () => {setInterval(setPageTime, 1000);});
function setPageTime() {
    var currentDateObj = document.getElementById('current-date');
    if (currentDateObj) {
        var monthList = new Array('января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля',
            'августа', 'сентября', 'октября', 'ноября', 'декабря');
        var currDate = new Date();
        var m = monthList[currDate.getMonth()];
        var _m = currDate.getMonth()+1;
        var d = currDate.getDate();
        var hh = currDate.getHours();
        var mm = currDate.getMinutes();
        var ss = currDate.getSeconds();
        if (d<10) { d = '0' + d }
        if (hh<10) { hh = '0' + hh }
        if (mm<10) { mm = '0' + mm }
        if (ss<10) { ss = '0' + ss }
        if (_m<10) { _m = '0' + _m }
        var s = hh + ':' + mm + ':' + ss + ' / ' + d + ' ' + m + ' ' + currDate.getFullYear();
        currentDateObj.innerHTML = s;
    }
}
// ----- //
// USERs TABLE //
const User_list = {
    elements: {
        main: null,
        usrContainer: null
    },

    init(db_user) {
        this.elements.main = document.createElement("div");
        this.elements.main.classList.add("users_list");
        this.elements.main.style.height = "68vh";
        this.elements.main.style.overflow = "auto";
        for (let i = 0; i < db_user.length; i++) {
            this.elements.usrContainer = document.createElement("div");
            this.elements.usrContainer.classList.add("user_info");
            user_info = db_user[i];
            for (let y = 0; y < user_info.length-3; y++) {
                const keyElement = document.createElement("div");
                keyElement.classList.add("user_key");
                keyElement.textContent = user_info[y];
                keyElement.id = 'u_'+user_info[8]+'_'+y;
                if (y==5) {
                    keyElement.classList.toggle("login", user_info[7]);
                }
                this.elements.usrContainer.appendChild(keyElement);
            }
            const keyElement = document.createElement("img");
            keyElement.classList.add("user_key_small");
            keyElement.src ="/static/images/buttons/change_pwd.png";
            keyElement.alt ="Изменить пароль";
            keyElement.setAttribute('onclick', "return new_pwd.init("+user_info[8]+");");
            keyElement.style.width = "5vh"
            keyElement.style.height = "5vh"
            this.elements.usrContainer.appendChild(keyElement);
            if (user_info[6] < 10) {
                let keyElement = document.createElement("img");
                keyElement.classList.add("user_key_small");
                keyElement.src="/static/images/buttons/change_perm.png";
                keyElement.alt="Изменить права";
                keyElement.setAttribute('onclick', "return new_user.init('u_"+user_info[8]+"');");
                keyElement.style.width = "5vh"
                keyElement.style.height = "5vh"
                this.elements.usrContainer.appendChild(keyElement);
                keyElement = document.createElement("img");
                keyElement.src="/static/images/buttons/delete_user.png";
                keyElement.alt="Удалить пользователя";
                keyElement.setAttribute('onclick', "return approve_delete.init("+user_info[8]+", 'delete_user');");
                keyElement.style.width = "5vh"
                keyElement.style.height = "5vh"
                this.elements.usrContainer.appendChild(keyElement);
            }
            this.elements.main.appendChild(this.elements.usrContainer);
        }
        document.getElementById('user_field').appendChild(this.elements.main);
    }
};
// ----- //
// NEW USER //
const new_user = {
    elements: {
        popup: null,
        box: null,
        usrContainer: null
    },
    init(_user) {
        this.elements.main = document.createElement("div");
        this.elements.main.classList.add("pop_up");
        this.elements.box = document.createElement("fieldset");
        this.elements.box.classList.add("add_box");
        let keyElement = document.createElement("div");
        keyElement.classList.add("user_box");
        if (_user == 'new') {keyElement.textContent = "Добавить нового пользователя";}
        else {keyElement.textContent = "Изменить пользователя";}
        this.elements.box.appendChild(keyElement);

        this.elements.usrContainer = document.createElement("div");
        this.elements.usrContainer.classList.add("user_box");
        keyElement = document.createElement("input");
        keyElement.type = "text";
        keyElement.id = "new_fullname";
        if (_user != 'new') {keyElement.value = document.getElementById(_user+'_0').textContent;}
        this.elements.usrContainer.appendChild(keyElement);
        keyElement = document.createElement("label");
        keyElement.textContent = "ФИО";
        this.elements.usrContainer.appendChild(keyElement);
        this.elements.box.appendChild(this.elements.usrContainer);

        this.elements.usrContainer = document.createElement("div");
        this.elements.usrContainer.classList.add("user_box");
        keyElement = document.createElement("input");
        keyElement.type = "text";
        keyElement.id = "new_login";
        if (_user != 'new') {keyElement.value = document.getElementById(_user+'_1').textContent;}
        this.elements.usrContainer.appendChild(keyElement);
        keyElement = document.createElement("label");
        keyElement.textContent = "Логин";
        this.elements.usrContainer.appendChild(keyElement);
        this.elements.box.appendChild(this.elements.usrContainer);
        if (_user == 'new') {
            this.elements.usrContainer = document.createElement("div");
            this.elements.usrContainer.classList.add("user_box");
            keyElement = document.createElement("input");
            keyElement.type = "text";
            keyElement.id = "new_pwd";
            this.elements.usrContainer.appendChild(keyElement);
            keyElement = document.createElement("label");
            keyElement.textContent = "Пароль";
            this.elements.usrContainer.appendChild(keyElement);
            this.elements.box.appendChild(this.elements.usrContainer);

            this.elements.usrContainer = document.createElement("div");
            this.elements.usrContainer.classList.add("user_box");
            keyElement = document.createElement("input");
            keyElement.type = "text";
            keyElement.id = "new_pwd2";
            this.elements.usrContainer.appendChild(keyElement);
            keyElement = document.createElement("label");
            keyElement.textContent = "Пароль повторно";
            this.elements.usrContainer.appendChild(keyElement);
            this.elements.box.appendChild(this.elements.usrContainer);
        }

        this.elements.usrContainer = document.createElement("div");
        this.elements.usrContainer.classList.add("choose-label");
        keyElement = document.createElement("label");
        keyElement.textContent = "Роль";
        this.elements.usrContainer.appendChild(keyElement);
        this.elements.box.appendChild(this.elements.usrContainer);

        this.elements.usrContainer = document.createElement("div");
        this.elements.usrContainer.classList.add("user_box");
        let selectElement = document.createElement("select");
        selectElement.classList.add("choose-box");
        selectElement.id = "new_priority";
        keyElement = document.createElement("option");
        keyElement.textContent = 'Наблюдатель';
        keyElement.setAttribute('value', 1);
        keyElement.setAttribute('selected', true);
        selectElement.appendChild(keyElement);
        keyElement = document.createElement("option");
        keyElement.textContent = 'Оператор';
        keyElement.setAttribute('value', 2);
        selectElement.appendChild(keyElement);
        keyElement = document.createElement("option");
        keyElement.textContent = 'Оператор системный';
        keyElement.setAttribute('value', 3);
        selectElement.appendChild(keyElement);
        this.elements.usrContainer.appendChild(selectElement);
        this.elements.box.appendChild(this.elements.usrContainer);

        this.elements.usrContainer = document.createElement("div");
        this.elements.usrContainer.classList.add("user_box");
        keyElement = document.createElement("button");
        if (_user == 'new') {keyElement.textContent = "Добавить";}
        else {keyElement.textContent = "Изменить";}
        keyElement.setAttribute('onclick', "return send_user('"+_user+"');");
        keyElement.id = "update_user";
        this.elements.usrContainer.appendChild(keyElement);
        keyElement = document.createElement("button");
        keyElement.textContent = "Закрыть";
        keyElement.setAttribute('onclick', "return close_popup();");
        this.elements.usrContainer.appendChild(keyElement);
        this.elements.box.appendChild(this.elements.usrContainer);

        this.elements.main.appendChild(this.elements.box);
        document.getElementById('main').appendChild(this.elements.main);
    }
};
// ----- //
// NEW PWD //
const new_pwd = {
    elements: {
        popup: null,
        box: null,
        usrContainer: null
    },
    init(_user) {
        this.elements.main = document.createElement("div");
        this.elements.main.classList.add("pop_up");
        this.elements.box = document.createElement("fieldset");
        this.elements.box.classList.add("add_box");
        let keyElement = document.createElement("div");
        keyElement.classList.add("user_box");
        keyElement.textContent = "Изменить пароль пользователя"
        this.elements.box.appendChild(keyElement);

         this.elements.usrContainer = document.createElement("div");
        this.elements.usrContainer.classList.add("user_box");
        keyElement = document.createElement("input");
        keyElement.type = "text";
        keyElement.id = "new_pwd";
        this.elements.usrContainer.appendChild(keyElement);
        keyElement = document.createElement("label");
        keyElement.textContent = "Пароль";
        this.elements.usrContainer.appendChild(keyElement);
        this.elements.box.appendChild(this.elements.usrContainer);

        this.elements.usrContainer = document.createElement("div");
        this.elements.usrContainer.classList.add("user_box");
        keyElement = document.createElement("input");
        keyElement.type = "text";
        keyElement.id = "new_pwd2";
        this.elements.usrContainer.appendChild(keyElement);
        keyElement = document.createElement("label");
        keyElement.textContent = "Пароль повторно";
        this.elements.usrContainer.appendChild(keyElement);
        this.elements.box.appendChild(this.elements.usrContainer);

        this.elements.usrContainer = document.createElement("div");
        this.elements.usrContainer.classList.add("user_box");
        keyElement = document.createElement("button");
        keyElement.textContent = "Изменить";
        keyElement.id = "update_user";
        keyElement.setAttribute('onclick', "return send_pwd("+_user+");");
        this.elements.usrContainer.appendChild(keyElement);
        keyElement = document.createElement("button");
        keyElement.textContent = "Закрыть";
        keyElement.setAttribute('onclick', "return close_popup();");
        this.elements.usrContainer.appendChild(keyElement);
        this.elements.box.appendChild(this.elements.usrContainer);

        this.elements.main.appendChild(this.elements.box);
        document.getElementById('main').appendChild(this.elements.main);
    }
};
// ----- //
// APPROVE DELETE //
const approve_delete = {
    elements: {
        popup: null,
        box: null,
        usrContainer: null
    },
    init(_id, _bd) {
        this.elements.main = document.createElement("div");
        this.elements.main.classList.add("pop_up");
        this.elements.box = document.createElement("fieldset");
        this.elements.box.classList.add("add_box");
        let keyElement = document.createElement("div");
        keyElement.classList.add("user_box");
        keyElement.textContent = "Удалить запись из БД?"
        this.elements.box.appendChild(keyElement);

        this.elements.usrContainer = document.createElement("div");
        this.elements.usrContainer.classList.add("user_box");
        keyElement = document.createElement("button");
        keyElement.textContent = "Да";
        keyElement.id = "update_user";
        keyElement.setAttribute('onclick', "return del_row("+_id+", '"+_bd+"');");
        this.elements.usrContainer.appendChild(keyElement);
        keyElement = document.createElement("button");
        keyElement.textContent = "Закрыть";
        keyElement.setAttribute('onclick', "return close_popup();");
        this.elements.usrContainer.appendChild(keyElement);
        this.elements.box.appendChild(this.elements.usrContainer);

        this.elements.main.appendChild(this.elements.box);
        document.getElementById('main').appendChild(this.elements.main);
    }
};
// ----- //
function close_popup() {$('.pop_up').remove();}
function send_user(_action) {
    if (_action == 'new') {
        _status = 'new_user';
        _password = bcrypt.hashSync(document.getElementById('new_pwd').value, 12);
    }
    else {
        _status = 'update_user';
        _password = '';
    }
    _id = _action;
    _login = document.getElementById('new_login').value;
    _fullname = document.getElementById('new_fullname').value;
    _job = $("#new_priority option:selected").text();;
    _priority = document.getElementById('new_priority').value;
    fetch('/system', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : _status,
            'id' : _id,
            'login' : _login,
            'password' : _password,
            'fullname' : _fullname,
            'job' : _job,
            'priority' : _priority,
        })
    })
    .then(function (response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                if (response.status == 'reload') {
                        setTimeout(function(){window.location.reload();},500);
                }
            });
        }
        else {
            throw Error('Something went wrong');
        }
    })
}
function del_row(_id, _action) {
    fetch('/system', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : _action,
            'id' : _id,
        })
    })
    .then(function (response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                if (response.status == 'delete ok') {
                        setTimeout(function(){window.location.reload();},500);
                }
            });
        }
        else {
            throw Error('Something went wrong');
        }
    })
}
function send_pwd(_id) {
    _password = bcrypt.hashSync(document.getElementById('new_pwd').value, 12);
    console.log(_password);
    fetch('/system', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : 'update_pwd',
            'id' : _id,
            'password' : _password,
        })
    })
    .then(function (response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                if (response.status == 'logout') {setTimeout(function(){document.location.href = '/logout';},500);}
                else {
                    close_popup();
                    console.log('password updated');
                }
            });
        }
        else {
            throw Error('Something went wrong');
        }
    })
}