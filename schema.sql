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

DROP TABLE IF EXISTS plc_settings;

CREATE TABLE plc_settings (
    id INTEGER PRIMARY KEY,
    az_max TEXT DEFAULT '360.0',
    az_min TEXT DEFAULT '0.0',
    el_max TEXT DEFAULT '360.0',
    el_min TEXT DEFAULT '0.0',
    pl_max TEXT DEFAULT '180.0',
    pl_min TEXT DEFAULT '-180.0',
    satellite INTEGER DEFAULT 1,
    ss_name TEXT DEFAULT '',
    ss_d TEXT DEFAULT '3.5',
    ss_lat TEXT DEFAULT '55.91',
    ss_lon TEXT DEFAULT '30.25',
    ss_alt TEXT DEFAULT '110',
    mode INTEGER DEFAULT 1
);