// INPUTMASK //
document.addEventListener('DOMContentLoaded', function () {
    $("#pl_new").inputmask({mask: "[~]9{1,3}.9{1,3}\u00B0", definitions: {'~': { validator: "[+-]",}}, placeholder: '0'});
    $("#az_new").inputmask({mask: "9{1,3}.9{1,3}\u00B0", placeholder: '0'});
    $("#el_new").inputmask({mask: "9{1,3}.9{1,3}\u00B0", placeholder: '0'});
    $("#freq").inputmask({mask: "9{1,5}.9{1,2}", placeholder: '0'});
    $("#speed").inputmask({mask: "9{1,2}\u0025", placeholder: '0'});
    $("#pl_min").inputmask({mask: "[~]9{1,3}.9{1,3}\u00B0", definitions: {'~': { validator: "[+-]",}}, placeholder: '0'});
    $("#pl_max").inputmask({mask: "[~]9{1,3}.9{1,3}\u00B0", definitions: {'~': { validator: "[+-]",}}, placeholder: '0'});
    $("#az_min").inputmask({mask: "9{1,3}.9{1,3}\u00B0", placeholder: '0'});
    $("#el_min").inputmask({mask: "9{1,3}.9{1,3}\u00B0", placeholder: '0'});
    $("#az_max").inputmask({mask: "9{1,3}.9{1,3}\u00B0", placeholder: '0'});
    $("#el_max").inputmask({mask: "9{1,3}.9{1,3}\u00B0", placeholder: '0'});
    $("#az_enc").inputmask({mask: "9{1,3}", placeholder: '0'});
    $("#el_enc").inputmask({mask: "9{1,3}", placeholder: '0'});
    $("#pl_enc").inputmask({mask: "9{1,3}", placeholder: '0'});
    $("#rcv_bndw").inputmask({mask: "9{1,3}", placeholder: '0'});
    $("#pl_correct").inputmask({mask: "9{1,3}.9{1,4}", placeholder: '0'});
    $("#track_step").inputmask({mask: "9{1,3}.9{1,4}", placeholder: '0'});
    $("#delta").inputmask({mask: "9{1,3}.9{1,4}", placeholder: '0'});
    $("#rcv_tilt").inputmask({mask: "9{1,3}.9{1,4}", placeholder: '0'});
    $("#az_err").inputmask({mask: "9{1,3}.9{1,3}\u00B0", placeholder: '0'});
    $("#el_err").inputmask({mask: "9{1,3}.9{1,3}\u00B0", placeholder: '0'});
    $("#pl_err").inputmask({mask: "9{1,3}.9{1,3}\u00B0", placeholder: '0'});
});
// ----- //
// UPDATE STATUS //
document.addEventListener('DOMContentLoaded', () => {
                  setInterval(request_status, 210);
              });
              function request_status() {
                    if (document.getElementById('st_14').textContent == 'Панель') {mode = 2;}
                    if (document.getElementById('st_14').textContent == 'Основное') {mode = 1;}
                    if (document.getElementById('st_14').textContent == 'Настройка ') {mode = 0;}
                    fetch('/engineer', {
                        headers : {
                            'Content-Type' : 'application/json'
                        },
                        method : 'POST',
                        body : JSON.stringify( {
                            'action' : 'status',
                            'mode'   : mode,
                        })
                    })
                    .then(function (response){
                        if(response.ok) {
                            response.json()
                            .then(function(response) {
                                if (response.connection == 'on') {
                                    document.getElementById('led_status').style.background = '#0f0';
                                    if (response.comanda != '0') {
                                        for (var i = 2; i<7; i++) {
                                            if (response.comanda == i) {
                                                if (document.getElementById('cmd_'+i)) {
                                                    document.getElementById('cmd_'+i).style.background = '#0f0';
                                                }
                                                if (i == 2) {stop();}
                                            }
                                        }
                                        if ((response.register_status[2] == '0')&&(response.comanda == 12)) {stop();}
                                    }
                                    else {
                                        for (var i = 2; i<7; i++) {
                                            if (document.getElementById('cmd_'+i)) {
                                                document.getElementById('cmd_'+i).style.background = 'linear-gradient(0deg, #77ccfd 0%, #6cc3ee 100%)';
                                            }
                                        }
                                    }
                                    if ((response.register_status[2] == '1')&&(response.register_status[4] == '0')&&(response.register_status[5] == '0')&&(response.register_status[3] == '0')) {stop();}
                                    document.getElementById('az_cur').textContent = response.position_az+'\u00B0';
                                    document.getElementById('el_cur').textContent = response.position_el+'\u00B0';
                                    document.getElementById('pl_cur').textContent = response.position_pl+'\u00B0';
                                    document.getElementById('freq').value = response.frequency;
                                    document.getElementById('level').textContent = response.level+'dBm';
                                    let reg_st = 'st_'
                                    for (var i = 0; i < response.register_status.length; i++) {
                                        if (response.register_status[i] == '1') {
                                            if (document.getElementById(reg_st + i)) {
                                                if (i == 14) {
                                                    document.getElementById(reg_st + i).textContent = 'Панель';
                                                    document.getElementById(reg_st + i).disabled = true;
                                                    document.getElementById(reg_st + i).style.background = '#f33';
                                                    var nodes = document.getElementById("position").getElementsByTagName('*');
                                                    for(var i = 0; i < nodes.length; i++){nodes[i].disabled = true;}
                                                    settings_frame_close();
                                                }
                                                if (i == 15) {
                                                    document.getElementById(reg_st + i).style.background = '#f33';
                                                }
                                                else {
                                                    document.getElementById(reg_st + i).style.background = '#0f0';
                                                }
                                            }
                                        }
                                        else {
                                            if (document.getElementById(reg_st + i)) {
                                                if (i == 14) {
                                                    document.getElementById(reg_st + i).disabled = false;
                                                    if (mode == 1) {
                                                        document.getElementById('st_14').textContent = 'Основное';
                                                        document.getElementById('st_14').style.background = '#f93';
                                                        var nodes = document.getElementById("position").getElementsByTagName('*');
                                                        for(var i = 0; i < nodes.length; i++){nodes[i].disabled = true;}
                                                        settings_frame_close();
                                                    }
                                                    else {
                                                        document.getElementById('st_14').textContent = 'Настройка';
                                                        document.getElementById('st_14').style.background = '#0f0';
                                                        var nodes = document.getElementById("position").getElementsByTagName('*');
                                                        for(var i = 0; i < nodes.length; i++){nodes[i].disabled = false;}
                                                        if (document.getElementById('pl_pr').value == '0') {document.getElementById('pl_new').disabled = true;}
                                                        if (document.getElementById('track').value == '0') {
                                                            document.getElementById('cmd_6').disabled = true;
                                                            document.getElementById('freq').disabled = true;
                                                            document.getElementById('as_3').disabled = true;
                                                        }
                                                    }
                                                }
                                                else {
                                                    if (i == 15) {
                                                        document.getElementById(reg_st + i).style.background = 'rgba(234,234,234,1)';
                                                    }
                                                    else {
                                                        document.getElementById(reg_st + i).style.background = '#999';
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    let reg_erhw = 'erhw_'
                                    for (var i = 6; i < 9; i++) {
                                        if ((response.register_errorhw[i] == '1')||(response.register_errorhw[i+3] == '1')) {
                                            if (document.getElementById(reg_erhw + i)) {
                                                document.getElementById(reg_erhw + i).style.background = '#f33';
                                            }
                                        }
                                        else {
                                            if ((response.register_errorhw[i] == '0')&&(response.register_errorhw[i+3] == '0')) {
                                                if (document.getElementById(reg_erhw + i)) {
                                                    document.getElementById(reg_erhw + i).style.background = '#999';
                                                }
                                            }
                                        }
                                    }
                                    for (var i = 12; i < 15; i++) {
                                        if (response.register_errorhw[i] == '1') {
                                            if (document.getElementById(reg_erhw + i)) {
                                                document.getElementById(reg_erhw + i).style.background = '#f33';
                                            }
                                        }
                                        else {
                                            if (document.getElementById(reg_erhw + i)) {
                                                document.getElementById(reg_erhw + i).style.background = '#999';
                                            }
                                        }
                                    }
                                    let reg_ershw = 'ershw_'
                                    var flag = 0
                                    for (var i = 0; i < 6; i++) {
                                        flag = 0
                                        if (response.register_errorsw[i] == '1') { flag = 1}
                                        if (response.register_errorhw[i] == '1') { flag = 2}
                                        if ((response.register_errorhw[i] == '1')&&(response.register_errorsw[i] == '1')){ flag = 3}
                                        if (flag == 0) {
                                            document.getElementById(reg_ershw + i).style.background = '#999';
                                            document.getElementById(reg_ershw + i).textContent = '';
                                        }
                                        if (flag == 1) {
                                            document.getElementById(reg_ershw + i).style.background = '#f33';
                                            document.getElementById(reg_ershw + i).textContent = 'прог.';
                                        }
                                        if (flag == 2) {
                                            document.getElementById(reg_ershw + i).style.background = '#f33';
                                            document.getElementById(reg_ershw + i).textContent = 'аппарат.';
                                        }
                                        if (flag == 3) {
                                            document.getElementById(reg_ershw + i).style.background = '#f33';
                                            document.getElementById(reg_ershw + i).textContent = 'ап./пр.';
                                        }
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
// VALIDATE //
document.addEventListener('DOMContentLoaded', () => {
                  setInterval(request_validate, 999);
              });
              function request_validate() {
                    fetch('/engineer', {
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
        var d = currDate.getDate();
        var hh = currDate.getHours();
        var mm = currDate.getMinutes();
        var ss = currDate.getSeconds();
        if (d<10) { d = '0' + d }
        if (hh<10) { hh = '0' + hh }
        if (mm<10) { mm = '0' + mm }
        if (ss<10) { ss = '0' + ss }
        var s = hh + ':' + mm + ':' + ss + ' / ' + d + ' ' + m + ' ' + currDate.getFullYear();
        currentDateObj.innerHTML = s;
    }
}
// ----- //
// START //
var mode = 1;
document.addEventListener('DOMContentLoaded', function () {
    fetch('/engineer', {
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
                    if (response.track == '1') {
                        document.getElementById('cmd_6').disabled = false;
                        document.getElementById('freq').disabled = false;
                        document.getElementById('as_3').disabled = false;
                    }
                    else {
                        document.getElementById('cmd_6').disabled = true;
                        document.getElementById('freq').disabled = true;
                        document.getElementById('as_3').disabled = true;
                    }
                    document.getElementById('version').textContent = 'ТрилайнСистемс ООО \u00A9 \u00AE, 2022, web.0.3b, v.0.5 - ' + response.ipplc + ' - ' + response.login;
                    document.getElementById('az_cur').textContent = response.position_az+'\u00B0';
                    document.getElementById('el_cur').textContent = response.position_el+'\u00B0';
                    document.getElementById('pl_cur').textContent = response.position_pl+'\u00B0';
                    document.getElementById('az_new').value = response.position_az+'\u00B0';
                    document.getElementById('el_new').value = response.position_el+'\u00B0';
                    document.getElementById('pl_new').value = response.position_pl+'\u00B0';
                    if (response.pl_pr == '1') {
                        document.getElementById('pl_new').disabled = false;
                    }
                    else {
                        document.getElementById('pl_new').disabled = true;
                    }
                    document.getElementById('freq').value = response.frequency;
                    document.getElementById('level').textContent = response.level+'dBm';
                    document.getElementById('speed').value = response.speed+'\u0025';
                    document.getElementById('cmd_5').textContent = 'Поз. Скор. ' + document.getElementById('speed').value;
                }
            })
        }
    })
});
// ----- //
function change_mode() {
    if (document.getElementById('st_14').textContent == 'Основное') {
        mode = 0;
        document.getElementById('st_14').textContent = 'Настройка';
        document.getElementById('st_14').style.background = '#0f0';
        var nodes = document.getElementById("position").getElementsByTagName('*');
        for(var i = 0; i < nodes.length; i++){nodes[i].disabled = false;}
        if (document.getElementById('pl_pr').value == '0') {document.getElementById('pl_new').disabled = true;}
        if (document.getElementById('track').value == '0') {
            document.getElementById('cmd_6').disabled = true;
            document.getElementById('freq').disabled = true;
            document.getElementById('as_3').disabled = true;
        }
        else {document.getElementById('as_3').disabled = false;}
    }
    else {
        document.getElementById('st_14').textContent = 'Основное';
        mode = 1;
        document.getElementById('st_14').style.background = '#f93';
        var nodes = document.getElementById("position").getElementsByTagName('*');
        for(var i = 0; i < nodes.length; i++){nodes[i].disabled = true;}
        settings_frame_close();
    }
    fetch('/engineer', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : 'change_mode',
            'mode': mode,
         })
    })
}

function set_speed(e) {document.getElementById('cmd_5').textContent = 'Поз. Скор. ' + e.value;}

function bind(cmd) {
    if (document.getElementById('cmd_'+cmd).style.background == 'rgb(0, 255, 0)') {
        stop()
    }
    else {
        fetch('/engineer', {
            headers : {
                'Content-Type' : 'application/json'
            },
            method : 'POST',
            body : JSON.stringify( {
                'action' : 'bind',
                'command': cmd,
                'az_new' : document.getElementById('az_new').value,
                'el_new' : document.getElementById('el_new').value,
                'pl_new' : document.getElementById('pl_new').value,
                'az_cur' : document.getElementById('az_cur').textContent,
                'el_cur' : document.getElementById('el_cur').textContent,
                'pl_cur' : document.getElementById('pl_cur').textContent,
                'speed'  : document.getElementById('speed').value,
                'freq'   : document.getElementById('freq').value,
            })
        })
        .then(function (response){
            if(response.ok) {
                response.json()
                .then(function(response) {
                    if (response.connection == 'on') {
                        console.log(response.status);
                        if (response.status == 'send new values') {
                            for (var i = 2; i<7; i++) {
                                if ((document.getElementById('cmd_'+i))&&(i != cmd)) {
                                    document.getElementById('cmd_'+i).disabled = true;
                                }
                            }
                            document.getElementById('cmd_6').disabled = document.getElementById('freq').disabled;
                            for (var i = 0; i<6; i++) {
                                document.getElementById('pos_'+i).disabled = true;
                                document.getElementById('pos_'+i).style.opacity = '0.2';
                            }
                        }
                    }
                })
            }
        });
    }
}

function man_bind(cmd) {
    if (((document.getElementById('pl_new').disabled == true)&&(cmd != '32')&&(cmd != '16'))||(document.getElementById('pl_new').disabled == false)){
        fetch('/engineer', {
            headers : {
                'Content-Type' : 'application/json'
            },
            method : 'POST',
            body : JSON.stringify( {
                'action' : 'man_bind',
                'command': cmd,
                'az_new' : document.getElementById('az_new').value,
                'el_new' : document.getElementById('el_new').value,
                'pl_new' : document.getElementById('pl_new').value,
                'speed'  : document.getElementById('speed').value,
            })
        })
        .then(function (response){
            if(response.ok) {
                response.json()
                .then(function(response) {
                    if (response.connection == 'on') {
                        console.log(response.status);
                    }
                })
            }
        });
    }
}

function settings_frame_open() {
    document.getElementById('body').style.height = '767px';
    element_settings_show('add_settings');
    element_settings_close('add_settings_loader');
    element_settings_close('receiver_settings');
    element_settings_close('limit_settings');
    element_settings_close('antenna_settings');
}

function settings_frame_close() {
    element_settings_close('add_settings');
    element_settings_close('receiver_settings');
    element_settings_close('limit_settings');
    element_settings_close('antenna_settings');
    element_settings_close('add_settings_loader');
}

function element_settings_close(element) {
    document.getElementById(element).style.visibility = 'hidden';
    document.getElementById(element).style.width = '0px';
    document.getElementById(element).style.height = '0px';
    document.getElementById(element).style.margin = '0px';
    document.getElementById(element).style.padding = '0px';
}

function element_settings_show(element) {
    document.getElementById(element).style.visibility = 'visible';
    document.getElementById(element).style.width = '363px';
    document.getElementById(element).style.height = 'auto';
    document.getElementById(element).style.margin = '10px 0 0 10px';
    document.getElementById(element).style.padding = '10px';
}

function stop() {
    document.getElementById('az_new').value = document.getElementById('az_cur').textContent;
    document.getElementById('el_new').value = document.getElementById('el_cur').textContent;
    document.getElementById('pl_new').value = document.getElementById('pl_cur').textContent;
    fetch('/engineer', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : 'stop',
        })
    })
    .then(function (response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                if (response.connection == 'on') {
                    console.log(response.status);
                    for (var i = 2; i<7; i++) {
                        if (document.getElementById('cmd_'+i)) {
                            document.getElementById('cmd_'+i).disabled = false;
                        }
                    }
                    document.getElementById('cmd_6').disabled = document.getElementById('freq').disabled;
                    for (var i = 0; i<6; i++) {
                        document.getElementById('pos_'+i).disabled = false;
                        document.getElementById('pos_'+i).style.opacity = '1';
                    }
                }
            })
        }
    });
}

function read_file(file_name, file_id) {
    element_settings_close('antenna_settings');
    element_settings_close('limit_settings');
    element_settings_close('receiver_settings');
    element_settings_show('add_settings_loader');
    fetch('/engineer', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : 'read_file',
            'name' : file_name,
            'file_id': file_id,
        })
    })
    .then(function (response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                console.log(response.status)
                if ((response.status == 'Read file ' + file_name + ' all ok')||(response.status == 'No such file or directory')) {
                    if (file_id == 1) {
                        element_settings_close('add_settings_loader');
                        element_settings_show('antenna_settings');
                        document.getElementById('az_enc').value = response.az_enc;
                        document.getElementById('el_enc').value = response.el_enc;
                        document.getElementById('pl_enc').value = response.pl_enc;
                        document.getElementById('pl_ph').value = response.pl_ph;
                        document.getElementById('pl_correct').value = response.pl_correct;
                        document.getElementById('az_err').value = response.az_err;
                        document.getElementById('el_err').value = response.el_err;
                        document.getElementById('pl_err').value = response.pl_err;
                        document.getElementById('pl_pr').value = response.pl_pr;
                        document.getElementById('track').value = response.track;
                        document.getElementById('track_step').value = response.track_step;
                        document.getElementById('signal_min').value = response.signal_min;
                        document.getElementById('delta').value = response.delta;
                    }
                    if (file_id == 2) {
                        element_settings_close('add_settings_loader');
                        element_settings_show('receiver_settings');
                        document.getElementById('rcv_bndw').value = response.rcv_bndw;
                        document.getElementById('rcv_filter').value = response.rcv_filter;
                        document.getElementById('rcv_tilt').value = response.rcv_tilt;
                    }
                    if (file_id == 0) {
                        element_settings_close('add_settings_loader');
                        element_settings_show('limit_settings');
                        document.getElementById('az_min').value = response.az_min;
                        document.getElementById('el_min').value = response.el_min;
                        document.getElementById('pl_min').value = response.pl_min;
                        document.getElementById('az_max').value = response.az_max;
                        document.getElementById('el_max').value = response.el_max;
                        document.getElementById('pl_max').value = response.pl_max;
                    }
                }
                if (response.status == 'No such file or directory') {
                    document.getElementById('err_text_'+file_id).style.height = 'auto';
                    document.getElementById('err_text_'+file_id).style.padding = '6px 10px 0 10px';
                    document.getElementById('err_text_'+file_id).style.color = '#f00';
                    document.getElementById('err_text_'+file_id).textContent = 'Необходимо записать параметры в память!'
                }
                else {
                    document.getElementById('err_text_'+file_id).style.height = '0px';
                    document.getElementById('err_text_'+file_id).style.padding = '0px';
                    document.getElementById('err_text_'+file_id).textContent = ''
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

function write_file(file_name, file_id) {
    element_settings_close('antenna_settings');
    element_settings_close('limit_settings');
    element_settings_close('receiver_settings');
    document.getElementById('add_settings_loader_legend').textContent = 'Запись параметров'
    element_settings_show('add_settings_loader');

    var data = '';
    if (file_id == 1) {
        data = 'EN'+document.getElementById('az_enc').value+';'+document.getElementById('el_enc').value+';'+document.getElementById('pl_enc').value+';'+document.getElementById('pl_ph').value+';'+document.getElementById('pl_correct').value+';\nER';
        data = data + document.getElementById('az_err').value.slice(0,-1)+';'+document.getElementById('el_err').value.slice(0,-1)+';'+document.getElementById('pl_err').value.slice(0,-1)+';\nPR';
        data = data + document.getElementById('pl_pr').value+';'+document.getElementById('track').value+';'+document.getElementById('track_step').value+';'+document.getElementById('delta').value+';\nOK\n'
        if (document.getElementById('pl_pr').value == '1') {document.getElementById('pl_new').disabled = false;}
        else {document.getElementById('pl_new').disabled = true;}
        if (document.getElementById('track').value == '1') {
            document.getElementById('cmd_6').disabled = false;
            document.getElementById('freq').disabled = false;
            document.getElementById('as_3').disabled = false;
        }
        else {
            document.getElementById('cmd_6').disabled = true;
            document.getElementById('freq').disabled = true;
            document.getElementById('as_3').disabled = true;
        }
    }
    if (file_id == 2) {
        data = 'BC'+document.getElementById('rcv_bndw').value+';'+document.getElementById('rcv_filter').value+';'+document.getElementById('rcv_tilt').value+';\n'
    }
    if (file_id == 0) {
        data = 'SW'+document.getElementById('az_min').value.slice(0,-1)+';'+document.getElementById('az_max').value.slice(0,-1)+';'+document.getElementById('el_min').value.slice(0,-1)+';'
        data = data + document.getElementById('el_max').value.slice(0,-1)+';'+document.getElementById('pl_min').value.slice(0,-1)+';'+document.getElementById('pl_max').value.slice(0,-1)+';\n'
    }
    fetch('/engineer', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : 'write_file',
            'name' : file_name,
            'file_id': file_id,
            'data': data,
        })
    })
    .then(function (response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                document.getElementById('add_settings_loader_legend').textContent = 'Чтение параметров'
                element_settings_close('add_settings_loader');
                if (file_id == 1) { element_settings_show('antenna_settings'); }
                if (file_id == 0) { element_settings_show('limit_settings'); }
                if (file_id == 2) { element_settings_show('receiver_settings'); }
                document.getElementById('err_text_'+file_id).style.height = '0px';
                document.getElementById('err_text_'+file_id).style.padding = '0px';
                document.getElementById('err_text_'+file_id).textContent = ''
                console.log(response.status);
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
