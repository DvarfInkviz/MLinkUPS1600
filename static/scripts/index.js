// INPUTMASK //
document.addEventListener('DOMContentLoaded', function () {
    $("#u_akb_min").inputmask({mask: "9{1,2}В", placeholder: '0'});
    $("#u_akb_max").inputmask({mask: "9{1,2}B", placeholder: '0'});
    $("#i_akb_min").inputmask({mask: "9{1,2}.9{1,2}A", placeholder: '0'});
    $("#i_akb_max").inputmask({mask: "9{1,2}.9{1,2}A", placeholder: '0'});
    $("#u_abc_min").inputmask({mask: "9{1,3}B", placeholder: '0'});
    $("#u_abc_max").inputmask({mask: "9{1,3}B", placeholder: '0'});
    $("#u_abc_alarm_min").inputmask({mask: "9{1,3}B", placeholder: '0'});
    $("#u_abc_alarm_max").inputmask({mask: "9{1,3}B", placeholder: '0'});
    $("#u_load_max").inputmask({mask: "9{1,2}.9{1}B", placeholder: '0'});
    $("#i_load_max").inputmask({mask: "9{1,2}A", placeholder: '0'});
    $("#t_charge_max").inputmask({mask: "9{1,2}ч", placeholder: '0'});
    $("#discharge_abc").inputmask({mask: "9{1,2}%", placeholder: '0'});
    $("#discharge_akb").inputmask({mask: "9{1,2}%", placeholder: '0'});
//    $("#t_delay").inputmask({mask: "9{1,3}мс", placeholder: '0'});
    $("#q_akb").inputmask({mask: "9{1,3}А\u00B7ч", placeholder: '0'});
    $("#i_charge_max").inputmask({mask: "9{1,2}A", placeholder: '0'});
    $("#u_load_abc").inputmask({mask: "9{1,2}B", placeholder: '0'});

//    $("#az_err").inputmask({mask: "9{1,3}.9{1,3}\u00B0", placeholder: '_'});
//    $("#el_err").inputmask({mask: "9{1,3}.9{1,3}\u00B0", placeholder: '_'});
//    $("#pl_err").inputmask({mask: "9{1,3}.9{1,3}\u00B0", placeholder: '_'});
//    $("#mlevel_track").inputmask({mask: "[~]9{1,2}.9{1}", definitions: {'~': { validator: "[+-]",}}, placeholder: '_'});
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
                document.getElementById('version').textContent = 'Микролинк-связь ООО \u00A9 \u00AE, 2023, '+ response.version + '.'+response.iakb1_0+'.'+response.uakb4_0;
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
                            s_status = "Работа от АКБ";
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
                    document.getElementById('discharge_abc').value = response.discharge_abc+'%';
                    document.getElementById('discharge_akb').value = response.discharge_akb+'%';
                    document.getElementById('i_load_max').value = response.i_load_max+'A';
                    document.getElementById('q_akb').value = response.q_akb+'A\u00B7ч';
                    document.getElementById('i_charge_max').value = response.i_charge_max+'A';
                    document.getElementById('u_load_abc').value = response.u_load_abc+'B';
                    document.getElementById('time_zone').value = response.time_zone;
                    document.getElementById('t_delay').value = response.t_delay;
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
        }
    }
}