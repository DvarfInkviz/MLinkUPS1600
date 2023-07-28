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
//                if (response.connection == 'on') {
                    document.getElementById('discharge_abc').value = response.discharge_abc+'%';
                    document.getElementById('discharge_akb').value = response.discharge_akb+'%';
                    document.getElementById('i_load_max').value = response.i_load_max+'A';
                    document.getElementById('q_akb').value = response.q_akb+'A\u00B7ч';
                    document.getElementById('i_charge_max').value = response.i_charge_max+'A';
                    document.getElementById('u_load_abc').value = response.u_load_abc+'B';
                    document.getElementById('time_zone').value = response.time_zone;
                    document.getElementById('t_delay').value = response.t_delay;
                    document.getElementById('iakb1_0').value = response.iakb1_0;
                    document.getElementById('iakb1').value = response.iakb1;
                    document.getElementById('uakb1').value = response.uakb1;
                    document.getElementById('uakb2').value = response.uakb2;
                    document.getElementById('uakb3').value = response.uakb3;
                    document.getElementById('uakb4').value = response.uakb4;
                    document.getElementById('iload').value = response.iload;
                    document.getElementById('ua').value = response.ua;
                    document.getElementById('ub').value = response.ub;
                    document.getElementById('uc').value = response.uc;
                    document.getElementById('temp_akb').value = response.temp_akb;
                    document.getElementById('temp_air').value = response.temp_air;
//                }
//                else {
//                                    document.getElementById('led_status').style.background = '#f33';
//                }
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