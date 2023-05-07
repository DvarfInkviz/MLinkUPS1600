#!/usr/bin/ python3
import smbus
import os
import serial
import time
from datetime import datetime
import sqlite3
from flask import Flask, render_template, request, redirect, flash, url_for, session
# import subprocess
from apscheduler.schedulers.background import BackgroundScheduler


def lcd_init():
    # Initialise display
    lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
    lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
    lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
    lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
    time.sleep(E_DELAY)


def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = the data
    # mode = 1 for data
    #        0 for command
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT
    # High bits
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)
    # Low bits
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)


def lcd_toggle_enable(bits):
    # Toggle enable
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(E_PULSE)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(E_DELAY)


def lcd_string(message, line):
    # Send string to display
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)
    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)


def to_human_log(session_val=None, msg=''):
    if session_val is None:
        session_val = {'ip_address': 'localhost', 'login': 'server-kan-b-brf'}
    if not os.path.isfile(f"/var/www/web-ups1600/logs/human_{datetime.now().strftime('%d%m%Y')}.log"):
        with open(f"/var/www/web-ups1600/logs/human_{datetime.now().strftime('%d%m%Y')}.log", 'w', encoding='utf-8') \
                as _file:
            _file.write(f"human log starts {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n-=-=-=-=-=-=-\n")
            _file.write(datetime.now().strftime("%d%m%Y %H:%M:%S.%s# ") + session_val['ip_address'] + ' # ' +
                        session_val['login'] + ' # ' + msg + '\n')
    else:
        with open(f"/var/www/web-ups1600/logs/human_{datetime.now().strftime('%d%m%Y')}.log", 'a', encoding='utf-8') \
                as _f:
            _f.write(datetime.now().strftime("%d%m%Y %H:%M:%S.%s# ") + session_val['ip_address'] + ' # ' +
                     session_val['login'] + ' # ' + msg + '\n')


def to_log(msg):
    if not os.path.isfile(f"/var/www/web-ups1600/logs/web_{datetime.now().strftime('%d%m%Y')}.log"):
        with open(f"/var/www/web-ups1600/logs/web_{datetime.now().strftime('%d%m%Y')}.log", 'w', encoding='utf-8') \
                as _file:
            _file.write(f"web log starts {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n-=-=-=-=-=-=-\n")
            _file.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S.%s ### ") + msg + '\n')
    else:
        with open(f"/var/www/web-ups1600/logs/web_{datetime.now().strftime('%d%m%Y')}.log", 'a', encoding='utf-8') \
                as _f:
            _f.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S.%s ### ") + msg + '\n')


def to_status_log(msg):
    if not os.path.isfile(f"/var/www/web-ups1600/logs/status_{datetime.now().strftime('%d%m%Y')}.log"):
        with open(f"/var/www/web-ups1600/logs/status_{datetime.now().strftime('%d%m%Y')}.log", 'w',
                  encoding='utf-8') as _file:
            _file.write(f"status log starts {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n-=-=-=-=-=-=-\n")
            _file.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S.%s ### ") + msg + '\n')
    else:
        with open(f"/var/www/web-ups1600/logs/status_{datetime.now().strftime('%d%m%Y')}.log", 'a',
                  encoding='utf-8') as _f:
            _f.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S.%s ### ") + msg + '\n')


def get_db_connection():
    # basedir = os.path.abspath(os.path.dirname(__file__))
    connection = sqlite3.connect("/var/www/web-gost-crypt-2/database.db")
    connection.row_factory = sqlite3.Row
    return connection


def update_temp():
    pass


def adc_stm(state, values):
    lcd_string(f"Read {state} state", LCD_LINE_1)
    lcd_string(f"", LCD_LINE_2)
    time.sleep(1)
    s = serial.Serial(port=serialPort, baudrate=serialBaud, bytesize=dataNumBytes, parity='N', stopbits=1,
                      xonxoff=False, rtscts=False, dsrdtr=False)
    s.reset_input_buffer()  # flush input buffer
    s.reset_output_buffer()
    if state == 'zero':
        s.write(b'Z')
    else:
        s.write(b'C')
    asw = s.readline().decode("utf-8")[:-1].split(sep=' ')
    if (state == 'zero') and (len(asw) == 2):
        values['iakb1_0'] = int(asw[0])*3.6/4095
        values['iakb2_0'] = int(asw[1])*3.6/4095
        lcd_string(f"I0={values['iakb1_0']:.2f} {values['iakb2_0']:.2f}", LCD_LINE_2)
        scheduler.remove_job(job_id='adc_stm')
        time.sleep(2)
        scheduler.add_job(func=adc_stm, args=['current', status_values], trigger='interval',
                          seconds=5, id='adc_stm', replace_existing=True)
    elif (state == 'current') and (len(asw) == 10):
        to_status_log(msg=f"STM => {str(asw)}")
        values['iakb1'] = int(asw[0]) * 3.6 / 4095
        values['iakb2'] = int(asw[1]) * 3.6 / 4095
        values['uakb4'] = int(asw[5]) * 3.6 / 4095
        values['uakb2_4'] = int(asw[9]) * 3.6 / 4095
        lcd_string(f"I={values['iakb1']:.2f} {values['iakb2']:.2f}", LCD_LINE_1)
        lcd_string(f"U={values['uakb4']:.2f} {values['uakb2_4']:.2f}", LCD_LINE_2)
        # scheduler.remove_job(job_id='adc_stm')
    else:
        to_status_log(msg=f"STM => {asw}")
    s.close()


def start_stm():
    # Connect to serial port
    lcd_string("Connect to MCU..", LCD_LINE_2)
    s = serial.Serial(port=serialPort, baudrate=serialBaud, bytesize=dataNumBytes, parity='N', stopbits=1,
                      xonxoff=False, rtscts=False, dsrdtr=False)
    s.reset_input_buffer()  # flush input buffer
    s.reset_output_buffer()
    s.write(b'R')
    asw = s.readline()
    if asw == b"Status code 0x52 received!\n":
        lcd_string("MCU connected!", LCD_LINE_2)
        scheduler.remove_job(job_id='start_stm')
        scheduler.add_job(func=adc_stm, args=['zero', status_values], trigger='interval',
                          seconds=1, id='adc_stm', replace_existing=True)

    else:
        to_status_log(msg=f"STM => {asw}")
    s.close()

scheduler = BackgroundScheduler()
scheduler.start()
temp_time = 1
status_values = {'iakb1_0': 0, 'iakb2_0': 0, 'iakb1': 0, 'iakb2': 0,
                 'uakb1': 0, 'uakb2': 0, 'uakb3': 0, 'uakb4': 0,
                 'uakb2_1': 0, 'uakb2_2': 0, 'uakb2_3': 0, 'uakb2_4': 0}
app = Flask(__name__)
app.config['SECRET_KEY'] = 'xtkjdtxrb;bkbljkuj'
application = app
time.sleep(2)
serialPort = '/dev/ttyS1'
serialBaud = 115200
dataNumBytes = 8

# Initialise display
# Define some device parameters
I2C_ADDR = 0x27  # I2C device address
LCD_WIDTH = 16  # Maximum characters per line

# Define some device constants
LCD_CHR = 1  # Mode - Sending data
LCD_CMD = 0  # Mode - Sending command
LCD_SETCGRAMADDR = 0x40
LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

LCD_BACKLIGHT = 0x08  # On
# LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100  # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Open I2C interface
bus = smbus.SMBus(0)

to_log(f'!!!!!!!!App starts at {datetime.now()}')
lcd_init()
lcd_string("MLink - UPS 1600", LCD_LINE_1)
lcd_string("Inicialization..", LCD_LINE_2)

if scheduler.get_job(job_id='start_stm') is None:
    scheduler.add_job(func=start_stm, trigger='interval', seconds=1, id='start_stm', replace_existing=True)


@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    if request.method == 'POST':
        try:
            json_data = request.get_json()
            to_log(f'=> {json_data}')
            if json_data['action'] == 'submit':
                conn = get_db_connection()
                user = json_data['login']
                passwd = conn.execute('SELECT password FROM users WHERE login =?', (user,)).fetchone()
                conn.close()
                to_log(f'User <{user}> is trying to login')
                if passwd:
                    session['ip_address'] = request.remote_addr
                    session['login'] = user
                    if user == 'sadmin':
                        to_log(f'User <{user}> login into system menu!')
                        return {
                            'connection': 'on',
                            'pwd': str(passwd[0]),
                            'url': 'system',
                        }
                    else:
                        to_log(f'User <{user}> login into main menu! hash={str(passwd[0])}')
                        return {
                            'connection': 'on',
                            'pwd': str(passwd[0]),
                            'url': 'index',
                        }
                else:
                    to_log(f'NOUSER <{user}> in DB!')
                    return redirect(url_for('login'))
            if json_data['action'] == 'submit_ok':
                conn = get_db_connection()
                user = session['login']
                session['priority'] = conn.execute('SELECT priority FROM users WHERE login =?', (user,)).fetchone()[0]
                to_log(f'Password for <{user}> is valid')
                conn.execute('UPDATE users SET logining = ?, log_in = 1, ip = ? WHERE login = ?',
                             (datetime.now().strftime("%d-%m-%Y %H:%M:%S"), request.remote_addr, user,))
                conn.commit()
                conn.close()
                return {
                    'connection': 'on',
                }
        except Exception as e:
            flash(str(e), "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    if 'login' in session:
        conn = get_db_connection()
        _login = session.get('login', None)
        conn.execute('UPDATE users SET log_in = 0 WHERE login = ?',
                     (_login,))
        conn.commit()
        session.clear()
        to_log(f'User <{_login}> logout!')
    return redirect(url_for('login'))


@app.route("/", methods=("GET", "POST"), strict_slashes=False)
@app.route("/index", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        json_data = request.get_json()
        to_log(f'=> {json_data}')
        if json_data['action'] == 'validate':
            conn = get_db_connection()
            ip_client = conn.execute('SELECT ip FROM users WHERE login =?', (session['login'],)).fetchone()
            _login = conn.execute('SELECT log_in FROM users WHERE login =?', (session['login'],)).fetchone()
            conn.close()
            # logging.info(f'### /index-> {ip_client[0]}({_login[0]}) <-> {request.remote_addr}')
            if (ip_client[0] != request.remote_addr) and _login[0]:
                return {
                    'status': 'logout',
                }
            else:
                return {
                    'status': 'ok',
                    'browser': request.user_agent.string,
                }
        if json_data['action'] == 'start':
            # conn = get_db_connection()
            # priority = conn.execute('SELECT priority FROM users WHERE login =?', (_login,)).fetchone()
            # conn.close()
            # _cid = read_cid()
            _cid = 'FF034678'
            return {
                'connection': 'on',
                # 'login': _login,
                # 'priority': priority[0],
                'version': 'web_m.0.2, v.0.6',
                'cid': _cid,
            }
        if json_data['action'] == 'update_service':
            conn = get_db_connection()
            conn.execute('UPDATE pids SET service = ?, video1 = ?, audio1 = ?, audio2 = ? WHERE id = ?',
                         (json_data['service'], json_data['video1'], json_data['audio1'], json_data['audio2'],
                          json_data['id'][2:],))
            conn.commit()
            conn.close()
            return {
                'status': 'reload',
            }
        if json_data['action'] == 'new_service':
            conn = get_db_connection()
            conn.execute("INSERT INTO pids (service, video1, audio1, audio2) "
                         "VALUES (?,?,?,?)", (json_data['service'], json_data['video1'],
                                              json_data['audio1'], json_data['audio2'])
                         )
            conn.commit()
            conn.close()
            return {
                'status': 'reload',
            }
        if json_data['action'] == 'get_service':
            db = []
            conn = get_db_connection()
            srvs = conn.execute('SELECT * FROM pids').fetchall()
            for srv in srvs:
                db.append(
                    [srv[0], srv[1], srv[2], srv[3], srv[4], ])
            conn.close()
            return {
                'connection': 'on',
                'service': db,
                'ip_client': request.remote_addr,
            }
        if json_data['action'] == 'delete_service':
            conn = get_db_connection()
            conn.execute('DELETE FROM pids WHERE id = ?',
                         (json_data['id'],))
            conn.commit()
            conn.close()
            return {
                'status': 'delete ok',
            }
        if json_data['action'] == 'send_cmd':
            conn = get_db_connection()
            if json_data['db_id'][-1] == '1':
                conn.execute('UPDATE pids SET video1 = ? WHERE id = ?',
                             (json_data['pid'], int(json_data['db_id'][:-1]),))
            if json_data['db_id'][-1] == '2':
                conn.execute('UPDATE pids SET audio1 = ? WHERE id = ?',
                             (json_data['pid'], int(json_data['db_id'][:-1]),))
            if json_data['db_id'][-1] == '3':
                conn.execute('UPDATE pids SET audio2 = ? WHERE id = ?',
                             (json_data['pid'], int(json_data['db_id'][:-1]),))
            conn.commit()
            conn.close()
            return {
                'status': json_data['command'],
            }
        if json_data['action'] == 'send_data':
            return {
                'status': json_data['data'],
            }
        if json_data['action'] == 'send_allow':
            return {
                'status': json_data['ids'],
            }
        if json_data['action'] == 'init':
            return {
                'status': 'init done',
            }
        if json_data['action'] == 'send_denied':
            return {
                'status': json_data['ids'],
            }

    return render_template("index.html")
    # if 'login' in session:
    #     _login = session['login']
    # else:
    #     return redirect(url_for('login'))


@app.route("/system", methods=["GET", "POST"])
# @login_required
def system():
    if 'login' in session:
        if request.method == "POST":
            json_data = request.get_json()
            to_log(f'=> {json_data}')
            db = []
            if json_data['action'] == 'validate':
                conn = get_db_connection()
                ip_client = conn.execute('SELECT ip FROM users WHERE login =?', (session['login'],)).fetchone()
                conn.close()
                if ip_client[0] != request.remote_addr:
                    return {
                        'status': 'logout',
                    }
                else:
                    return {
                        'status': 'ok',
                        'browser': request.user_agent.string,
                    }
            if json_data['action'] == 'delete_user':
                if json_data['id'] > 2:
                    conn = get_db_connection()
                    conn.execute('DELETE FROM users WHERE id = ?',
                                 (json_data['id'],))
                    conn.commit()
                    conn.close()
                    return {
                        'status': 'delete ok',
                    }
                else:
                    return {
                        'status': 'permission denied',
                    }
            if json_data['action'] == 'update_pwd':
                conn = get_db_connection()
                conn.execute('UPDATE users SET password = ? WHERE id = ?',
                             (json_data['password'], json_data['id'],))
                conn.commit()
                conn.close()
                if json_data['id'] == 1:
                    return {
                        'status': 'logout',
                    }
                else:
                    return {
                        'status': 'ok',
                    }
            if json_data['action'] == 'update_user':
                conn = get_db_connection()
                conn.execute('UPDATE users SET login = ?, fullname = ?, job_title = ?, priority = ? WHERE id = ?',
                             (json_data['login'], json_data['fullname'], json_data['job'], json_data['priority'],
                              json_data['id'][2:],))
                conn.commit()
                conn.close()
                return {
                    'status': 'reload',
                }
            if json_data['action'] == 'new_user':
                conn = get_db_connection()
                conn.execute("INSERT INTO users (created, login, password, fullname, job_title, priority) "
                             "VALUES (?,?,?,?,?,?)",
                             (datetime.now().strftime("%d-%m-%Y %H:%M:%S"), json_data['login'],
                              json_data['password'], json_data['fullname'],
                              json_data['job'], json_data['priority'])
                             )
                conn.commit()
                conn.close()
                return {
                    'status': 'reload',
                }
            if json_data['action'] == 'start':
                conn = get_db_connection()
                users = conn.execute('SELECT * FROM users').fetchall()
                for user in users:
                    db.append([user[5], user[3], user[6], user[1], user[2], user[11], user[7], user[10], user[0], ])
                conn.close()
                return {
                    'connection': 'on',
                    'users': db,
                    'ip_client': request.remote_addr,
                }
        return render_template("system.html")
    else:
        return redirect(url_for('login'))
