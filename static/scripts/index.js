// INPUTMASK //
document.addEventListener('DOMContentLoaded', function () {
    $("#i_load_max").inputmask({mask: "9{2}A", placeholder: '_'});
    $("#discharge_depth").inputmask({mask: "9{2}%", placeholder: '_'});
    $("#q_akb").inputmask({mask: "9{2,3}А\u00B7ч", placeholder: '_'});
    $("#u_abc_max").inputmask({mask: "9{2}B", placeholder: '_'});
    $("#max_temp_air").inputmask({mask: "9{2}\u00B0C", placeholder: '_'});
    $("#ip_addr").inputmask({alias: "ip",greedy: false});
    $("#ip_mask").inputmask({alias: "ip",greedy: false});
    $("#ip_gate").inputmask({alias: "ip",greedy: false});
});
// ----- //
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
                document.getElementById('version').textContent = 'Микролинк-связь ООО \u00A9 \u00AE, 2023, '+ response.version + '.'+response.iakb1_0;
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
//document.addEventListener('DOMContentLoaded', () => {
//                  setInterval(request_validate, 9999);
//              });
//              function request_validate() {
//                    fetch('/index', {
//                        headers : {
//                            'Content-Type' : 'application/json'
//                        },
//                        method : 'POST',
//                        body : JSON.stringify( {
//                            'action' : 'validate',
//                        })
//                    })
//                    .then(function (response){
//                        if(response.ok) {
//                            response.json()
//                            .then(function(response) {
//                                if (response.status == 'logout') {
//                                    window.location = 'logout'
//                                }
//                            });
//                        }
//                        else {
//                            throw Error('Something went wrong');
//                        }
//                    })
//                    .catch(function(error) {
//                        console.log(error);
//                    });
//                }
// ----- //

// UPDATE STATUS //
var s_status;
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => { setInterval(request_status, 800); }, 300);
              });
function request_status() {
    fetch('/index', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : 'status'
        })
    })
    .then(function (response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                if (response.connection == 'on') {
                    switch (response.state) {
                        case '0':
                            switch (response.status) {
                                case 194:
                                    s_status = "Работа от АКБ - заряд АКБ";
                                    break;
                                case 196:
                                    s_status = "Работа от АКБ - разряд АКБ";
                                    break;
                                default:
                                    s_status = "Работа от АКБ - разряд АКБ";
                            }
                            break;
                        case '1':
                            s_status = "Работа от сети без АКБ";
                            break;
                        case '2':
                            switch (response.status) {
                                case 194:
                                    s_status = "Буферный режим - заряд АКБ";
                                    break;
                                case 196:
                                    s_status = "Буферный режим - разряд АКБ";
                                    break;
                                default:
                                    s_status = "Буферный режим - заряд АКБ";
                            }
                            break;
                        case '3':
                            switch (response.err) {
                                case 64:
                                    s_status = "Критическая ошибка - перегрузка по току!";
                                    break;
                                case 32:
                                    s_status = "Критическая ошибка - перегрузка по напряжению!";
                                    break;
                                case 4:
                                    s_status = "Критическая ошибка - датчик тока вышел из строя!";
                                    break;
                                case 8:
                                    s_status = "Критическая ошибка - напряжение на фазах вне диапазона!";
                                    break;
                                case 16:
                                    s_status = "Критическая ошибка - напряжение на АКБ вне диапазона!";
                                    break;
                                case 128:
                                    s_status = "Критическая ошибка - перегрев АКБ!";
                                    break;
                                default:
                                    s_status = "Неизвестная критическая ошибка - Code#" + response.err;
                            }
                            break;
                    }
                    document.getElementById('led_status').style.background = '#3f3';
                    document.getElementById('err_sts').textContent = s_status;
                    document.getElementById('iakb1').textContent = response.iakb1+' A';
                    document.getElementById('uakb1').textContent = response.uakb1+' B';
                    if (response.uakb1 == 0) {
                        document.getElementById('uakb2').textContent = '0.0 B';
                        document.getElementById('uakb3').textContent = '0.0 B';
                        document.getElementById('uakb4').textContent = '0.0 B';
                    }
                    else {
                        document.getElementById('uakb2').textContent = response.uakb2+' B';
                        document.getElementById('uakb3').textContent = response.uakb3+' B';
                        document.getElementById('uakb4').textContent = response.uakb4+' B';
                    }
                    document.getElementById('uload').textContent = response.uload+' B';
                    document.getElementById('iload').textContent = response.iload+' A';
                    document.getElementById('u_bv').textContent = response.u_bv+' B';
                    document.getElementById('ua').textContent  = response.ua+' B';
                    document.getElementById('ub').textContent  = response.ub+' B';
                    document.getElementById('uc').textContent  = response.uc+' B';
                    document.getElementById('tinv1').textContent  = response.tinv1+' \u00B0C';
                    document.getElementById('tinv2').textContent  = response.tinv2+' \u00B0C';
                    document.getElementById('tinv3').textContent  = response.tinv3+' \u00B0C';
                    document.getElementById('iinv1').textContent  = response.iinv1+' A';
                    document.getElementById('iinv2').textContent  = response.iinv2+' A';
                    document.getElementById('iinv3').textContent  = response.iinv3+' A';
                    document.getElementById('temp_akb').textContent = response.temp_akb+' \u00B0C';
                    document.getElementById('temp_air').textContent = response.temp_air+' \u00B0C';
//                    document.getElementById('temp_cpu').textContent = response.temp_cpu+' \u00B0C';
                    document.getElementById('dry1_in').classList.toggle('rele_in_up', response.dry1_in);
                    document.getElementById('dry2_in').classList.toggle('rele_in_up', response.dry2_in);
                    document.getElementById('dry3_in').classList.toggle('rele_in_up', response.dry3_in);
                    document.getElementById('dry4_in').classList.toggle('rele_in_up', response.dry4_in);
                    document.getElementById('dry1_out').classList.toggle('rele_out_up', response.dry1_out);
                    document.getElementById('dry2_out').classList.toggle('rele_out_up', response.dry2_out);
                    document.getElementById('dry3_out').classList.toggle('rele_out_up', response.dry3_out);
                    document.getElementById('dry4_out').classList.toggle('rele_out_up', response.dry4_out);
                    if (response.bv1_status == 'ok') {
                        document.getElementById('bv1_status').classList.toggle('alerts-border', 0);
                        document.getElementById('bv1_status').style.background = '#3f3';
                    }
                    if (response.bv2_status == 'ok') {
                        document.getElementById('bv2_status').classList.toggle('alerts-border', 0);
                        document.getElementById('bv2_status').style.background = '#3f3';
                    }
                    if (response.bv3_status == 'ok') {
                        document.getElementById('bv3_status').classList.toggle('alerts-border', 0);
                        document.getElementById('bv3_status').style.background = '#3f3';
                    }
                    if (response.bv1_status == 'alarm') {
                        document.getElementById('bv1_status').classList.toggle('alerts-border', 1);
                        document.getElementById('bv1_status').style.background = '#3f3';
                    }
                    if (response.bv2_status == 'alarm') {
                        document.getElementById('bv2_status').classList.toggle('alerts-border', 1);
                        document.getElementById('bv2_status').style.background = '#3f3';
                    }
                    if (response.bv3_status == 'alarm') {
                        document.getElementById('bv3_status').classList.toggle('alerts-border', 1);
                        document.getElementById('bv3_status').style.background = '#3f3';
                    }
                    if (response.bv1_status == 'error') {
                        document.getElementById('bv1_status').classList.toggle('alerts-border', 1);
                        document.getElementById('bv1_status').style.background = '#999';
                    }
                    if (response.bv2_status == 'error') {
                        document.getElementById('bv2_status').classList.toggle('alerts-border', 1);
                        document.getElementById('bv2_status').style.background = '#999';
                    }
                    if (response.bv3_status == 'error') {
                        document.getElementById('bv3_status').classList.toggle('alerts-border', 1);
                        document.getElementById('bv3_status').style.background = '#999';
                    }
                }
                else {
                    document.getElementById('led_status').style.background = '#f33';
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
    const $journal_list = document.querySelector('#table_journal');
    if ($journal_list) {$journal_list.parentElement.removeChild($journal_list);}
    var nodes = document.getElementById("fs_1").getElementsByTagName('*');
    for(var y = 0; y < nodes.length; y++){
         nodes[y].disabled = false;
    }
    for (var i = 0; i<3; i++) {
        if ((document.getElementById('fs_'+i))&&(i != number)) {
            document.getElementById('fs_'+i).style.visibility = 'hidden';
            document.getElementById('fs_'+i).style.zIndex = '0';
        }
        else {
            document.getElementById('fs_'+i).style.visibility = 'visible';
            document.getElementById('fs_'+i).style.zIndex = '100';
            if (i == 1) {
                fetch('/index', {
                    headers : {
                        'Content-Type' : 'application/json'
                    },
                    method : 'POST',
                    body : JSON.stringify( {
                        'action' : 'get_journal',
                    })
                })
                .then(function (response){
                    if(response.ok) {
                        response.json()
                        .then(function(response) {
                            if (response.status == 'ok') {
                                journal.init(response.journal);
                            }
                        })
                    }
                })
            }
            if (i == 2) {
                fetch('/index', {
                    headers : {
                        'Content-Type' : 'application/json'
                    },
                    method : 'POST',
                    body : JSON.stringify( {
                        'action' : 'get_settings',
                    })
                })
                .then(function (response){
                    if(response.ok) {
                        response.json()
                        .then(function(response) {
                            if (response.status == 'ok') {
                                document.getElementById('discharge_depth').value = response.discharge_depth+'%';
                                document.getElementById('i_load_max').value = response.i_load_max+'A';
                                document.getElementById('q_akb').value = response.q_akb+'A\u00B7ч';
                                document.getElementById('u_abc_max').value = response.u_abc_max+'B';
                                document.getElementById('time_zone').value = response.time_zone;
                                document.getElementById('max_temp_air').value = response.max_temp_air;
                                document.getElementById('ip_addr').value = response.ip_addr;
                                document.getElementById('ip_mask').value = response.ip_mask;
                                document.getElementById('ip_gate').value = response.ip_gate;
                            }
                        })
                    }
                })
            }
        }
    }
}
function check_input(el) {
    let text = el.value;
    while (text.indexOf('_') >= 0) {text = text.replace('_', '0');}
    el.value = text;
    fetch('/index', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : 'update',
            'status_values': el.id,
            'value' : text,
        })
    })
}

function check_input_ip(el) {
    let text = el.value;
    fetch('/index', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : 'update_ip',
            'status_values': el.id,
            'value' : text,
        })
    })
}
// JOURNAL //
const journal = {
    elements: {
        table: null,
        tr: null
    },
    init(db_journal) {
        this.elements.table = document.createElement("table");
        this.elements.table.id = "table_journal";
        let _td;
        let keyElement;
        for (let i = 0; i < db_journal.length; i++) {
            this.elements.tr = document.createElement("tr");
            _td = db_journal[i].split("#");
            for (let j = 0; j < _td.length; j++) {
                keyElement = document.createElement("td");
                keyElement.textContent = _td[j];
                this.elements.tr.appendChild(keyElement);
            }
            this.elements.table.appendChild(this.elements.tr)
        }
        document.getElementById('journal').appendChild(this.elements.table);
    }
};
// ----- //