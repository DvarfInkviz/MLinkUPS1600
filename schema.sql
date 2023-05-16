DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    logining TIMESTAMP DEFAULT '',
    login TEXT NOT NULL,
    password BLOB NOT NULL,
    fullname TEXT DEFAULT '',
    job_title TEXT DEFAULT '',
    priority INTEGER NOT NULL DEFAULT 0,
    permissions TEXT NOT NULL DEFAULT '',
    t_session INTEGER NOT NULL DEFAULT 120,
    log_in INTEGER NOT NULL DEFAULT 0,
    ip TEXT DEFAULT ''
);

DROP TABLE IF EXISTS ups_settings;

CREATE TABLE ups_settings (
    id INTEGER PRIMARY KEY,
    u_akb_min TEXT DEFAULT '44',
    u_akb_max TEXT DEFAULT '58',
    i_akb_min TEXT DEFAULT '2730',
    i_akb_max TEXT DEFAULT '2958',
    u_abc_min TEXT DEFAULT '180',
    u_abc_max TEXT DEFAULT '240',
    u_abc_alarm_min TEXT DEFAULT '120',
    u_abc_alarm_max TEXT DEFAULT '260',
    u_load_max TEXT DEFAULT '4000',
    i_load_max TEXT DEFAULT '90',
    t_charge_max TEXT DEFAULT '20',
    discharge_abc TEXT DEFAULT '10',
    discharge_akb TEXT DEFAULT '70',
    t_delay TEXT DEFAULT '100',
    q_akb TEXT DEFAULT '200',
    i_charge_max TEXT DEFAULT '20',
    u_load_abc TEXT DEFAULT '48'
);