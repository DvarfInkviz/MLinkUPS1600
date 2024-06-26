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
from w1thermsensor import W1ThermSensor, SensorNotReadyError, NoSensorFoundError
# import subprocess
from apscheduler.schedulers.background import BackgroundScheduler
from stm32loader.main import main


def lcd_init():
    # Initialise display
    _e = False
    try:
        lcd_byte(0x30, LCD_CMD)  # 110000 Initialise
    except BlockingIOError as _err:
        to_human_log(msg='Сбой инициализации экрана')
        to_log(msg=f'Сбой инициализации экрана - {_err}')
        _e = False
    else:
        lcd_byte(0x02, LCD_CMD)  # 000010 Initialise
        # lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
        # lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
        lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
        lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
        lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
        lcd_byte(LCD_LINE_1, LCD_CMD)  # 10000000 переход на 1 строку
        time.sleep(E_DELAY)
        _e = True
    finally:
        return _e


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
    if lcd_error:
        # Send string to display
        message = message.ljust(LCD_WIDTH, " ")
        lcd_byte(line, LCD_CMD)
        for i in range(LCD_WIDTH):
            lcd_byte(ord(message[i]), LCD_CHR)


def to_human_log(session_val=None, msg=''):
    if session_val is None:
        session_val = {'ip_address': 'localhost', 'login': 'server-kan-b-brf'}
    if not os.path.isfile(f"/var/www/{PROJECT_NAME}/logs/human_{datetime.now().strftime('%d%m%Y')}.log"):
        with open(f"/var/www/{PROJECT_NAME}/logs/human_{datetime.now().strftime('%d%m%Y')}.log", 'w',
                  encoding='utf-8') as _file:
            _file.write(f"human log starts {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n-=-=-=-=-=-=-\n")
            _file.write(datetime.now().strftime("%d%m%Y %H:%M:%S.%s# ") + msg + '\n')
    else:
        with open(f"/var/www/{PROJECT_NAME}/logs/human_{datetime.now().strftime('%d%m%Y')}.log", 'a',
                  encoding='utf-8') as _f:
            _f.write(datetime.now().strftime("%d%m%Y %H:%M:%S.%s# ") + msg + '\n')


def to_log(msg):
    if not os.path.isfile(f"/var/www/{PROJECT_NAME}/logs/web_{datetime.now().strftime('%d%m%Y')}.log"):
        with open(f"/var/www/{PROJECT_NAME}/logs/web_{datetime.now().strftime('%d%m%Y')}.log", 'w', encoding='utf-8') \
                as _file:
            _file.write(f"web log starts {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n-=-=-=-=-=-=-\n")
            _file.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S.%s ### ") + msg + '\n')
    else:
        with open(f"/var/www/{PROJECT_NAME}/logs/web_{datetime.now().strftime('%d%m%Y')}.log", 'a', encoding='utf-8') \
                as _f:
            _f.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S.%s ### ") + msg + '\n')


def to_status_log(msg):
    if not os.path.isfile(f"/var/www/{PROJECT_NAME}/logs/status_{datetime.now().strftime('%d%m%Y')}.log"):
        with open(f"/var/www/{PROJECT_NAME}/logs/status_{datetime.now().strftime('%d%m%Y')}.log", 'w',
                  encoding='utf-8') as _file:
            _file.write(f"status log starts {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n-=-=-=-=-=-=-\n")
            _file.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S.%s ### ") + msg + '\n')
    else:
        with open(f"/var/www/{PROJECT_NAME}/logs/status_{datetime.now().strftime('%d%m%Y')}.log", 'a',
                  encoding='utf-8') as _f:
            _f.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S.%s ### ") + msg + '\n')


def get_db_connection():
    # basedir = os.path.abspath(os.path.dirname(__file__))
    connection = sqlite3.connect(f"/var/www/{PROJECT_NAME}/database.db")
    connection.row_factory = sqlite3.Row
    return connection


def update_temp(values):
    global cnt1_error
    global cnt2_error
    try:
        values['temp1'] = values['w1temp'][0].get_temperature()
        values['menu_3_1'] = f'Q={values["i_charge_max"] * 10:5} Ah;T={values["temp1"]:5.1f} C'
        cnt1_error = 0
    except IndexError as _err:
        values['temp1'] = -1
        to_status_log(msg=f'Temp1_error: {_err}')
        values['menu_3_1'] = f'Q={values["i_charge_max"] * 10:5} Ah;T= n/a C'
        if cnt1_error < 3:
            to_human_log(msg='Датчик температуры на АКБ не подключен!')
            cnt1_error += 1
    except SensorNotReadyError:
        values['menu_3_1'] = f'Q={values["i_charge_max"] * 10:5} Ah;T= n/a C'
        values['temp1'] = -1
        to_status_log(msg=f'Temp1_error: is not ready to read')
        if cnt1_error < 3:
            to_human_log(msg='Датчик температуры на АКБ не готов к чтению!')
            cnt1_error += 1
    except NoSensorFoundError:
        values['menu_3_1'] = f'Q={values["i_charge_max"] * 10:5} Ah;T= n/a C'
        values['temp1'] = -1
        to_status_log(msg=f'Temp1_error: Could not find sensor of type DS18B20')
        if cnt1_error < 3:
            to_human_log(msg='Датчик температуры на АКБ вышел из строя!')
            cnt1_error += 1
    try:
        values['temp2'] = values['w1temp'][1].get_temperature()
        cnt2_error = 0
    except IndexError as _err:
        to_status_log(msg=f'Temp2_error: {_err}')
        values['temp2'] = -1
        if cnt2_error < 3:
            to_human_log(msg='Датчик температуры в шкафу не подключен!')
            cnt2_error += 1
    except SensorNotReadyError:
        to_status_log(msg=f'Temp2_error: is not ready to read')
        values['temp2'] = -1
        if cnt2_error < 3:
            to_human_log(msg='Датчик температуры в шкафу не готов к чтению!')
            cnt2_error += 1
    except NoSensorFoundError:
        to_status_log(msg=f'Temp2_error: Could not find sensor of type DS18B20')
        values['temp2'] = -1
        if cnt2_error < 3:
            to_human_log(msg='Датчик температуры в шкафу вышел из строя!')
            cnt2_error += 1
    if values['temp1'] == -1 or values['temp2'] == -1:
        status_values['w1temp'] = W1ThermSensor.get_available_sensors()
        for _i in range(0, len(status_values['w1temp'])):
            status_values[f'temp{_i + 1}_id'] = status_values['w1temp'][_i].id
            status_values[f'temp{_i + 1}'] = status_values['w1temp'][_i].get_temperature()


def get_error_status(cur, old):
    if cur > 0 and not cur == old:
        try:
            to_human_log(msg=err_dict[cur])
        except KeyError as _err:
            to_status_log(msg=f'KeyError: {_err}')
    return cur


def get_state_status(old, cur, err, st):
    if err == 0 and not cur == old:
        try:
            to_human_log(msg=status_dict[st][cur])
        except KeyError as _err:
            to_status_log(msg=f'KeyError: {_err}')
        if cur == 194:
            status_values['start_charge'] = datetime.now()
        if cur == 196:
            status_values['t_charge_mode'] = datetime.now() - status_values['start_charge']
    return cur


def get_inv_error(err, _id):
    _error = f'{err:08b}'[::-1]
    if _error[0] == '1':
        to_human_log(msg=f'Общий отказа {_id}-го БВ')
    if _error[1] == '1':
        to_human_log(msg=f'Отказ вентилятора {_id}-го БВ')
    if _error[2] == '1':
        to_human_log(msg=f'Перенапряжение на выходе {_id}-го БВ DC')
    if _error[3] == '1':
        to_human_log(msg=f'Недонапряжение на выходе {_id}-го БВ DC')
    if _error[4] == '1':
        to_human_log(msg=f'Перегрев {_id}-го БВ')
    if _error[5] == '1':
        to_human_log(msg=f'Недонапряжение на входе {_id}-го БВ АС')
    if _error[6] == '1':
        to_human_log(msg=f'Перегрузка {_id}-го БВ')
    if _error[7] == '1':
        to_human_log(msg=f'Перенапряжение на входе {_id}-го БВ АС')
    return err


def reset_stm32():
    global stm_reset
    try:
        stm_reset = digitalio.DigitalInOut(board.pin.PC3)
        stm_reset.direction = digitalio.Direction.OUTPUT
        stm_reset.value = False
        stm_boot = digitalio.DigitalInOut(board.pin.PG8)
        stm_boot.direction = digitalio.Direction.OUTPUT
        stm_boot.value = False
        stm_reset.value = True
        time.sleep(1)
        stm_reset.value = False
    except OSError as _err:
        # to_human_log(msg='Сбой инициализации ARM')
        to_log(msg=f'Сбой инициализации boot, reset STM pins - {_err}')


def get_stm_status(values):
    s = serial.Serial(port=serialPort, baudrate=serialBaud, bytesize=dataNumBytes, parity='N', stopbits=1,
                      xonxoff=False, rtscts=False, dsrdtr=False, timeout=5)
    # to_status_log(msg=f"open port {s.name}")
    if not s.is_open:
        s.open()
    s.reset_input_buffer()  # flush input buffer
    s.reset_output_buffer()
    cnt_m = 10  # количество значений для усреднения
    _m = 0
    _m_list = [{}, {}, {}, {}, {}, {}]
    _first = True
    _sync = False
    while s.is_open:
        sync_byte = 0
        while not _sync:
            _one_byte = list(s.read())
            to_log(msg=f"000 sync... {sync_byte} > read: {_one_byte}")
            if len(_one_byte) >= 0:
                sync_byte += 1 if _one_byte[0] == 27 else 0
            else:
                reset_stm32()
            _sync = True if sync_byte == 3 else False
        len_buf = 51 if sync_byte == 3 else 54
        rs_buf = s.read(size=len_buf)
        in_buf = list(rs_buf)[3:] if len_buf == 54 else list(rs_buf)
        to_log(msg=f"111 IN_DATA >> {str(list(rs_buf))}")
        _u_akb4 = 0
        if len(in_buf) == 51:
            values['stm'] = 'ok'
            to_status_log(msg=f"-=-From STM-=-\nErr:{str(in_buf[:2])},"
                              f"Status:{str(in_buf[2])},"
                              f"ADC:{str(in_buf[3:20])},"
                              f"U_akb_max_pc:{str(in_buf[20])},"
                              f"pcs1:{str(in_buf[21:29])},"
                              f"pcs2:{str(in_buf[29:37])},"
                              f"pcs3:{str(in_buf[37:45])},"
                              f"state:{str(in_buf[45])},"
                              f"U_bv:{str(in_buf[46:48])},"
                              f"Rele_in:{str(in_buf[48])},"
                              f"Rele_out:{str(in_buf[49])},"
                              f"ver.:{str(in_buf[50])}")
            values['version'] = f'arm.{in_buf[50] // 10}.{in_buf[50] % 10}'
            values['menu_0_7'] = f"Version:;{values['version']} {MCU_VERSION}"
            values['err'] = get_error_status(cur=in_buf[1], old=values['err'])
            values['menu_0_1'] = f'{datetime.now().strftime("%H:%M %d.%m.%Y")};Error code:{values["err"]:5}'
            values['iakb1'] = (in_buf[4] * 256 + in_buf[5] - IAKB1_0) / values['k_i_akb']
            # values['uakb1'] = (in_buf[7] * 256 + in_buf[8]) * 3.3 / 4096 * 20 * K_U1
            # values['uakb2'] = (in_buf[10] * 256 + in_buf[11]) * 3.3 / 4096 * 20 * K_U2
            # values['uakb3'] = (in_buf[13] * 256 + in_buf[14]) * 3.3 / 4096 * 20 * K_U3
            # values['uakb4'] = (in_buf[16] * 256 + in_buf[17]) * 3.3 / 4096 * 20 * K_U4
            values['uakb1'] = (in_buf[7] * 256 + in_buf[8]) * 3.3 / 4096 * 20 * K_U1
            values['uakb2'] = (in_buf[10] * 256 + in_buf[11]) * 3.3 / 4096 * 20 * K_U2 - values['uakb1']
            values['uakb3'] = (in_buf[13] * 256 + in_buf[14]) * 3.3 / 4096 * 20 * K_U3 - values['uakb2'] - \
                              values['uakb1']
            if values['uakb1'] == values['uakb2'] == values['uakb3'] == 0:
                values['uakb4'] = 0
            else:
                values['uakb4'] = (in_buf[16] * 256 + in_buf[17]) * 3.3 / 4096 * 20 * values['k_u_akb'] - \
                                  values['uakb3'] - values['uakb2'] - values['uakb1']
            _u_akb4 = (in_buf[16] * 256 + in_buf[17]) * 3.3 / 4096 * 20 * values['k_u_akb']
            # values['uakb4_0'] = in_buf[22] * 256 + in_buf[23]
            # 21 - F1
            values['iinv1'] = (in_buf[23] * 256 + in_buf[22]) / 10
            values['ua'] = in_buf[25] * 256 + in_buf[24]
            values['tinv1'] = in_buf[26]
            values['einv1'] = get_inv_error(err=in_buf[27], _id=1)
            # 29 - F2
            values['iinv2'] = (in_buf[31] * 256 + in_buf[30]) / 10
            values['ub'] = in_buf[33] * 256 + in_buf[32]
            values['tinv2'] = in_buf[34]
            values['einv2'] = get_inv_error(err=in_buf[35], _id=2)
            # 37 - F3
            values['iinv3'] = (in_buf[39] * 256 + in_buf[38]) / 10
            values['uc'] = in_buf[41] * 256 + in_buf[40]
            values['tinv3'] = in_buf[42]
            values['einv3'] = get_inv_error(err=in_buf[43], _id=3)
            values['iload'] = values['iinv1'] + values['iinv2'] + values['iinv3'] + values['iakb1']
            values['state'] = in_buf[45]
            values['status'] = get_state_status(cur=in_buf[2], old=values['status'], err=values['err'],
                                                st=values['state'])
            values['u_bv'] = (in_buf[46] * 256 + in_buf[47]) / 80
            values['rele_in'] = f'{in_buf[48]:04b}'[::-1]
            values['rele_out'] = f'{in_buf[49]:04b}'[::-1]
            if _first:
                if _m < cnt_m - 1:
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
            if values['iload'] < 0.5:
                values['iload'] = 0
            if values['state'] == 0 and values['status'] == 196 and values['iakb1'] < 0:
                values['iakb1'] = 0
            values['uload'] = values['uakb1'] + values['uakb2'] + values['uakb3'] + values['uakb4']
            if values['uakb4'] < 0:
                values['uakb4'] = 0
            values['menu_2_0'] = f'I1={values["iinv1"]} I2={values["iinv2"]};I3={values["iinv3"]}'
            values['menu_2_1'] = f'UA={values["ua"]} UB={values["ub"]};UC={values["uc"]}'
            values['menu_3_0'] = f'U1={values["uakb1"]:.1f} U2={values["uakb2"]:.1f};U3={values["uakb3"]:.1f} ' \
                                 f'U4={values["uakb4"]:.1f}'
            values['menu_3_1'] = f'Q={values["i_charge_max"] * 10:5} Ah;T={values["temp1"]:5.1f} C'
            if values['temp1'] > 20:
                values['discharge_abc'] = u_akb_dict[40][100 - values['discharge_depth']]
                values['discharge_akb'] = u_akb_dict[40][30]
                values['u_akb_max'] = u_akb_dict[40][100]
            else:
                values['discharge_abc'] = u_akb_dict[0][100 - values['discharge_depth']]
                values['discharge_akb'] = u_akb_dict[0][30]
                values['u_akb_max'] = u_akb_dict[0][100]
            _temp2 = 0 if values['temp2'] < 0 else values['temp2']
            try:
                if int(abs((values['u_akb_max'] * 4 - _u_akb4) * 10)) > 255:
                    s_out = bytearray.fromhex(format(int(15000804), '06x') +
                                              format(int(float(values['discharge_abc']) * 10), '02x') +
                                              format(int(float(values['discharge_akb']) * 10), '02x') +
                                              format(int(float(values['i_load_max'])), '02x') +
                                              format(int(float(values['u_akb_max']) * 10), '02x') +
                                              format(int(float(values['u_abc_max'])), '02x') +
                                              format(int(float(values['i_charge_max'])), '02x') +
                                              format(int(float(values['k_u_akb']) * 1000), '04x') +
                                              format(int(float(values['k_i_akb']) * 10), '04x') +
                                              format(int(float(values['t_delay']) / 10), '02x') +
                                              format(int(float(_temp2)), '02x') +
                                              format(int(float(values['max_temp_air'])), '02x') +
                                              format(int(abs(values['iakb1'] * 10)), '04x') +
                                              format(int(255), '02x') +
                                              format(int(abs(values['uload'] * 10)), '04x') +
                                              format(int(IAKB1_0), '04x')
                                              )
                else:
                    s_out = bytearray.fromhex(format(int(15000804), '06x') +
                                              format(int(float(values['discharge_abc']) * 10), '02x') +
                                              format(int(float(values['discharge_akb']) * 10), '02x') +
                                              format(int(float(values['i_load_max'])), '02x') +
                                              format(int(float(values['u_akb_max']) * 10), '02x') +
                                              format(int(float(values['u_abc_max'])), '02x') +
                                              format(int(float(values['i_charge_max'])), '02x') +
                                              format(int(float(values['k_u_akb']) * 1000), '04x') +
                                              format(int(float(values['k_i_akb']) * 10), '04x') +
                                              format(int(float(values['t_delay']) / 10), '02x') +
                                              format(int(float(_temp2)), '02x') +
                                              format(int(float(values['max_temp_air'])), '02x') +
                                              format(int(abs(values['iakb1'] * 10)), '04x') +
                                              format(int(abs((values['u_akb_max'] * 4 - _u_akb4) * 10)), '02x') +
                                              format(int(abs(values['uload'] * 10)), '04x') +
                                              format(int(IAKB1_0), '04x')
                                              )
            except ValueError as _err:
                to_status_log(msg=f"ValueError: {_err}; {values['discharge_abc']}, {values['discharge_akb']}, "
                                  f"{values['i_load_max']}, {values['u_akb_max']}, {values['u_abc_max']},"
                                  f"{values['i_charge_max']}, {values['k_u_akb']}, {values['k_i_akb']},"
                                  f"{values['t_delay']}, {values['temp2']}, {values['max_temp_air']},"
                                  f"{values['iakb1']}, {values['u_akb_max'] * 4 - _u_akb4}, {values['uload']}")
            else:
                to_status_log(msg=f"-=-To STM-=-\n{str(list(s_out))}")
                to_log(msg=f"222 {str(list(s_out))}")
                s.write(s_out)
            finally:
                to_log(f"333 U_akb_max={in_buf[20]}; "
                       f"Uakb4={(in_buf[16] * 256 + in_buf[17]) * 3.3 / 4096 * 20 * values['k_u_akb']:.1f}; "
                       f"d_uakb={in_buf[18] / 10:.1f}; u_load_abc={(in_buf[46] * 256 + in_buf[47]) / 80:.1f}; "
                       f"d_iakb={in_buf[19] / 10:.1f}; E0_{format(in_buf[1], '02x').upper()}; "
                       f"{hex(in_buf[2])[2:].upper()}")
        else:
            to_status_log(msg=f"{str(in_buf)}")
            to_human_log(msg="Модуль прибора ARM не отвечает!")
            values['stm'] = 'error'
            s_out = bytearray.fromhex(format(int(15000804), '06x') +
                                      format(int(0), '02x') +
                                      format(int(0), '02x') +
                                      format(int(0), '02x') +
                                      format(int(0), '02x') +
                                      format(int(0), '02x') +
                                      format(int(0), '02x') +
                                      format(int(0), '04x') +
                                      format(int(0), '04x') +
                                      format(int(0), '02x') +
                                      format(int(0), '02x') +
                                      format(int(0), '02x') +
                                      format(int(0), '04x') +
                                      format(int(0), '02x') +
                                      format(int(0), '04x') +
                                      format(int(0), '04x')
                                      )
            s.write(s_out)

    # s.close()


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
                if values["submenu"] == 0 and values["i_load_max"] < 80:
                    values["i_load_max"] += 1
                    values['menu_4_0'] = f'I load max:;{values["i_load_max"]:15}A'
                if values["submenu"] == 1 and values["i_charge_max"] < 20:
                    values["i_charge_max"] += 1
                    values['menu_4_1'] = f'Capacity:;{values["i_charge_max"] * 10:14}Ah'
                    values['menu_3_1'] = f'Q={values["i_charge_max"] * 10:5} Ah;T={values["temp1"]:5.1f} C'
                if values["submenu"] == 2 and values["discharge_depth"] < 70:
                    values["discharge_depth"] += 10
                    values['menu_4_2'] = f'Discharge depth:;{values["discharge_depth"]:15}%'
                if values["submenu"] == 3 and values["u_abc_max"] < 55:
                    values["u_abc_max"] += 1
                    values['menu_4_3'] = f'U load w/o AKB:;{values["u_abc_max"]:15}V'
                if values["submenu"] == 4 and values["max_temp_air"] < 60:
                    values["max_temp_air"] += 1
                    values['menu_4_4'] = f'Max temperature:;{values["max_temp_air"]:15}C'
            elif values["submenu"] < values[f"sub_cnt{values['menu']}"]:
                values["submenu"] = values["submenu"] + 1
            if values["menu"] == 0 and values["submenu"] == 6:
                with open(f"/home/microlink/uptime", 'r', encoding='utf-8') as _f:
                    up_time = int(_f.readline()) / 3600
                with open(f"/home/microlink/up_cur", 'r') as _file:
                    up_time += int(_file.readline().split(sep='.')[0]) / 3600
                    values['menu_0_6'] = f'Operating up;time {up_time:10.1f}h'
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
                if values["submenu"] == 0 and values["i_load_max"] > 20:
                    values["i_load_max"] -= 1
                    values['menu_4_0'] = f'I load max:;{values["i_load_max"]:15}A'
                if values["submenu"] == 1 and values["i_charge_max"] > 4:
                    values["i_charge_max"] -= 1
                    values['menu_4_1'] = f'Capacity:;{values["i_charge_max"] * 10:14}Ah'
                    values['menu_3_1'] = f'Q={values["i_charge_max"] * 10:5} Ah;T={values["temp1"]:5.1f} C'
                if values["submenu"] == 2 and values["discharge_depth"] > 30:
                    values["discharge_depth"] -= 10
                    values['menu_4_2'] = f'Discharge depth:;{values["discharge_depth"]:15}%'
                if values["submenu"] == 3 and values["u_abc_max"] > 44:
                    values["u_abc_max"] -= 1
                    values['menu_4_3'] = f'U load w/o AKB:;{values["u_abc_max"]:15}V'
                if values["submenu"] == 4 and values["max_temp_air"] > 30:
                    values["max_temp_air"] -= 1
                    values['menu_4_4'] = f'Max temperature:;{values["max_temp_air"]:15}C'
            elif values["submenu"] > 0:
                values["submenu"] = values["submenu"] - 1
            if values["menu"] == values["submenu"] == 0:
                values['menu_0_0'] = f'M-Link UPS 1600;{datetime.now().strftime("%H:%M %d.%m.%Y")}'
            if values["menu"] == 0 and values["submenu"] == 6:
                with open(f"/home/microlink/uptime", 'r', encoding='utf-8') as _f:
                    up_time = int(_f.readline()) / 3600
                with open(f"/home/microlink/up_cur", 'r') as _file:
                    up_time += int(_file.readline().split(sep='.')[0]) / 3600
                    values['menu_0_6'] = f'Operating up;time {up_time:10.1f}h'
            lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[0], LCD_LINE_1)
            lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[1], LCD_LINE_2)
            if values['edit']:
                lcd_byte(LCD_LINE_2, LCD_CMD)  # переход на 2 строку
                lcd_byte(0x0F, LCD_CMD)  # 001111 мигающий курсор
            to_status_log(msg=f'Left: {values["menu"]} - {values["submenu"]} - {values["edit"]}')
            counter0 = counter
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
                    _conn = get_db_connection()
                    if values['submenu'] == 0:
                        _conn.execute('UPDATE ups_settings SET i_load_max = ? WHERE id =1',
                                      (str(values["i_load_max"]),))
                        to_human_log(msg=f'LCD: Уставку "Максимальный ток нагрузки – ток отсечки" изменили '
                                         f' на {values["i_load_max"]}A')
                    if values['submenu'] == 1:
                        _conn.execute('UPDATE ups_settings SET i_charge_max = ? WHERE id =1',
                                      (str(values["i_charge_max"]),))
                        to_human_log(msg=f'LCD: Уставку "Емкость АКБ" изменили на {values["i_charge_max"] * 10} Ah')
                    if values['submenu'] == 2:
                        _conn.execute('UPDATE ups_settings SET discharge_depth = ? WHERE id =1',
                                      (str(values["discharge_depth"]),))
                        to_human_log(msg=f'LCD: Уставку "Глубина разряда АКБ при наличии входного напряжения" изменили '
                                         f'на {values["discharge_depth"]}%')
                    if values['submenu'] == 3:
                        _conn.execute('UPDATE ups_settings SET u_abc_max = ? WHERE id =1', (str(values["u_abc_max"]),))
                        to_human_log(msg=f'LCD: Уставку "Напряжение на выходе ИБП в случае работы без АКБ" изменили '
                                         f'на {values["u_abc_max"]}B')
                    if values['submenu'] == 4:
                        _conn.execute('UPDATE ups_settings SET max_temp_air = ? WHERE id =1',
                                      (str(values["max_temp_air"]),))
                        to_human_log(msg=f'LCD: Уставку "Максимальная температура в шкафу" изменили '
                                         f'на {values["max_temp_air"]}°С')
                    _conn.commit()
                    _conn.close()
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
                if values['menu'] == 0 and 1 < values['submenu'] < 5:
                    values['menu'] = values['submenu']
                    values['submenu'] = 0
                    lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[0], LCD_LINE_1)
                    lcd_string(values[f'menu_{values["menu"]}_{values["submenu"]}'].split(sep=';')[1], LCD_LINE_2)
                to_status_log(msg=f'Btn press: {values["menu"]} - {values["submenu"]} - {values["edit"]}')
            #         мигающий курсор
            push = 0
        time.sleep(0.005)


def lcd_time(values):
    values['menu_0_0'] = f'U={status_values["uload"]:.1f}V I={status_values["iload"]:.2f}A;' \
                         f'{datetime.now().strftime("%H:%M %d.%m.%Y")}'
    if values["menu"] == values["submenu"] == 0:
        lcd_string(values[f'menu_0_0'].split(sep=';')[0], LCD_LINE_1)
        lcd_string(values[f'menu_0_0'].split(sep=';')[1], LCD_LINE_2)


def get_bv_status(u_bv, values):
    if int(values['uabc_min']) < u_bv < int(values['uabc_max']):
        return 'ok'
    elif u_bv < int(values['u_abc_alarm_min']) or u_bv > int(values['u_abc_alarm_max']):
        return 'error'
    elif (int(values['u_abc_alarm_min']) < u_bv < int(values['uabc_min'])) or \
            (int(values['uabc_max']) < u_bv < int(values['u_abc_alarm_max'])):
        return 'alarm'


PROJECT_NAME = 'web-ups1600'
MCU_VERSION = 'mcu.1.15'
K_U1 = 0.969  # 1.278
K_U2 = 0.923  # 1.208
K_U3 = 0.916  # 1.189
K_U4 = 0.909  # 1.016
K_I1 = 16.2
IAKB1_0 = 1877
START_CURL_SH = ["/usr/bin/python3 /home/microlink/STM_loader.py &> /home/microlink/stdout_file.txt\n",
                 "IPV4=$(/bin/sed -n '1{p;q;}' /home/microlink/ip_cur)\n",
                 "MASKV4=$(/bin/sed -n '2{p;q;}' /home/microlink/ip_cur)\n",
                 "GATEV4=$(/bin/sed -n '3{p;q;}' /home/microlink/ip_cur)\n",
                 "/bin/sed -i '0,/address.*/s//address '$IPV4'/; s/netmask.*/netmask '$MASKV4'/; s/gateway.*/gateway "
                 "'$GATEV4'/' /etc/network/interfaces\n",
                 "/bin/sed -i 's/ServerName.*/ServerName '$IPV4'/' /etc/apache2/sites-available/web-ups1600.conf\n",
                 "/bin/sed -i 's/nameserver.*/nameserver '$GATEV4'/' /etc/resolv.conf\n",
                 "sleep 1\n",
                 "service networking restart\n",
                 "sleep 5\n",
                 "/sbin/ethtool -s end0 speed 100 duplex full autoneg off\n",
                 "sleep 5\n",
                 "curl $IPV4\n",
                 "sleep 2\n",
                 "curl $IPV4\n"]
scheduler = BackgroundScheduler()
scheduler.start()
temp_time = 1
cnt1_error = 0
cnt2_error = 0
with open("/etc/network/interfaces", 'r', encoding='utf-8') as _file:
    _d = _file.readlines()
    mac = _d[-1].split(sep=' ')[-1][:-1]
if not os.path.isfile(f"/home/microlink/uptime"):
    with open(f"/home/microlink/uptime", 'w', encoding='utf-8') as _file:
        _file.write('0')
    up_time = 0
else:
    with open(f"/home/microlink/uptime", 'r', encoding='utf-8') as _f:
        all_time = int(_f.readline())
    if os.path.isfile(f"/home/microlink/up_cur"):
        with open(f"/home/microlink/up_cur", 'r') as _file:
            try:
                all_time += int(_file.readline().split(sep='.')[0])
            except Exception as error:
                to_status_log(msg=f"Error in file 'up_cur' ({Exception})")
    with open(f"/home/microlink/uptime", 'w', encoding='utf-8') as _f:
        _f.write(str(all_time))
    up_time = all_time / 3600
conn = get_db_connection()
ups_set = conn.execute('SELECT * FROM ups_settings WHERE id =1').fetchone()
u_akb_dict = {0: {30: 13, 40: 13.1, 50: 13.2, 60: 13.3, 70: 13.4, 80: 13.4, 90: 13.5, 100: 13.6},
              40: {30: 13.2, 40: 13.3, 50: 13.4, 60: 13.5, 70: 13.6, 80: 13.6, 90: 13.7, 100: 13.8}}
err_dict = {4: 'Критическая ошибка - датчик тока вышел из строя!',
            8: 'Ошибка - напряжение на фазах вне диапазона!',
            16: 'Критическая ошибка - напряжение на АКБ вне диапазона!',
            32: 'Критическая ошибка - перегрузка по напряжению!',
            64: 'Критическая ошибка - перегрузка по току!',
            128: 'Критическая ошибка - перегрев АКБ!'}
status_dict = {0: {196: 'Работа от АКБ - разряд АКБ'},
               1: {193: 'Работа от сети без АКБ'},
               2: {194: 'Буферный режим - заряд АКБ', 196: 'Буферный режим - разряд АКБ'}}
status_values = {'iakb1': 0, 'uakb1': 0, 'uakb2': 0, 'uakb3': 0, 'uakb4': 0, 'uakb4_0': 0, 'uload': 0,
                 'bat': 100, 't_bat': 2, 'iload': 0, 'tinv1': 0, 'tinv2': 0, 'tinv3': 0, 'einv1': 0, 'einv2': 0,
                 'einv3': 0, 'iinv1': 0, 'iinv2': 0, 'iinv3': 0, 'ua': 0, 'ub': 0, 'uc': 0, 'w1temp': [],
                 'temp1': 0, 'temp1_id': '', 'temp2': 0, 'temp2_id': '', 'uabc_min': 180, 'uabc_max': 240,
                 'u_abc_alarm_min': 120, 'u_abc_alarm_max': 260, 'u_akb_max': u_akb_dict[40][100],
                 'i_load_max': int(ups_set[2]), 't_charge_max': ups_set[3], 'discharge_abc': ups_set[4],
                 'discharge_akb': int(ups_set[5]), 't_delay': int(ups_set[6]), 'i_charge_max': int(ups_set[7]),
                 'u_abc_max': int(ups_set[8]), 'state': -1, 'err': 0, 'status': 0,
                 't_charge_mode': 0, 'start_charge': datetime.now(),
                 'u_load_max': 0, 'u_bv': 0, 'i_max_stm': 0, 'k_u_akb': K_U4, 'k_i_akb': K_I1, 'menu': 0, 'submenu': 0,
                 'edit': False, 'rele_in': '0000', 'rele_out': '0000',
                 'menu_0_0': f'M-Link UPS 1600;{datetime.now().strftime("%H:%M %d.%m.%Y")}', 'sub_cnt0': 7,
                 'menu_0_1': f'{datetime.now().strftime("%H:%M %d.%m.%Y")};Error code:    0', 'sub_cnt1': 0,
                 'menu_0_2': 'Inverter      >>; ', 'sub_cnt2': 1,
                 'menu_0_3': 'Battery       >>; ', 'sub_cnt3': 1,
                 'menu_0_4': 'Settings      >>; ', 'sub_cnt4': 4,
                 'menu_0_5': 'IP address:; ', 'sub_cnt5': 0,
                 'menu_0_6': f'Operating up;time {up_time:10.1f}h', 'discharge_depth': int(ups_set[9]), 'sub_cnt6': 0,
                 'menu_0_7': f'Version:;arm.--, {MCU_VERSION}',
                 'menu_0_8': f'Update process..;Step 1 - wait...', 'sub_cnt7': 0,
                 'max_temp_air': int(ups_set[10]), 'ip_addr': '192.168.1.10', 'ip_mask': '255.255.255.0',
                 'ip_gate': '192.168.1.1', 'version': '0.0', 'stm': 'error'}

# u_load_max TEXT DEFAULT '4000',    1
# i_load_max TEXT DEFAULT '90'       2
# t_charge_max TEXT DEFAULT '20',    3
# discharge_abc TEXT DEFAULT '48',   4
# discharge_akb TEXT DEFAULT '48',   5
# t_delay TEXT DEFAULT '100',        6
# i_charge_max TEXT DEFAULT '10',    7
# u_abc_max TEXT DEFAULT '48'        8
# discharge_depth TEXT DEFAULT '30'  9
# max_temp_air TEXT DEFAULT '60'     10
status_values['menu_2_0'] = f'I1={status_values["iinv1"]} I2={status_values["iinv2"]};I3={status_values["iinv3"]}'
status_values['menu_2_1'] = f'UA={status_values["ua"]} UB={status_values["ub"]};UC={status_values["uc"]}'
status_values['menu_3_0'] = f'U1={status_values["uakb1"]} U2={status_values["uakb2"]};U3={status_values["uakb3"]} ' \
                            f'U4={status_values["uakb4"]}'
status_values['menu_3_1'] = f'Q={status_values["i_charge_max"] * 10:5} Ah;T={status_values["temp1"]:5.1f} C'
status_values['menu_4_0'] = f'I load max:;{status_values["i_load_max"]:15}A'
status_values['menu_4_1'] = f'Capacity:;{status_values["i_charge_max"] * 10:14}Ah'
status_values['menu_4_2'] = f'Discharge depth:;{status_values["discharge_depth"]:15}%'
status_values['menu_4_3'] = f'U load w/o AKB:;{status_values["u_abc_max"]:15}V'
status_values['menu_4_4'] = f'Max temperature:;{status_values["max_temp_air"]:15}C'
with open(f"/etc/network/interfaces", 'r') as _file:
    settings = _file.readlines()
status_values['ip_addr'] = settings[4].split('\n')[0].split(' ')[-1]
status_values['ip_mask'] = settings[5].split('\n')[0].split(' ')[-1]
status_values['ip_gate'] = settings[6].split('\n')[0].split(' ')[-1]
status_values['menu_0_5'] = f"IP address:;{status_values['ip_addr']:>16}"
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
reset_stm32()
to_log(f'!!!!!!!!App starts at {datetime.now()}')
to_status_log(f'!!!!!!!!App starts at {datetime.now()}')
to_human_log(msg=f'Прибор включили, веб-сервис запущен в {datetime.now()}')
lcd_error = lcd_init()
lcd_string(status_values['menu_0_0'].split(sep=';')[0], LCD_LINE_1)
lcd_string(status_values['menu_0_0'].split(sep=';')[1], LCD_LINE_2)
with open(f"/etc/timezone", 'r') as tz_f:
    _time = tz_f.readline()
status_values['tz'] = _time[8:-1]
status_values['w1temp'] = W1ThermSensor.get_available_sensors()
for _i in range(0, len(status_values['w1temp'])):
    status_values[f'temp{_i + 1}_id'] = status_values['w1temp'][_i].id
    status_values[f'temp{_i + 1}'] = status_values['w1temp'][_i].get_temperature()
if scheduler.get_job(job_id='get_stm_status') is None:
    to_status_log(msg='Start working with stm')
    scheduler.add_job(func=get_stm_status, args=[status_values], trigger='interval',
                      seconds=1, id='get_stm_status', replace_existing=True)
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
    scheduler.add_job(func=lcd_time, args=[status_values], id='lcd_time', trigger='interval', seconds=15,
                      replace_existing=True)
else:
    scheduler.remove_job(job_id='lcd_time')
    time.sleep(0.2)
    scheduler.add_job(func=lcd_time, args=[status_values], id='lcd_time', trigger='interval', seconds=15,
                      replace_existing=True)
if scheduler.get_job(job_id='update_temp') is None:
    scheduler.add_job(func=update_temp, args=[status_values], id='update_temp', trigger='interval', seconds=32,
                      replace_existing=True)
else:
    scheduler.remove_job(job_id='update_temp')
    time.sleep(0.2)
    scheduler.add_job(func=update_temp, args=[status_values], id='update_temp', trigger='interval', seconds=32,
                      replace_existing=True)


@app.route("/", methods=("GET", "POST"), strict_slashes=False)
@app.route("/index", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # if 'myFile' in request.files:
        #     to_status_log(msg='%%%%%%% Get file!')
        #     _f_in = request.files['myFile']
        #     _f_in.save(f'/var/www/{PROJECT_NAME}/static/files/upload/stm32.bin')
        #     return {
        #         'connection': 'on',
        #         'file_info': _f_in.filename,
        #     }
        json_data = request.get_json()
        session['ip_address'] = request.remote_addr
        if json_data['action'] == 'start':
            return {
                'connection': 'on',
                'version': f'{status_values["version"]}, {MCU_VERSION}',
            }
        if json_data['action'] == 'status':
            with open(f"/etc/armbianmonitor/datasources/soctemp", 'r') as _file:
                soc_t = int(_file.readline()) / 1000
            with open(f"/proc/uptime", 'r') as up_f:
                with open(f"/home/microlink/up_cur", 'w') as cur_f:
                    cur_f.write(up_f.readline().split(sep=' ')[0])
            _temp1 = "---" if status_values["temp1"] == -1 else f'{status_values["temp1"]:.1f}'
            _temp2 = "---" if status_values["temp2"] == -1 else f'{status_values["temp2"]:.1f}'
            if status_values['stm'] == 'ok':
                return {
                    'connection': 'on',
                    'version': f'{status_values["version"]}, {MCU_VERSION}',
                    'err': status_values['err'],
                    'status': status_values['status'],
                    'bv1_status': get_bv_status(u_bv=status_values['ua'], values=status_values),
                    'bv2_status': get_bv_status(u_bv=status_values['ub'], values=status_values),
                    'bv3_status': get_bv_status(u_bv=status_values['uc'], values=status_values),
                    'dry1_in': int(status_values['rele_in'][0]),
                    'dry2_in': int(status_values['rele_in'][1]),
                    'dry3_in': int(status_values['rele_in'][2]),
                    'dry4_in': int(status_values['rele_in'][3]),
                    'dry1_out': int(status_values['rele_out'][0]),
                    'dry2_out': int(status_values['rele_out'][1]),
                    'dry3_out': int(status_values['rele_out'][2]),
                    'dry4_out': int(status_values['rele_out'][3]),
                    'u_load_max': status_values['u_load_max'],
                    'time_zone': status_values['tz'],
                    'iakb1': f'{status_values["iakb1"]:.2f}',
                    'uakb1': f'{status_values["uakb1"]:.1f}',
                    'uakb2': f'{status_values["uakb2"]:.1f}',
                    'uakb3': f'{status_values["uakb3"]:.1f}',
                    'uakb4': f'{status_values["uakb4"]:.1f}',
                    'iload': f'{status_values["iload"]:.2f}',
                    'uload': f'{status_values["uload"]:.1f}',
                    'ua': f'{status_values["ua"]}',
                    'ub': f'{status_values["ub"]}',
                    'uc': f'{status_values["uc"]}',
                    'state': f'{status_values["state"]}',
                    'u_bv': f'{status_values["u_bv"]:.1f}',
                    'tinv1': f'{status_values["tinv1"]}',
                    'tinv2': f'{status_values["tinv2"]}',
                    'tinv3': f'{status_values["tinv3"]}',
                    'iinv1': f'{status_values["iinv1"]:.1f}',
                    'iinv2': f'{status_values["iinv2"]:.1f}',
                    'iinv3': f'{status_values["iinv3"]:.1f}',
                    'temp_akb': _temp1,
                    'temp_air': _temp2,
                    'temp_cpu': f'{soc_t:.1f}',
                    't_charge_mode': f'{status_values["t_charge_mode"]}'
                }
            else:
                return {
                    'connection': 'on',
                    'version': f'arm.----, {MCU_VERSION}',
                    'err': 666,
                    'status': status_values['status'],
                    'bv1_status': 'no',
                    'bv2_status': 'no',
                    'bv3_status': 'no',
                    'dry1_in': 0,
                    'dry2_in': 0,
                    'dry3_in': 0,
                    'dry4_in': 0,
                    'dry1_out': 0,
                    'dry2_out': 0,
                    'dry3_out': 0,
                    'dry4_out': 0,
                    'u_load_max': status_values['u_load_max'],
                    'time_zone': status_values['tz'],
                    'iakb1': "---",
                    'uakb1': "---",
                    'uakb2': "---",
                    'uakb3': "---",
                    'uakb4': "---",
                    'iload': "---",
                    'uload': "---",
                    'ua': "---",
                    'ub': "---",
                    'uc': "---",
                    'state': f'3',
                    'u_bv': "---",
                    'tinv1': "---",
                    'tinv2': "---",
                    'tinv3': "---",
                    'iinv1': "---",
                    'iinv2': "---",
                    'iinv3': "---",
                    'temp_akb': "---",
                    'temp_air': "---",
                    'temp_cpu': "---",
                    't_charge_mode': f'{status_values["t_charge_mode"]}'
                }
        if json_data['action'] == 'get_journal':
            with open(f"/var/www/{PROJECT_NAME}/logs/human_{datetime.now().strftime('%d%m%Y')}.log", 'r',
                      encoding='utf-8') as _file:
                _data = _file.readlines()
            return {
                'status': 'ok',
                'journal': _data[::-1],
            }
        if json_data['action'] == 'get_settings':
            return {
                'status': 'ok',
                'discharge_depth': status_values['discharge_depth'],
                'q_akb': status_values["i_charge_max"] * 10,
                'u_abc_max': status_values['u_abc_max'],
                'i_load_max': status_values['i_load_max'],
                'max_temp_air': status_values['max_temp_air'],
                'ip_addr': status_values['ip_addr'],
                'ip_mask': status_values['ip_mask'],
                'ip_gate': status_values['ip_gate'],
                'ip_mac': mac,
                'datetime': datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
                'time_zone': status_values['tz'],
            }
        if json_data['action'] == 'updateutc':
            os.system(f"sudo /usr/bin/date -s '{json_data['value'].replace('T', ' ')}' --utc")
            os.system('sudo /usr/sbin/hwclock --systohc -f /dev/rtc1')
            return {
                'status': 'ok',
            }
        if json_data['action'] == 'updatetz':
            os.system(f"sudo /usr/bin/timedatectl set-timezone Etc/GMT-{json_data['value']}")
            os.system('sudo /usr/sbin/hwclock --systohc -f /dev/rtc1')
            status_values['tz'] = json_data['value']
            with open(f"/etc/timezone", 'w') as tz_f:
                tz_f.writelines(f"Etc/GMT-{json_data['value']}\n")
            return {
                'status': 'ok',
            }
        if json_data['action'] == 'reboot':
            if status_values['ip_addr'] != json_data['ipv4']:
                to_human_log(msg=f"Изменили IP адрес на {json_data['ipv4']}")
                status_values['ip_addr'] = json_data['ipv4']
            if status_values['ip_mask'] != json_data['mask4']:
                to_human_log(msg=f"Изменили Маску сети на {json_data['mask4']}")
                status_values['ip_mask'] = json_data['mask4']
            if status_values['ip_gate'] != json_data['gate4']:
                to_human_log(msg=f"Изменили Шлюз на {json_data['gate4']}")
                status_values['ip_gate'] = json_data['gate4']
            with open(f"/home/microlink/ip_cur", 'w') as cur_f:
                cur_f.writelines([f"{status_values['ip_addr']}\n", f"{status_values['ip_mask']}\n",
                                  f"{status_values['ip_gate']}\n"])
            time.sleep(1)
            os.system("sudo /sbin/reboot")
        if json_data['action'] == 'stm32loader':
            if scheduler.get_job(job_id='menu'):
                scheduler.remove_job(job_id='menu')
            time.sleep(2)
            if scheduler.get_job(job_id='press'):
                scheduler.remove_job(job_id='press')
            time.sleep(2)
            if scheduler.get_job(job_id='menu') is None and scheduler.get_job(job_id='press') is None:
                lcd_string(status_values[f'menu_0_8'].split(sep=';')[0], LCD_LINE_1)
                lcd_string(status_values[f'menu_0_8'].split(sep=';')[1], LCD_LINE_2)
                with open(f"/home/microlink/start_curl.sh", 'w') as curl_f:
                    curl_f.writelines(START_CURL_SH)
                time.sleep(1)
                os.system("sudo /sbin/reboot")
        #     https://github.com/florisla/stm32loader/tree/master#electrically
        # if json_data['action'] == 'stm32_work':
        #     stm_boot.value = False
        #     time.sleep(0.5)
        #     stm_reset.value = True
        #     time.sleep(1)
        #     stm_reset.value = False
        #     time.sleep(1)
        #     if scheduler.get_job(job_id='get_stm_status') is None:
        #         to_status_log(msg='Start working with stm')
        #         scheduler.add_job(func=get_stm_status, args=[status_values], trigger='interval',
        #                           seconds=1, id='get_stm_status', replace_existing=True)
        #     to_human_log(msg=f'ARM обновлен, текущая версия {status_values["version"]}')
        #     return {
        #         'status': 'STM_work start!',
        #     }
        if json_data['action'] == 'update':
            if json_data['status_values'] == 'q_akb':
                status_values["i_charge_max"] = int(json_data['value'] / 10)
                to_human_log(msg=f'Web: Уставку "Емкость АКБ" изменили на {status_values["i_charge_max"] * 10} Аh')
                _conn = get_db_connection()
                _conn.execute(f"UPDATE ups_settings SET i_charge_max = ? WHERE id =1",
                              (str(status_values["i_charge_max"]),))
                _conn.commit()
                _conn.close()
            else:
                status_values[json_data['status_values']] = json_data['value']
                _conn = get_db_connection()
                _conn.execute(f"UPDATE ups_settings SET {json_data['status_values']} = ? WHERE id =1",
                              (str(status_values[json_data['status_values']]),))
                _conn.commit()
                _conn.close()
                if json_data['status_values'] == 'discharge_depth':
                    to_human_log(msg=f'Web: Уставку "Глубина разряда АКБ при наличии входного напряжения" изменили '
                                     f'на {status_values[json_data["status_values"]]}%')
                if json_data['status_values'] == 'i_load_max':
                    to_human_log(msg=f'Web: Уставку "Максимальный ток нагрузки – ток отсечки" изменили '
                                     f'на {status_values[json_data["status_values"]]}A')
                if json_data['status_values'] == 'u_abc_max':
                    to_human_log(msg=f'Web: Уставку "Напряжение на выходе ИБП в случае работы без АКБ" изменили '
                                     f'на {status_values[json_data["status_values"]]}B')
                if json_data['status_values'] == 'max_temp_air':
                    to_human_log(msg=f'Web: Уставку "Максимальная температура в шкафу" изменили '
                                     f'на {status_values[json_data["status_values"]]}°С')

            status_values['menu_4_0'] = f'I load max:;{status_values["i_load_max"]:15}A'
            status_values['menu_4_1'] = f'Capacity:;{status_values["i_charge_max"] * 10:14}Ah'
            status_values['menu_4_2'] = f'Discharge depth:;{status_values["discharge_depth"]:15}%'
            status_values['menu_4_3'] = f'U load w/o AKB:;{status_values["u_abc_max"]:15}V'
            status_values['menu_4_4'] = f'Max temperature:;{status_values["max_temp_air"]:15}C'
            return {
                'status': 'update_ok',
            }
        if json_data['action'] == 'update_ip':
            status_values[json_data['status_values']] = json_data['value']
            to_human_log(msg=f"Изменили {json_data['status_values']} на {json_data['value']}")
            with open(f"/home/microlink/ip_cur", 'w') as cur_f:
                cur_f.writelines([f"{status_values['ip_addr']}\n", f"{status_values['ip_mask']}\n",
                                  f"{status_values['ip_gate']}\n"])
    return render_template("index.html")

# sudo /bin/sed -i 's/address.*/address 192.168.1.52/; s/netmask.*/netmask 255.255.255.0/; s/gateway.*/gateway 192.168.1.111/' /etc/network/interfaces
# sudo /bin/sed -i 's/address.*/address 192.168.8.52/; s/netmask.*/netmask 255.255.255.0/; s/gateway.*/gateway 192.168.8.1/' /etc/network/interfaces
# sudo /bin/sed -i 's/ServerName.*/ServerName 192.168.8.52/' /etc/apache2/sites-available/web-ups1600.conf
# sudo /bin/sed -i 's/ServerName.*/ServerName 192.168.1.52/' /etc/apache2/sites-available/web-ups1600.conf
# sudo /bin/sed -i 's/nameserver.*/nameserver 192.168.8.1/' /etc/resolv.conf
# sudo service networking restart
# MYIPV4=$(ip addr show end0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
# cat /etc/armbianmonitor/datasources/soctemp
# sudo date -s "$(curl -s --head http://google.com | grep ^Date: | sed 's/Date: //g')"
