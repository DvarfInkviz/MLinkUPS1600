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
    u_load_max TEXT DEFAULT '55',
    i_load_max TEXT DEFAULT '80',
    t_charge_max TEXT DEFAULT '20',
    discharge_abc TEXT DEFAULT '48',
    discharge_akb TEXT DEFAULT '48',
    t_delay TEXT DEFAULT '100',
    q_akb TEXT DEFAULT '100',
    i_charge_max TEXT DEFAULT '10',
    u_load_abc TEXT DEFAULT '48',
    discharge_depth TEXT DEFAULT '70',
    max_temp_air TEXT DEFAULT '60'
);