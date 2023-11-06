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
                document.getElementById('version').textContent = 'Микролинк-связь ООО \u00A9 \u00AE, 2023, '+ response.version;
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
//                    document.getElementById('led_status').style.background = '#3f3';
//                    if (response.t_charge_mode == '0') {document.getElementById('t_charge_mode').textContent = "0:00:00.0"}
//                    else {document.getElementById('t_charge_mode').textContent = response.t_charge_mode;}
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
    for (var i = 0; i<4; i++) {
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
                                document.getElementById('ip_mac').value = response.ip_mac;
                                document.getElementById('localdaytime').value = response.datetime;
                                document.getElementById('btn_reboot').style.visibility = 'hidden';
                            }
                        })
                    }
                })
            }
        }
    }
}
var ip4, gate4, mask4;
function rem(el) {
    if (el.id == 'ip_addr') {ip4 = el.value}
    if (el.id == 'ip_mask') {mask4 = el.value}
    if (el.id == 'ip_gate') {gate4 = el.value}
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
            'value' : parseFloat(text),
        })
    })
}
function reboot_pc() {
    spinner.init();
    ip4 = document.getElementById('ip_addr').value;
    fetch('/index', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : 'reboot',
            'ipv4': document.getElementById('ip_addr').value,
            'mask4': document.getElementById('ip_mask').value,
            'gate4': document.getElementById('ip_gate').value,
        })
    })
    setTimeout(reload_page, 30000);
}
function reload_page() {
    close_popup();
    window.open("http://"+ip4, "_self");
}
function check_input_ip(el) {
    let text = el.value;
    if ((el.id == 'ip_addr')&&(ip4 != el.value)) {document.getElementById('btn_reboot').style.visibility = 'visible';}
    if ((el.id == 'ip_mask')&&(mask4 != el.value)) {document.getElementById('btn_reboot').style.visibility = 'visible';}
    if ((el.id == 'ip_gate')&&(gate4 != el.value)) {document.getElementById('btn_reboot').style.visibility = 'visible';}
//    fetch('/index', {
//        headers : {
//            'Content-Type' : 'application/json'
//        },
//        method : 'POST',
//        body : JSON.stringify( {
//            'action' : 'update_ip',
//            'status_values': el.id,
//            'value' : text,
//        })
//    })
}
// ----- /
const handleImageUpload = event => {
  let files = event.target.files
  let formData = new FormData()
  formData.append('myFile', files[0])

  fetch('/index', {
    method: 'POST',
    body: formData
  })
    .then(function (response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                document.getElementById('update_arm').style.visibility = 'visible';
                console.log(response.file_info)
            })
        }
    })
  .catch(error => {
    console.error(error)
  })
}

document.querySelector('#fileUpload').addEventListener('change', event => {
  handleImageUpload(event)
})
function stm32loader() {
    spinner.init();
    fetch('/index', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'action' : 'stm32loader',
        })
    })
    .then(function (response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                console.log(response.status);
                close_popup();
                show_fieldset(0);
                    fetch('/index', {
                        headers : {
                            'Content-Type' : 'application/json'
                        },
                        method : 'POST',
                        body : JSON.stringify( {
                            'action' : 'stm32_work',
                        })
                    })
                    .then(function (response){
                        if(response.ok) {
                            response.json()
                            .then(function(response) {
                                console.log(response.status);
                })}})
            })
        }
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
// Canvas //
var MAX_DATA_SET_LENGTH = 120;
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => { setInterval(reLoad, 1000); }, 1000);
              });
function reLoad() {
//  adddata(44, 56);
    var u1 = parseFloat(document.getElementById('u_bv').textContent);
    var u2 = parseFloat(document.getElementById('uload').textContent);
  adddata(u1, u2);
}

var canvas = document.getElementById('myChart');
var data = {
  datasets: [{
      label: 'Uупр.',
      borderColor: 'rgb(237, 18, 237)',
      fill: false,
      borderWidth: 1
    },
    {
      label: 'Uнаг.',
      borderColor: 'rgb(0, 115, 255)',
      fill: false,
      borderWidth: 1
    }
  ]
}
var options = {
  scales: {
    yAxes: [{
      type: 'linear',
      ticks: {
        min: 40,
        suggestedMax: 60
      }
    }],

    xAxes: [{
      type: 'time',
      ticks: {
        maxTicksLimit: 5,
      },
      time: {
        unit: 'second',
        displayFormats: {
          'second': 'HH:mm:ss',
        },
        tooltipFormat: 'HH:mm:ss',
      }
    }]
  },
  showLines: true
};
var myChart = new Chart.Line(canvas, {
  data: data,
  options: options
});

function adddata(download = NaN, upload = NaN, label = moment()) {
  var datasets = myChart.data.datasets;
  var labels = myChart.data.labels;
  var downloadDataSet = datasets[0].data;
  var uploadDataSet = datasets[1].data;

  var downloadDataLength = downloadDataSet.length;
  var uploadDataLength = uploadDataSet.length;

  // if upload/download's data set has more than MAX_DATA_SET_LENGTH entries,
  // remove the first one entry and push on a new data entry
  var didRemoveData = false;
  if (downloadDataLength > MAX_DATA_SET_LENGTH) {
    downloadDataSet.shift();
    didRemoveData = true;
  }

  if (uploadDataLength > MAX_DATA_SET_LENGTH) {
    uploadDataSet.shift();
    didRemoveData = true;
  }

  // if either download or upload data was removed, we also need to remove
  // the first label to keep the data from squeezing in.
  if (didRemoveData) {
    labels.shift();
  }

  labels.push(label);
  downloadDataSet.push(download);
  uploadDataSet.push(upload);
  myChart.update();
}
//-----------//
// SPINNER //
const spinner = {
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
        keyElement.textContent = "LOAD...";
        keyElement.style.height = "200px";

        this.elements.usrContainer = document.createElement("div");
        this.elements.usrContainer.classList.add("load-1");
        let keyElement2 = document.createElement("div");
        keyElement2.classList.add("line")
        this.elements.usrContainer.appendChild(keyElement2);
        keyElement2 = document.createElement("div");
        keyElement2.classList.add("line")
        this.elements.usrContainer.appendChild(keyElement2);
        keyElement2 = document.createElement("div");
        keyElement2.classList.add("line");
        this.elements.usrContainer.appendChild(keyElement2);
        keyElement.appendChild(this.elements.usrContainer);
        this.elements.box.appendChild(keyElement);

        this.elements.main.appendChild(this.elements.box);
        document.getElementById('main').appendChild(this.elements.main);
    }
};
// ----- //
function close_popup() {$('.pop_up').remove();}