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
from w1thermsensor import W1ThermSensor
# import subprocess
from apscheduler.schedulers.background import BackgroundScheduler


def lcd_init():
    # Initialise display
    lcd_byte(0x30, LCD_CMD)  # 110000 Initialise
    lcd_byte(0x02, LCD_CMD)  # 000010 Initialise
    # lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
    # lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
    lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
    lcd_byte(LCD_LINE_1, LCD_CMD)  # 10000000 переход на 1 строку
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


def update_temp(values):
    values['temp1'] = values['w1temp'][0].get_temperature()
    values['temp2'] = values['w1temp'][1].get_temperature()


def adc_stm(state, values):
    # TODO try-exept for open serial port
    s = serial.Serial(port=serialPort, baudrate=serialBaud, bytesize=dataNumBytes, parity='N', stopbits=1,
                      xonxoff=False, rtscts=False, dsrdtr=False)
    s.reset_input_buffer()  # flush input buffer
    s.reset_output_buffer()
    cnt_m = 50  # количество значений для усреднения
    _m = 0
    _m_list = [{}, {}, {}, {}, {}, {}]
    _first = True
    while True:
        # TODO try-exept for read data
        in_buf = list(s.read(size=33))
        values['iakb1_0'] = in_buf[4] * 256 + in_buf[5]
        values['iakb1'] = in_buf[7] * 256 + in_buf[8] - (in_buf[4] * 256 + in_buf[5])
        values['uakb1'] = (in_buf[10] * 256 + in_buf[11]) * 3.3 / 4096 * 20 * 1.023
        values['uakb2'] = (in_buf[13] * 256 + in_buf[14]) * 3.3 / 4096 * 20 * 1.023
        values['uakb3'] = (in_buf[16] * 256 + in_buf[17]) * 3.3 / 4096 * 20 * 1.023
        values['uakb4'] = (in_buf[19] * 256 + in_buf[20]) * 3.3 / 4096 * 20 * 1.023
        values['iinv1'] = (in_buf[22] * 256 + in_buf[23]) / 10
        values['iinv2'] = (in_buf[26] * 256 + in_buf[27]) / 10
        values['iinv3'] = (in_buf[30] * 256 + in_buf[31]) / 10
        values['uc'] = in_buf[24]
        values['ub'] = in_buf[28]
        values['ua'] = in_buf[32]
        values['iload'] = values['iinv1'] + values['iinv2'] + values['iinv3'] - values['iakb1']
        if _first:
            if _m < cnt_m-1:
                _m_list[0][_m] = values['iakb1']
                for _j in range(1, 5):
                    _m_list[_j][_m] = values[f'uakb{_j}']
                _m_list[5][_m] = values['iload']
                _m += 1
            else:
                _first = False
                _m_list[0][_m] = values['iakb1']
                for _j in range(1, 5):
                    _m_list[_j][_m] = values[f'uakb{_j}']
                _m_list[5][_m] = values['iload']
                _m = 0
                _sum = [0, 0, 0, 0, 0, 0]
                for _i in range(0, cnt_m):
                    for _j in range(0, 6):
                        _sum[_j] += _m_list[_j][_i]
                values['iakb1'] = _sum[0] / cnt_m
                values['uakb1'] = _sum[1] / cnt_m
                values['uakb2'] = _sum[2] / cnt_m
                values['uakb3'] = _sum[3] / cnt_m
                values['uakb4'] = _sum[4] / cnt_m
                values['iload'] = _sum[5] / cnt_m
        else:
            if _m < cnt_m:
                _m_list[0][_m] = values['iakb1']
                for _j in range(1, 5):
                    _m_list[_j][_m] = values[f'uakb{_j}']
                _m_list[5][_m] = values['iload']
                _m += 1
                _sum = [0, 0, 0, 0, 0, 0]
                for _i in range(0, cnt_m):
                    for _j in range(0, 6):
                        _sum[_j] += _m_list[_j][_i]
                values['iakb1'] = _sum[0] / cnt_m
                values['uakb1'] = _sum[1] / cnt_m
                values['uakb2'] = _sum[2] / cnt_m
                values['uakb3'] = _sum[3] / cnt_m
                values['uakb4'] = _sum[4] / cnt_m
                values['iload'] = _sum[5] / cnt_m
            else:
                _m = 0
        stm_out = f"Код ошибки: E0_{hex(in_buf[1])[2:].upper()}, статус код: {hex(in_buf[2])[2:].upper()}, " \
                  f"Iakb1_0 = {values['iakb1_0']}, "\
                  f"Iakb1 = {values['iakb1']:.2f}, "\
                  f"Uakb1 = {values['uakb1']:.2f}, "\
                  f"Uakb2 = {values['uakb2']:.2f}, "\
                  f"Uakb3 = {values['uakb3']:.2f}, "\
                  f"Uakb4 = {values['uakb4']:.2f}, "\
                  f"I1 = {values['iinv1']:.2f}, UC = {values['uc']}, "\
                  f"I2 = {values['iinv2']:.2f}, UB = {values['ub']}, "\
                  f"I3 = {values['iinv3']:.2f}, UA = {values['ua']}"
        to_status_log(msg=f"STM => {stm_out}")
    # s.close()


# def start_stm():
#     s = serial.Serial(port=serialPort, baudrate=serialBaud, bytesize=dataNumBytes, parity='N', stopbits=1,
#                       xonxoff=False, rtscts=False, dsrdtr=False)
#     s.reset_input_buffer()  # flush input buffer
#     s.reset_output_buffer()
#     s.write(b'R')
#     asw = s.readline()
#     if asw == b"Status code 0x52 received!\n":
#         scheduler.remove_job(job_id='start_stm')
#         scheduler.add_job(func=adc_stm, args=['zero', status_values], trigger='interval',
#                           seconds=1, id='adc_stm', replace_existing=True)
#
#     else:
#         to_status_log(msg=f"STM => {asw}")
#     s.close()


def menu(values):
    clk = digitalio.DigitalInOut(board.pin.PC0)
    clk.direction = digitalio.Direction.INPUT
    dt = digitalio.DigitalInOut(board.pin.PC1)
    dt.direction = digitalio.Direction.INPUT

    counter0 = 0
    counter = 0
    clk_last_state = clk.value
    dt_last_state = dt.value

    while True:
        clk_state = clk.value
        dt_state = dt.value
        # if (clk_state != clk_last_state) or (dt_state != dt_last_state):
        #     to_status_log(msg=f'clk: {clk_last_state} -> {clk_state}; dt: {dt_last_state} -> {dt_state}')
        if clk_last_state and dt_last_state and clk_state and not dt_state:
            counter -= 1
        elif clk_last_state and not dt_last_state and not clk_state and not dt_state:
            counter -= 1
        elif not clk_last_state and not dt_last_state and not clk_state and dt_state:
            counter -= 1
        elif not clk_last_state and dt_last_state and clk_state and dt_state:
            counter -= 1
        elif not clk_last_state and not dt_last_state and clk_state and not dt_state:
            counter += 1
        elif clk_last_state and not dt_last_state and clk_state and dt_state:
            counter += 1
        elif clk_last_state and dt_last_state and not clk_state and dt_state:
            counter += 1
        elif not clk_last_state and dt_last_state and not clk_state and not dt_state:
            counter += 1
        clk_last_state = clk_state
        dt_last_state = dt_state
        if counter - counter0 > 2:
            to_status_log(msg=f'RightRotate: {counter0 - counter}')
            if values["menu"] == 4 and values['edit']:
                _conn = get_db_connection()
                if values["submenu"] == 0 and values["i_load_max"] < 90:
                    values["i_load_max"] += 1
                    _conn.execute('UPDATE ups_settings SET i_load_max = ? WHERE id =1', (str(values["i_load_max"]),))
                    status_values['menu_4_0'] = f'I load max:;{status_values["i_load_max"]}A'
                if values["submenu"] == 1 and values["u_load_max"] < 56:
                    values["u_load_max"] += 1
                    _conn.execute('UPDATE ups_settings SET u_load_max = ? WHERE id =1', (str(values["u_load_max"]),))
                    status_values['menu_4_1'] = f'U load max:;{status_values["u_load_max"]}V'
                if values["submenu"] == 2 and values["discharge_akb"] < 70:
                    values["discharge_akb"] += 10
                    _conn.execute('UPDATE ups_settings SET discharge_akb = ? WHERE id =1',
                                  (str(values["discharge_akb"]),))
                    status_values['menu_4_2'] = f'Discharge depth:;{status_values["discharge_akb"]}%'
                if values["submenu"] == 3 and values["t_delay"] < 500:
                    values["t_delay"] += 1
                    _conn.execute('UPDATE ups_settings SET t_delay = ? WHERE id =1', (str(values["t_delay"]),))
                    status_values['menu_4_3'] = f'Protection time:;{status_values["t_delay"]}ms'
                _conn.commit()
                _conn.close()
            elif values["submenu"] < values[f"sub_cnt{values['menu']}"]:
                values["submenu"] = values["submenu"] + 1
            lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[0], LCD_LINE_1)
            lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[1], LCD_LINE_2)
            if values['edit']:
                lcd_byte(LCD_LINE_2, LCD_CMD)  # переход на 2 строку
                lcd_byte(0x0F, LCD_CMD)  # 001111 мигающий курсор
            to_status_log(msg=f'Right: {values["menu"]} - {values["submenu"]} - {values["edit"]}')
            counter0 = counter
        elif counter - counter0 < -2:
            to_status_log(msg=f'LeftRotate: {counter0 - counter}')
            if values["menu"] == 4 and values['edit']:
                _conn = get_db_connection()
                if values["submenu"] == 0 and values["i_load_max"] > 1:
                    values["i_load_max"] -= 1
                    _conn.execute('UPDATE ups_settings SET i_load_max = ? WHERE id =1', (str(values["i_load_max"]),))
                    status_values['menu_4_0'] = f'I load max:;{status_values["i_load_max"]}A'
                if values["submenu"] == 1 and values["u_load_max"] > 44:
                    values["u_load_max"] -= 1
                    _conn.execute('UPDATE ups_settings SET u_load_max = ? WHERE id =1', (str(values["u_load_max"]),))
                    status_values['menu_4_1'] = f'U load max:;{status_values["u_load_max"]}V'
                if values["submenu"] == 2 and values["discharge_akb"] > 10:
                    values["discharge_akb"] -= 10
                    _conn.execute('UPDATE ups_settings SET discharge_akb = ? WHERE id =1',
                                  (str(values["discharge_akb"]),))
                    status_values['menu_4_2'] = f'Discharge depth:;{status_values["discharge_akb"]}%'
                if values["submenu"] == 3 and values["t_delay"] > 1:
                    values["t_delay"] -= 1
                    _conn.execute('UPDATE ups_settings SET t_delay = ? WHERE id =1', (str(values["t_delay"]),))
                    status_values['menu_4_3'] = f'Protection time:;{status_values["t_delay"]}ms'
                _conn.commit()
                _conn.close()
            elif values["submenu"] > 0:
                values["submenu"] = values["submenu"] - 1
            if values["menu"] == values["submenu"] == 0:
                values['menu_0_0'] = f'M-Link UPS 1600;{datetime.now().strftime("%H:%M %d.%m.%Y")}'
            lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[0], LCD_LINE_1)
            lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[1], LCD_LINE_2)
            if values['edit']:
                lcd_byte(LCD_LINE_2, LCD_CMD)  # переход на 2 строку
                lcd_byte(0x0F, LCD_CMD)  # 001111 мигающий курсор
            to_status_log(msg=f'Left: {values["menu"]} - {values["submenu"]} - {values["edit"]}')
            counter0 = counter
        # else:
        #     to_status_log(msg=f'Rotate: {counter0 - counter}')
        time.sleep(0.005)


def press(values):
    btn = digitalio.DigitalInOut(board.pin.PC2)
    btn.direction = digitalio.Direction.INPUT
    push = 0
    while True:
        if not btn.value:
            push += 1
        else:
            if push > 0:
                to_status_log(msg=f'btn unpress - counter={push} - {values["edit"]}')
            if push > 60:
                if values['edit'] and values['menu'] == 4:
                    values['edit'] = False
                    lcd_byte(LCD_LINE_1, LCD_CMD)  # переход на 1 строку
                    lcd_byte(0x0C, LCD_CMD)  # 001100 нормальный режим работы
                if not values['edit'] and 0 < values['menu']:
                    values['submenu'] = values['menu']
                    values['menu'] = 0
                    lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[0], LCD_LINE_1)
                    lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[1], LCD_LINE_2)
                to_status_log(msg=f'Btn press: {values["menu"]} - {values["submenu"]} - {values["edit"]}')
            elif push > 0:
                if values['menu'] == 4 and not values['edit']:
                    values['edit'] = True
                    lcd_byte(LCD_LINE_2, LCD_CMD)  # переход на 2 строку
                    lcd_byte(0x0F, LCD_CMD)  # 001111 мигающий курсор
                if values['menu'] == 0 and 0 < values['submenu'] < 6:
                    values['menu'] = values['submenu']
                    values['submenu'] = 0
                    lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[0], LCD_LINE_1)
                    lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[1], LCD_LINE_2)
                to_status_log(msg=f'Btn press: {values["menu"]} - {values["submenu"]} - {values["edit"]}')
            #         мигающий курсор
            push = 0
        time.sleep(0.005)


def lcd_time(values):
    values['menu_0_0'] = f'M-Link UPS 1600;{datetime.now().strftime("%H:%M %d.%m.%Y")}'
    values['menu_0_1'] = f'{datetime.now().strftime("%H:%M %d.%m.%Y")};Errors:        0'
    values['menu_5_0'] = f'{datetime.now().strftime("%H:%M %d.%m.%Y")};empty'
    if values["menu"] == values["submenu"] == 0:
        lcd_string(values[f'menu_0_0'].split(sep=';')[1], LCD_LINE_2)


scheduler = BackgroundScheduler()
scheduler.start()
temp_time = 1
conn = get_db_connection()
ups_set = conn.execute('SELECT * FROM ups_settings WHERE id =1').fetchone()
status_values = {'iakb1_0': 0, 'iakb1': 0, 'uakb1': 0, 'uakb2': 0, 'uakb3': 0, 'uakb4': 0,
                 'bat': 100, 't_bat': 2, 'iload': 0,
                 'iinv1': 0, 'iinv2': 0, 'iinv3': 0, 'ua': 220, 'ub': 220, 'uc': 220, 'w1temp': [],
                 'temp1': 0, 'temp1_id': '',  # temp akb
                 'temp2': 0, 'temp2_id': '',  # air temp
                 'u_akb_min': ups_set[1], 'u_akb_max': ups_set[2], 'i_akb_min': ups_set[3], 'i_akb_max': ups_set[4],
                 'u_abc_min': ups_set[5], 'u_abc_max': ups_set[6], 'u_abc_alarm_min': ups_set[7],
                 'u_abc_alarm_max': ups_set[8], 'u_load_max': int(ups_set[9]), 'i_load_max': int(ups_set[10]),
                 't_charge_max': ups_set[11], 'discharge_abc': ups_set[12], 'discharge_akb': int(ups_set[13]),
                 't_delay': int(ups_set[14]), 'q_akb': ups_set[15], 'i_charge_max': ups_set[16],
                 'u_load_abc': ups_set[17],
                 'menu': 0, 'submenu': 0, 'sub_cnt0': 6, 'sub_cnt1': 0, 'sub_cnt2': 4, 'sub_cnt3': 2, 'sub_cnt4': 3,
                 'sub_cnt5': 0, 'edit': False,
                 'menu_0_0': f'M-Link UPS 1600;{datetime.now().strftime("%H:%M %d.%m.%Y")}', 'menu_0_2': 'Inverter; ',
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
status_values['menu_0_3'] = f'Battery - {status_values["bat"]}%;t charge - {status_values["t_bat"]}h'
status_values['menu_2_0'] = f'I1={status_values["iinv1"]} I2={status_values["iinv2"]};I3={status_values["iinv3"]}'
status_values['menu_2_1'] = f'UA={status_values["ua"]} UB={status_values["ub"]};UC={status_values["uc"]}'
status_values['menu_3_0'] = f'U1={status_values["uakb1"]} U2={status_values["uakb2"]};U3={status_values["uakb3"]} ' \
                            f'U4={status_values["uakb4"]}'
status_values['menu_3_1'] = f'Q={status_values["q_akb"]}Ah;T={status_values["temp1"]}'
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
# LCD_SETCGRAMADDR = 0x40
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
status_values['w1temp'] = W1ThermSensor.get_available_sensors()
if len(status_values['w1temp']) == 2:
    status_values['temp1_id'] = status_values['w1temp'][0].id
    status_values['temp2_id'] = status_values['w1temp'][1].id
    status_values['temp1'] = status_values['w1temp'][0].get_temperature()
    status_values['temp2'] = status_values['w1temp'][1].get_temperature()
if scheduler.get_job(job_id='adc_stm') is None:
    scheduler.add_job(func=adc_stm, args=['zero', status_values], trigger='interval',
                      seconds=1, id='adc_stm', replace_existing=True)
time.sleep(1)
if scheduler.get_job(job_id='menu') is None:
    scheduler.add_job(func=menu, args=[status_values], id='menu', trigger='interval', seconds=1, coalesce=True,
                      replace_existing=False)
else:
    scheduler.remove_job(job_id='menu')
    time.sleep(0.2)
    scheduler.add_job(func=menu, args=[status_values], id='menu', trigger='interval', seconds=1, coalesce=True,
                      replace_existing=False)
if scheduler.get_job(job_id='press') is None:
    scheduler.add_job(func=press, args=[status_values], id='press', trigger='interval', seconds=1, coalesce=True,
                      replace_existing=False)
else:
    scheduler.remove_job(job_id='press')
    time.sleep(0.2)
    scheduler.add_job(func=press, args=[status_values], id='press', trigger='interval', seconds=1, coalesce=True,
                      replace_existing=False)
if scheduler.get_job(job_id='lcd_time') is None:
    scheduler.add_job(func=lcd_time, args=[status_values], id='lcd_time', trigger='interval', seconds=29,
                      replace_existing=True)
else:
    scheduler.remove_job(job_id='lcd_time')
    time.sleep(0.2)
    scheduler.add_job(func=lcd_time, args=[status_values], id='lcd_time', trigger='interval', seconds=29,
                      replace_existing=True)
if scheduler.get_job(job_id='update_temp') is None:
    scheduler.add_job(func=update_temp, args=[status_values], id='update_temp', trigger='interval', seconds=60,
                      replace_existing=True)
else:
    scheduler.remove_job(job_id='update_temp')
    time.sleep(0.2)
    scheduler.add_job(func=update_temp, args=[status_values], id='update_temp', trigger='interval', seconds=29,
                      replace_existing=True)


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
        if json_data['action'] == 'status':
            return {
                'connection': 'on',
                'u_akb_min': status_values['u_akb_min'],
                'u_akb_max': status_values['u_akb_max'],
                'i_akb_min': status_values['i_akb_min'],
                'i_akb_max': status_values['i_akb_max'],
                'u_abc_min': status_values['u_abc_min'],
                'u_abc_max': status_values['u_abc_max'],
                'u_abc_alarm_min': status_values['u_abc_alarm_min'],
                'u_abc_alarm_max': status_values['u_abc_alarm_max'],
                'u_load_max': status_values['u_load_max'],
                'i_load_max': status_values['i_load_max'],
                't_charge_max': status_values['t_charge_max'],
                'discharge_abc': status_values['discharge_abc'],
                'discharge_akb': status_values['discharge_akb'],
                't_delay': status_values['t_delay'],
                'q_akb': status_values['q_akb'],
                'i_charge_max': status_values['i_charge_max'],
                'u_load_abc': status_values['u_load_abc'],
                'time_zone': 3,
                'iakb1_0': f'{status_values["iakb1_0"]}',
                'iakb1': f'{status_values["iakb1"]:.2f}',
                'uakb1': f'{status_values["uakb1"]:.1f}',
                'uakb2': f'{status_values["uakb2"]:.1f}',
                'uakb3': f'{status_values["uakb3"]:.1f}',
                'uakb4': f'{status_values["uakb4"]:.1f}',
                'iload': f'{status_values["iload"]:.2f}',
                'ua': f'{status_values["ua"]}',
                'ub': f'{status_values["ub"]}',
                'uc': f'{status_values["uc"]}',
                'temp_akb': f'{status_values["temp1"]:.1f}',
                'temp_air': f'{status_values["temp2"]:.1f}'
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
