import configparser
import os
import sys

SEC_SMA = 'sma'

ITEM_SHO = 'short'
ITEM_MID = 'middle'
ITEM_LON = 'long'

_INI_FILE = 'config.ini'

_config_def = {
    ITEM_SHO: '5',
    ITEM_MID: '20',
    ITEM_LON: '75'
}
_cfg = configparser.ConfigParser(_config_def)

_config = {}
_config[SEC_SMA] = _config_def

if not os.path.exists(_INI_FILE):
    sys.stderr.write("{}ファイルがありません。初期値を設定します。" .format(_INI_FILE))


def read():
    _cfg.read(_INI_FILE)
    if not _cfg.has_section(SEC_SMA):
        _cfg.add_section(SEC_SMA)
    _config[SEC_SMA][ITEM_SHO] = _cfg.getint(SEC_SMA, ITEM_SHO)
    _config[SEC_SMA][ITEM_MID] = _cfg.getint(SEC_SMA, ITEM_MID)
    _config[SEC_SMA][ITEM_LON] = _cfg.getint(SEC_SMA, ITEM_LON)


def write():
    if not _cfg.has_section(SEC_SMA):
        _cfg.add_section(SEC_SMA)
    _cfg.set(SEC_SMA, ITEM_SHO, str(_config[SEC_SMA][ITEM_SHO]))
    _cfg.set(SEC_SMA, ITEM_MID, str(_config[SEC_SMA][ITEM_MID]))
    _cfg.set(SEC_SMA, ITEM_LON, str(_config[SEC_SMA][ITEM_LON]))
    with open(_INI_FILE, 'w') as f:
        _cfg.write(f)


def set_conf(sec, item, value):
    _config[sec][item] = value


def get_conf(sec, item):
    return _config[sec][item]


if __name__ == "__main__":
    print("start")
    print("read")
    read()
    print(_config)
    set_conf(SEC_SMA, ITEM_SHO, 3)
    set_conf(SEC_SMA, ITEM_MID, 15)
    set_conf(SEC_SMA, ITEM_LON, 60)
    print(_config)
    print("write")
    write()
