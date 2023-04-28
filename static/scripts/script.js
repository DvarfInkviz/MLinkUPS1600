window.addEventListener(`resize`, event => {
  if (document.documentElement.clientWidth <= 1200){
    document.getElementById('table_top').width = "100%";
//    if (document.documentElement.clientHeight > document.documentElement.clientWidth) {
//        document.getElementById('table_top').height = document.documentElement.clientWidth;
//    }
//    else {
//        document.getElementById('table_top').height = document.documentElement.clientWidth;
//    }
  }
  else {
    document.getElementById('table_top').width = "60%";
    document.getElementById('table_top').height = document.documentElement.clientWidth;
  }
}, false);

document.addEventListener('DOMContentLoaded', () => {
                  setInterval(request_register, 800);
              });
              function request_register() {
                    fetch('/engineer', {
                        headers : {
                            'Content-Type' : 'application/json'
                        },
                        method : 'POST',
                        body : JSON.stringify( {
                            'register_status' : '0000000000000000',
                            'register_errors' : '0000000000000000'
                        })
                    })
                    .then(function (response){
                        if(response.ok) {
                            response.json()
                            .then(function(response) {
                                if (response.connection === 'on') {
                                    var ava = document.querySelector('[src="static/off.png"]');
                                    if (ava) {
                                        ava.setAttribute('src','static/on.png');
                                    }
                                    document.getElementById('position_az').value = response.position_az;
                                    document.getElementById('position_el').value = response.position_el;
                                    document.getElementById('position_pl').value = response.position_pl;
                                    document.getElementById('freq').value = response.frequency;
                                    let reg_st = 'st_'
                                    for (var i = 0; i < response.register_status.length; i++) {
                                        if (response.register_status[i] === '1') {
                                            if (document.getElementById(reg_st + i)) {
                                                if (i === 15) {
                                                    document.getElementById(reg_st + i).style.background = 'red';
                                                }
                                                else {
                                                    document.getElementById(reg_st + i).style.background = 'green';
                                                }
                                            }
                                        }
                                        else {
                                            if (document.getElementById(reg_st + i)) {
                                                document.getElementById(reg_st + i).style.background = '#e3ffec';
                                            }
                                        }
                                    }
                                    let reg_ersw = 'ersw_'
                                    for (var i = 0; i < response.register_errorsw.length; i++) {
                                        if (response.register_status[i] === '1') {
                                            if (document.getElementById(reg_ersw + i)) {
                                                document.getElementById(reg_ersw + i).style.background = 'red';
                                            }
                                        }
                                        else {
                                            if (document.getElementById(reg_ersw + i)) {
                                                document.getElementById(reg_ersw + i).style.background = '#e3ffec';
                                            }
                                        }
                                    }
                                    let reg_erhw = 'erhw_'
                                    for (var i = 0; i < response.register_errorhw.length; i++) {
                                        if (response.register_status[i] === '1') {
                                            if (document.getElementById(reg_erhw + i)) {
                                                document.getElementById(reg_erhw + i).style.background = 'red';
                                            }
                                        }
                                        else {
                                            if (document.getElementById(reg_erhw + i)) {
                                                document.getElementById(reg_erhw + i).style.background = '#e3ffec';
                                            }
                                        }
                                    }
                                }
                                else {
                                    var ava = document.querySelector('[src="static/on.png"]');
                                    if (ava) {
                                        ava.setAttribute('src','static/off.png');
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
