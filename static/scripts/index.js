// START //
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
                document.getElementById('version').textContent = 'Микролинк-связь ООО \u00A9 \u00AE, 2023, '+ response.version;
//                show_fieldset(0);
//                show_fieldset(1);
//                if (response.priority == 1) {
//                    var nodes = document.getElementById("main-base").getElementsByTagName('*');
//                    for(var i = 0; i < nodes.length; i++){
//                         nodes[i].disabled = true;
//                    }
//                    document.getElementById('main-base').disabled = true;
//                }
            })
        }
    })
});
// ----- //
// SET TIME //
document.addEventListener('DOMContentLoaded', () => {
                  setInterval(setPageTime, 1000);
              });

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
// VALIDATE //
document.addEventListener('DOMContentLoaded', () => {
                  setInterval(request_validate, 9999);
              });
              function request_validate() {
                    fetch('/index', {
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
// BUTTONS //
function show_fieldset(number) {
    var nodes = document.getElementById("fs_1").getElementsByTagName('*');
    for(var y = 0; y < nodes.length; y++){
         nodes[y].disabled = false;
    }
    let $s_list = document.querySelector('#service_list');
    if ($s_list) {$s_list.parentElement.removeChild($s_list);}
    $s_list = document.querySelector('#service_treeline');
    if ($s_list) {$s_list.parentElement.removeChild($s_list);}
    $s_list = document.querySelector('#div_services');
    if ($s_list) {$s_list.parentElement.removeChild($s_list);}
    $s_list = document.querySelector('#div_srv_module');
    if ($s_list) {$s_list.parentElement.removeChild($s_list);}
    for (var i = 0; i<5; i++) {
        if ((document.getElementById('fs_'+i))&&(i != number)) {
            document.getElementById('fs_'+i).style.visibility = 'hidden';
            document.getElementById('fs_'+i).style.zIndex = '0';
        }
        else {
            document.getElementById('fs_'+i).style.visibility = 'visible';
            document.getElementById('fs_'+i).style.zIndex = '100';
            if (number != '3') {
                fetch('/index', {
                    headers : {
                        'Content-Type' : 'application/json'
                    },
                    method : 'POST',
                    body : JSON.stringify( {
                        'action' : 'get_service',
                    })
                })
                .then(function (response){
                    if(response.ok) {
                        response.json()
                        .then(function(response) {
                            if ((response.connection == 'on')&&(response.service.length > 0)) {
                                if (number == '4') {service_list.init(response.service);}
                                if (number == '2') {service_module.init(response.service);}
                                if (number == '1') {scr_service.init(response.service);}
                                if (number == '0') {service_treeline.init(response.service);}
                            }
                        })
                    }
                })
            }
        }
    }
}

function active_man() {
    var nodes = document.getElementById("fs_1").getElementsByTagName('*');
    for(var i = 0; i < nodes.length; i++){
         nodes[i].disabled = false;
    }
}

// ----- //
// SERVICES TABLE //
const service_list = {
    elements: {
        main: null,
        usrContainer: null
    },

    init(db_user) {
        this.elements.main = document.createElement("div");
        this.elements.main.classList.add("pids_list");
        this.elements.main.id = 'service_list';
        this.elements.main.style.height = "53vh";
        this.elements.main.style.overflow = "auto";
        for (let i = 0; i < db_user.length; i++) {
            this.elements.usrContainer = document.createElement("div");
            this.elements.usrContainer.classList.add("pid_info");
            user_info = db_user[i];
            for (let y = 1; y < user_info.length; y++) {
                const keyElement = document.createElement("div");
                if (y == 1) {
                    keyElement.classList.add("pid_key");
                    keyElement.textContent = user_info[y];
                }
                else {
                    keyElement.classList.add("pid_key_c");
                    if (Number(user_info[y]) > 32768) {keyElement.textContent = '' + (Number(user_info[y]) - 32768)}
                    else {keyElement.textContent = user_info[y];}
                }
                keyElement.id = 's_'+user_info[0]+'_'+y;
                this.elements.usrContainer.appendChild(keyElement);
            }
            let keyElement = document.createElement("img");
            keyElement.classList.add("pid_key_small");
            keyElement.src="/static/images/buttons/change_perm.png";
            keyElement.alt="Изменить сервис";
            keyElement.setAttribute('onclick', "return new_service.init('s_"+user_info[0]+"');");
            keyElement.style.width = "5vh"
            keyElement.style.height = "5vh"
            this.elements.usrContainer.appendChild(keyElement);
            keyElement = document.createElement("img");
            keyElement.classList.add("pid_key_small");
            keyElement.src="/static/images/buttons/delete_user.png";
            keyElement.alt="Удалить сервис";
            keyElement.setAttribute('onclick', "return approve_delete.init("+user_info[0]+", 'delete_service');");
            keyElement.style.width = "5vh"
            keyElement.style.height = "5vh"
            this.elements.usrContainer.appendChild(keyElement);
            this.elements.main.appendChild(this.elements.usrContainer);
        }
        document.getElementById('pid_field').appendChild(this.elements.main);
    }
};
// ----- //
// NEW SERVICE //
const new_service = {
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
        if (_user == 'new') {keyElement.textContent = "Добавить новый сервис";}
        else {keyElement.textContent = "Изменить сервис";}
        this.elements.box.appendChild(keyElement);

        this.elements.usrContainer = document.createElement("div");
        this.elements.usrContainer.classList.add("user_box");
        keyElement = document.createElement("input");
        keyElement.type = "text";
        keyElement.id = "new_service";
        if (_user != 'new') {keyElement.value = document.getElementById(_user+'_1').textContent;}
        this.elements.usrContainer.appendChild(keyElement);
        keyElement = document.createElement("label");
        keyElement.textContent = "Название сервиса";
        this.elements.usrContainer.appendChild(keyElement);
        this.elements.box.appendChild(this.elements.usrContainer);

        this.elements.usrContainer = document.createElement("div");
        this.elements.usrContainer.classList.add("user_box");
        keyElement = document.createElement("input");
        keyElement.type = "text";
        keyElement.id = "new_video1";
        if (_user != 'new') {keyElement.value = document.getElementById(_user+'_2').textContent;}
        this.elements.usrContainer.appendChild(keyElement);
        keyElement = document.createElement("label");
        keyElement.textContent = "PID видео";
        this.elements.usrContainer.appendChild(keyElement);
        this.elements.box.appendChild(this.elements.usrContainer);

        this.elements.usrContainer = document.createElement("div");
        this.elements.usrContainer.classList.add("user_box");
        keyElement = document.createElement("input");
        keyElement.type = "text";
        keyElement.id = "new_audio1";
        if (_user != 'new') {keyElement.value = document.getElementById(_user+'_3').textContent;}
        this.elements.usrContainer.appendChild(keyElement);
        keyElement = document.createElement("label");
        keyElement.textContent = "PID аудио1";
        this.elements.usrContainer.appendChild(keyElement);
        this.elements.box.appendChild(this.elements.usrContainer);

        this.elements.usrContainer = document.createElement("div");
        this.elements.usrContainer.classList.add("user_box");
        keyElement = document.createElement("input");
        keyElement.type = "text";
        keyElement.id = "new_audio2";
        if (_user != 'new') {keyElement.value = document.getElementById(_user+'_4').textContent;}
        this.elements.usrContainer.appendChild(keyElement);
        keyElement = document.createElement("label");
        keyElement.textContent = "PID аудио2";
        this.elements.usrContainer.appendChild(keyElement);
        this.elements.box.appendChild(this.elements.usrContainer);

        this.elements.usrContainer = document.createElement("div");
        this.elements.usrContainer.classList.add("user_box");
        keyElement = document.createElement("button");
        if (_user == 'new') {keyElement.textContent = "Добавить";}
        else {keyElement.textContent = "Изменить";}
        keyElement.setAttribute('onclick', "return send_service('"+_user+"');");
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
// SERVICES TREELINE //
// https://iamkate.com/code/tree-views/ //
const service_treeline = {
    elements: {
        main: null,
        ulContainer: null,
        liContainer: null
    },

    init(db_user) {
        const att = document.createAttribute("open");
        this.elements.main = document.createElement("ul");
        this.elements.main.classList.add("tree");
        this.elements.main.id = 'service_treeline';
        this.elements.main.textContent = "T2-MI over MPEG2 TS";
        this.elements.main.style.height = "68vh";
        this.elements.main.style.overflow = "auto";
        let li_main = document.createElement("li");
        li_main.textContent = "PMT - 0x0100";
        this.elements.main.appendChild(li_main);
        li_main = document.createElement("li");
        li_main.textContent = "DATA - 0x1000";
        let ul_main = document.createElement("ul");
        for (let i = 0; i < db_user.length; i++) {
            user_info = db_user[i];
            let keyElement;
            let keyDetail;
            this.elements.liContainer = document.createElement("li");
            keyDetail = document.createElement('details');
            keyElement = document.createElement('summary');
            keyElement.textContent = user_info[1];
            keyDetail.appendChild(keyElement);
            this.elements.ulContainer = document.createElement("ul");
            for (let y = 2; y < user_info.length; y++) {
                if (user_info[y] != '') {
                    keyElement = document.createElement("li");
                    if (Number(user_info[y]) > 32768) {keyElement.textContent = '' + (Number(user_info[y]) - 32768)}
                    else {keyElement.textContent = user_info[y];}
                    keyElement.style.display = "list-item";
                    if (y == 2) {keyElement.style.listStyleImage = "url('/static/images/buttons/v_srv_20.png')";}
                    else {keyElement.style.listStyleImage = "url('/static/images/buttons/a_srv_20.png')";}
                    keyElement.style.listStylePosition = "inside";
                    keyElement.style.paddingLeft = "1vh";
                    keyElement.style.background = "none";
                    this.elements.ulContainer.appendChild(keyElement);
                }
            }
            keyDetail.appendChild(this.elements.ulContainer);
            this.elements.liContainer.appendChild(keyDetail);

            ul_main.appendChild(this.elements.liContainer);
        }
        li_main.appendChild(ul_main);
        this.elements.main.appendChild(li_main);
        document.getElementById('fs_0').appendChild(this.elements.main);
//        document.getElementsByTagName("details").setAttributeNode(att);
    }
};
// ----- //
// SERVICES FOR MODULE //
const service_module = {
    elements: {
        div_main: null,
        inputContainer: null,
        labelContainer: null
    },
//    <div><input type="checkbox" id="calc_coord" name="vehicle1" value=1>
//        <label for="vehicle1">Пересчитать координаты для спутников</label>
//    </div>

    init(db_user) {
        let main = document.createElement("div");
        main.id = "div_srv_module"
        for (let i = 0; i < db_user.length; i++) {
            user_info = db_user[i];
            this.elements.div_main = document.createElement("div");
            this.elements.div_main.style.padding = "1vh";
            this.elements.inputContainer = document.createElement("input");
            this.elements.inputContainer.setAttribute('type', "checkbox");
            this.elements.inputContainer.id = user_info[0];
            this.elements.inputContainer.name = 'service';
            this.elements.div_main.appendChild(this.elements.inputContainer);
            this.elements.labelContainer = document.createElement("label");
            this.elements.labelContainer.setAttribute('for', user_info[0]);
            this.elements.labelContainer.textContent = user_info[1];
            this.elements.div_main.appendChild(this.elements.labelContainer);
            main.appendChild(this.elements.div_main);
        }
        document.getElementById('srv_module').appendChild(main);
    }
};
// ----- //
// SCR MANAGEMENT //
const scr_service = {
    elements: {
        main: null,
        ulContainer: null,
        liContainer: null
    },

    init(db_user) {
        this.elements.main = document.createElement("div");
        this.elements.main.id = 'div_services'
        this.elements.main.style.height = "100%";
        this.elements.main.style.width = "100%";
        this.elements.main.style.display = "flex";
        this.elements.main.style.flexDirection = "row";
        this.elements.main.style.flexWrap = "wrap";
        this.elements.main.style.alignContent = "flex-start";
        this.elements.main.style.justifyContent = "flex-start";
        for (let i = 0; i < db_user.length; i++) {
            user_info = db_user[i];
            let keyElement;
            let keyIMG;
            let keyDetail;
            keyDetail = document.createElement("ul");
            keyDetail.classList.add("tree");
            keyDetail.style.width = "20vh";
            keyDetail.style.padding = "0";
            keyDetail.id = 'service_'+user_info[0];
            keyDetail.textContent = user_info[1];
            for (let y = 2; y < user_info.length; y++) {
                if (user_info[y] != '') {
                    keyElement = document.createElement("li");
                    if (Number(user_info[y]) > 32768) {keyElement.textContent = '' + (Number(user_info[y]) - 32768)}
                    else {keyElement.textContent = user_info[y];}
                    keyElement.style.display = "list-item";
                    keyElement.id = 'pid_'+user_info[0]+'_'+(y-1)
                    if (y == 2) {keyElement.style.listStyleImage = "url('/static/images/buttons/v_srv_20.png')";}
                    else {keyElement.style.listStyleImage = "url('/static/images/buttons/a_srv_20.png')";}
                    keyElement.style.listStylePosition = "inside";
                    keyElement.style.paddingLeft = "1vh";
                    keyElement.style.background = "none";
                    keyDetail.appendChild(keyElement);
                    keyIMG = document.createElement("img");
    //                keyElement.classList.add("user_key_small");
                    if (Number(user_info[y]) > 32768) {keyIMG.src="/static/images/buttons/lock_20.png";}
                    else {keyIMG.src="/static/images/buttons/unlock_20.png";}
                    keyIMG.style.padding = "0 1vh";
    //                keyElement.alt="Изменить права";
                    keyIMG.setAttribute('onclick', "return send_cmd(this);");
                    keyIMG.id = "img"+user_info[0]+(y-1).toString();
                    keyIMG.setAttribute('pid', user_info[y]);
                    keyIMG.setAttribute('db_id', user_info[0]+(y-1).toString());
    //                keyElement.style.width = "5vh"
    //                keyElement.style.height = "5vh"
                    keyElement.appendChild(keyIMG);
                }
            }
            this.elements.main.appendChild(keyDetail);
        }
        document.getElementById('scrambling').appendChild(this.elements.main);
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
function del_row(_id, _action) {
    fetch('/index', {
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
                    close_popup();
                    show_fieldset('9');
                }
            });
        }
        else {
            throw Error('Something went wrong');
        }
    })
}
function str2float(x) {
    var floatValue = +(x);
    return floatValue;
}
function send_service(_action) {
    if (_action == 'new') {_status = 'new_service';}
    else {_status = 'update_service';}
    _id = _action;
    _service = document.getElementById('new_service').value;
    _video1 = document.getElementById('new_video1').value;
    _audio1 = document.getElementById('new_audio1').value;
    _audio2 = document.getElementById('new_audio2').value;
    fetch('/index', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : _status,
            'id' : _id,
            'service' : _service,
            'video1' : _video1,
            'audio1' : _audio1,
            'audio2' : _audio2,
        })
    })
    .then(function (response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                if (response.status == 'reload') {setTimeout(function(){window.location.reload();},500);}
            });
        }
        else {
            throw Error('Something went wrong');
        }
    })
}
function readfpga() {
    fetch('/index', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : 'read_cmd',
        })
    })
    .then(function (response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                console.log(response.status);
                document.getElementById('readfpga').value = response.status
            });
        }
        else {
            throw Error('Something went wrong');
        }
    })
}
function init() {
    fetch('/index', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : 'init',
        })
    })
    .then(function (response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                console.log(response.status);
            });
        }
        else {
            throw Error('Something went wrong');
        }
    })
}
function send_data() {
    let data = document.getElementById('send_data').value
    if (data != '') {
        document.getElementById('send_data').value = ''
        fetch('/index', {
            headers : {
                'Content-Type' : 'application/json'
            },
            method : 'POST',
            body : JSON.stringify( {
                'action' : 'send_data',
                'data': data,
            })
        })
        .then(function (response){
            if(response.ok) {
                response.json()
                .then(function(response) {
                    console.log(response.status);
                });
            }
            else {
                throw Error('Something went wrong');
            }
        })
    }
    else {console.log('Nothing to send!')}
}
function send_cmd(e) {
    var image = document.getElementById('img'+e.getAttribute('db_id'));
    var hex_pid = Number(e.getAttribute('pid')).toString(16);
    while (hex_pid.length < 4) {hex_pid = '0' + hex_pid;}
    p_l = hex_pid.slice(2);
    const myarray = e.src.split("/");
    if (myarray[myarray.length - 1] == "unlock_20.png") {
        if (hex_pid.slice(0,1)=='1') {p_h = '9'+hex_pid.slice(1,2);}
        else {p_h = '8'+hex_pid.slice(1,2);}
        image.src = "/static/images/buttons/lock_20.png";
    }
    else {
        if (hex_pid.slice(0,1)=='9') {p_h = '1'+hex_pid.slice(1,2);}
        else {p_h = '0'+hex_pid.slice(1,2);}
        image.src = "/static/images/buttons/unlock_20.png";
    }
    fetch('/index', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : 'send_cmd',
            'command': '70,'+p_l+';78,'+p_h,
            'pid'    : ''+parseInt(p_h+p_l, 16),
            'db_id'  : e.getAttribute('db_id'),
        })
    })
    .then(function (response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                console.log(response.status);
            });
        }
        else {
            throw Error('Something went wrong');
        }
    })
}
function send_module(action) {
    let checkboxes = document.querySelectorAll('input[name="service"]:checked');
    let values = [];
    checkboxes.forEach((checkbox) => {values.push(checkbox.id);});
    if (values.length > 0) {
        fetch('/index', {
            headers : {
                'Content-Type' : 'application/json'
            },
            method : 'POST',
            body : JSON.stringify( {
                'action' : action,
                'module' : document.getElementById('module').value,
                'ids'    : values,
            })
        })
        .then(function (response){
            if(response.ok) {
                response.json()
                .then(function(response) {
                    console.log(response.status);
                });
            }
            else {
                throw Error('Something went wrong');
            }
        })
    }
    else {console.log('nothing')}
}
