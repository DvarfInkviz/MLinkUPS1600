#!/usr/bin/ python3
import logging
import time
from datetime import datetime
import sqlite3
from flask import Flask, render_template, request, redirect, flash, url_for, session
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(
    level=logging.INFO,
    filename="/var/www/web-gost-crypt-2/logs/web.log",
    format="%(asctime)s - %(pathname)s - %(module)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
    # datefmt='%H:%M:%S',
)


def get_db_connection():
    # basedir = os.path.abspath(os.path.dirname(__file__))
    connection = sqlite3.connect("/var/www/web-gost-crypt-2/database.db")
    connection.row_factory = sqlite3.Row
    return connection


logging.info(f'!!!!!!!!App starts at {datetime.now()}')
scheduler = BackgroundScheduler()
scheduler.start()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'xtkjdtxrb;bkbljkuj'
application = app

# application = app


@app.route("/", methods=("GET", "POST"), strict_slashes=False)
@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    if request.method == 'POST':
        try:
            json_data = request.get_json()
            logging.info(f'=> {json_data}')
            if json_data['action'] == 'submit':
                conn = get_db_connection()
                user = json_data['login']
                passwd = conn.execute('SELECT password FROM users WHERE login =?', (user,)).fetchone()
                conn.close()
                logging.warning(f'User <{user}> is trying to login')
                if passwd:
                    session['ip_address'] = request.remote_addr
                    session['login'] = user
                    if user == 'sadmin':
                        logging.critical(f'User <{user}> login into system menu!')
                        return {
                            'connection': 'on',
                            'pwd': str(passwd[0]),
                            'url': 'system',
                        }
                    else:
                        logging.critical(f'User <{user}> login into main menu! hash={str(passwd[0])}')
                        return {
                            'connection': 'on',
                            'pwd': str(passwd[0]),
                            'url': 'index',
                        }
                else:
                    logging.critical(f'NOUSER <{user}> in DB!')
                    return redirect(url_for('login'))
            if json_data['action'] == 'submit_ok':
                conn = get_db_connection()
                user = session['login']
                session['priority'] = conn.execute('SELECT priority FROM users WHERE login =?', (user,)).fetchone()[0]
                logging.warning(f'Password for <{user}> is valid')
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
        logging.warning(f'User <{_login}> logout!')
    return redirect(url_for('login'))


@app.route("/index", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        json_data = request.get_json()
        logging.info(f'=> {json_data}')
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
            logging.info(f'=> {json_data}')
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
