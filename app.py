#!/usr/bin/ python3
import smbus
import digitalio
import board
import os
import serial
import time
from datetime import datetime
import sqlite3
from flask import Flask, render_template, request, redirect, flash, url_for, session
# import subprocess
from apscheduler.schedulers.background import BackgroundScheduler

# TODO:
#   1. create and connect to db
#   2. save settings


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
    connection = sqlite3.connect("/var/www/web-ups1600/database.db")
    connection.row_factory = sqlite3.Row
    return connection


def update_temp():
    pass


def adc_stm(state, values):
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
        values['iakb1_0'] = int(asw[0]) * 3.6 / 4095
        values['iakb2_0'] = int(asw[1]) * 3.6 / 4095
        # lcd_string(f"I0={values['iakb1_0']:.2f} {values['iakb2_0']:.2f}", LCD_LINE_2)
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
        # lcd_string(f"I={values['iakb1']:.2f} {values['iakb2']:.2f}", LCD_LINE_1)
        # lcd_string(f"U={values['uakb4']:.2f} {values['uakb2_4']:.2f}", LCD_LINE_2)
        # scheduler.remove_job(job_id='adc_stm')
    else:
        to_status_log(msg=f"STM => {asw}")
    s.close()


def start_stm():
    s = serial.Serial(port=serialPort, baudrate=serialBaud, bytesize=dataNumBytes, parity='N', stopbits=1,
                      xonxoff=False, rtscts=False, dsrdtr=False)
    s.reset_input_buffer()  # flush input buffer
    s.reset_output_buffer()
    s.write(b'R')
    asw = s.readline()
    if asw == b"Status code 0x52 received!\n":
        scheduler.remove_job(job_id='start_stm')
        scheduler.add_job(func=adc_stm, args=['zero', status_values], trigger='interval',
                          seconds=1, id='adc_stm', replace_existing=True)

    else:
        to_status_log(msg=f"STM => {asw}")
    s.close()


def menu(values):
    clk = digitalio.DigitalInOut(board.pin.PC0)
    clk.direction = digitalio.Direction.INPUT
    dt = digitalio.DigitalInOut(board.pin.PC1)
    dt.direction = digitalio.Direction.INPUT
    # btn = digitalio.DigitalInOut(board.pin.PC2)
    # btn.direction = digitalio.Direction.INPUT

    counter0 = 0
    counter = 0
    clkLastState = clk.value

    while True:
        clkState = clk.value
        dtState = dt.value
        # btn_state = btn.value
        if clkState != clkLastState:
            if dtState != clkState:
                counter += 1
            else:
                counter -= 1
            # print(counter)
        clkLastState = clkState
        if counter - counter0 > 2 and values["submenu"] < values[f"sub_cnt{values['menu']}"]:
            if values["menu"] == 4 and values['edit']:
                if values["submenu"] == 0 and values["i_load_max"] < 90:
                    values["i_load_max"] += 1
                    status_values['menu_4_0'] = f'I load max:;{status_values["i_load_max"]}A'
                if values["submenu"] == 1 and values["u_load_max"] < 56:
                    values["u_load_max"] += 1
                    status_values['menu_4_1'] = f'U load max:;{status_values["u_load_max"]}V'
                if values["submenu"] == 2 and values["discharge_akb"] < 70:
                    values["discharge_akb"] += 10
                    status_values['menu_4_2'] = f'Discharge depth:;{status_values["discharge_akb"]}%'
                if values["submenu"] == 3 and values["tdelay"] < 500:
                    values["tdelay"] += 1
                    status_values['menu_4_3'] = f'Protection time:;{status_values["tdelay"]}ms'
            else:
                values["submenu"] = values["submenu"] + 1
            lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[0], LCD_LINE_1)
            lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[1], LCD_LINE_2)
            # lcd_string(f'{datetime.now().strftime("%H:%M %d.%m.%Y")}', LCD_LINE_1)
            # lcd_string(f'{values["menu"]} - {values["submenu"]} - {btn_state}', LCD_LINE_2)
            to_status_log(msg=f'Right: {values["menu"]} - {values["submenu"]} - {values["edit"]}')
            counter0 = counter
        elif values["submenu"] > 0 and counter - counter0 < -2:
            if values["menu"] == 4 and values['edit']:
                if values["submenu"] == 0 and values["i_load_max"] > 1:
                    values["i_load_max"] -= 1
                    status_values['menu_4_0'] = f'I load max:;{status_values["i_load_max"]}A'
                if values["submenu"] == 1 and values["u_load_max"] > 44:
                    values["u_load_max"] -= 1
                    status_values['menu_4_1'] = f'U load max:;{status_values["u_load_max"]}V'
                if values["submenu"] == 2 and values["discharge_akb"] > 10:
                    values["discharge_akb"] -= 10
                    status_values['menu_4_2'] = f'Discharge depth:;{status_values["discharge_akb"]}%'
                if values["submenu"] == 3 and values["tdelay"] > 1:
                    values["tdelay"] -= 1
                    status_values['menu_4_3'] = f'Protection time:;{status_values["tdelay"]}ms'
            else:
                values["submenu"] = values["submenu"] - 1
            lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[0], LCD_LINE_1)
            lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[1], LCD_LINE_2)
            # lcd_string(f'{datetime.now().strftime("%H:%M %d.%m.%Y")}', LCD_LINE_1)
            # lcd_string(f'{values["menu"]} - {values["submenu"]} - {btn_state}', LCD_LINE_2)
            to_status_log(msg=f'Left: {values["menu"]} - {values["submenu"]} - {values["edit"]}')
            counter0 = counter
        time.sleep(0.01)


def press(values):
    btn = digitalio.DigitalInOut(board.pin.PC2)
    btn.direction = digitalio.Direction.INPUT
    push = 0
    while True:
        if not btn.value:
            push += 1
        else:
            if push > 0:
                to_status_log(msg=f'btn unpress - counter={push}')
            if push > 45:
                if values['edit'] and values['menu'] == 4:
                    values['edit'] = False
                if not values['edit'] and 0 < values['menu']:
                    values['submenu'] = values['menu']
                    values['menu'] = 0
                    lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[0], LCD_LINE_1)
                    lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[1], LCD_LINE_2)
                to_status_log(msg=f'Btn press: {values["menu"]} - {values["submenu"]}')
            elif push > 0:
                if values['menu'] == 4 and not values['edit']:
                    values['edit'] = True
                if values['menu'] == 0 and 0 < values['submenu'] < 6:
                    values['menu'] = values['submenu']
                    values['submenu'] = 0
                    lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[0], LCD_LINE_1)
                    lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[1], LCD_LINE_2)
                to_status_log(msg=f'Btn press: {values["menu"]} - {values["submenu"]}')
            #         мигающий курсор
            push = 0
        time.sleep(0.005)


scheduler = BackgroundScheduler()
scheduler.start()
temp_time = 1
conn = get_db_connection()
ups_set = conn.execute('SELECT * FROM ups_settings WHERE id =1').fetchone()
status_values = {'iakb1_0': 0, 'iakb2_0': 0, 'iakb1': 0, 'iakb2': 0, 'uakb1': 0, 'uakb2': 0, 'uakb3': 0, 'uakb4': 0,
                 'uakb2_1': 0, 'uakb2_2': 0, 'uakb2_3': 0, 'uakb2_4': 0, 'i_inv': 0, 'u_inv': 0, 'bat': 100, 't_bat': 2,
                 'iinv1': 0, 'iinv2': 0, 'iinv3': 0, 'iinv4': 0, 'iinv5': 0, 'iinv6': 0, 'ua': 220, 'ub': 220,
                 'uinv1': 0, 'uinv2': 0, 'uinv3': 0, 'uinv4': 0, 'uinv5': 0, 'uinv6': 0, 'uc': 220, 'Takb': 0,
                 'u_akb_min': ups_set[1], 'u_akb_max': ups_set[2], 'i_akb_min': ups_set[3], 'i_akb_max': ups_set[4],
                 'u_abc_min': ups_set[5], 'u_abc_max': ups_set[6], 'u_abc_alarm_min': ups_set[7],
                 'u_abc_alarm_max': ups_set[8], 'u_load_max': ups_set[9], 'i_load_max': ups_set[10],
                 't_charge_max': ups_set[11], 'discharge_abc': ups_set[12], 'discharge_akb': ups_set[13],
                 't_delay': ups_set[14], 'q_akb': ups_set[15], 'i_charge_max': ups_set[16], 'u_load_abc': ups_set[17],
                 'menu': 0, 'submenu': 0, 'sub_cnt0': 6, 'sub_cnt1': 0, 'sub_cnt2': 4, 'sub_cnt3': 2, 'sub_cnt4': 3,
                 'sub_cnt5': 0, 'edit': False,
                 'menu_0_0': f'M-Link UPS 1600;{datetime.now().strftime("%H:%M %d.%m.%Y")}',
                 'menu_0_1': f'{datetime.now().strftime("%H:%M %d.%m.%Y")};Errors:        0',
                 'menu_0_4': 'Settings; ', 'menu_0_5': 'Logs; ', 'menu_0_6': 'Operating up;time',
                 'menu_1_0': 'Ini error:;empty', 'menu_5_0': f'{datetime.now().strftime("%H:%M %d.%m.%Y")};empty'}
# 1 u_akb_min TEXT DEFAULT '44.0',
# 2 u_akb_max TEXT DEFAULT '58.0',
# 3 i_akb_min TEXT DEFAULT '2730',
# 4 i_akb_max TEXT DEFAULT '2958',
# 5 u_abc_min TEXT DEFAULT '180.0',
# 6 u_abc_max TEXT DEFAULT '240.0',
# 7 u_abc_alarm_min TEXT DEFAULT '120.0',
# 8 u_abc_alarm_max TEXT DEFAULT '260.0',
# 9 u_load_max TEXT DEFAULT '4000',
# 10 i_load_max TEXT DEFAULT '90'
# 11 t_charge_max TEXT DEFAULT '20',
# 12 discharge_abc TEXT DEFAULT '10',
# 13 discharge_akb TEXT DEFAULT '70',
# 14 t_delay TEXT DEFAULT '100',
# 15 q_akb TEXT DEFAULT '200',
# 16 i_charge_max TEXT DEFAULT '20',
# 17 u_load_abc TEXT DEFAULT '48'
status_values['menu_0_2'] = f'Inverter;I={status_values["i_inv"]}A U={status_values["u_inv"]}V'
status_values['menu_0_3'] = f'Battery - {status_values["bat"]}%;t charge - {status_values["t_bat"]}h'
status_values['menu_2_0'] = f'I1={status_values["iinv1"]} I2={status_values["iinv2"]};I3={status_values["iinv3"]}'
status_values['menu_2_1'] = f'U1={status_values["uinv1"]} U2={status_values["uinv2"]};U3={status_values["uinv3"]}'
status_values['menu_2_2'] = f'I4={status_values["iinv4"]} I5={status_values["iinv5"]};I6={status_values["iinv6"]}'
status_values['menu_2_3'] = f'U4={status_values["uinv4"]} U5={status_values["uinv5"]};U6={status_values["uinv6"]}'
status_values['menu_2_4'] = f'UA={status_values["ua"]} UB={status_values["ub"]};UC={status_values["uc"]}'
status_values['menu_3_0'] = f'U1={status_values["uakb1"]} U2={status_values["uakb2"]};U3={status_values["uakb3"]} ' \
                            f'U4={status_values["uakb4"]}'
status_values['menu_3_1'] = f'U5={status_values["uakb2_1"]} U6={status_values["uakb2_2"]};' \
                            f'U7={status_values["uakb2_3"]} U8={status_values["uakb2_4"]}'
status_values['menu_3_2'] = f'Q={status_values["q_akb"]}Ah;T={status_values["Takb"]}'
status_values['menu_4_0'] = f'I load max:;{status_values["i_load_max"]}A'
status_values['menu_4_1'] = f'U load max:;{status_values["u_load_max"]}V'
status_values['menu_4_2'] = f'Discharge depth:;{status_values["discharge_akb"]}%'
status_values['menu_4_3'] = f'Protection time:;{status_values["t_delay"]}ms'

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
lcd_string(status_values['menu_0_0'].split(sep=';')[0], LCD_LINE_1)
lcd_string(status_values['menu_0_0'].split(sep=';')[1], LCD_LINE_2)

if scheduler.get_job(job_id='start_stm') is None:
    scheduler.add_job(func=start_stm, trigger='interval', seconds=1, id='start_stm', replace_existing=True)
time.sleep(1)
scheduler.add_job(func=menu, args=[status_values], id='menu', replace_existing=True)
scheduler.add_job(func=press, args=[status_values], id='press', replace_existing=True)


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
        # if json_data['action'] == 'validate':
        #     conn = get_db_connection()
        #     ip_client = conn.execute('SELECT ip FROM users WHERE login =?', (session['login'],)).fetchone()
        #     _login = conn.execute('SELECT log_in FROM users WHERE login =?', (session['login'],)).fetchone()
        #     conn.close()
        #     # logging.info(f'### /index-> {ip_client[0]}({_login[0]}) <-> {request.remote_addr}')
        #     if (ip_client[0] != request.remote_addr) and _login[0]:
        #         return {
        #             'status': 'logout',
        #         }
        #     else:
        #         return {
        #             'status': 'ok',
        #             'browser': request.user_agent.string,
        #         }
        if json_data['action'] == 'start':
            return {
                'connection': 'on',
                'version': 'arm.0.1, mcu.0.1',
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
