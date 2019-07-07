import configparser
import os
import sys

# アクティベート
ITEM_SMA = 'sma'
ITEM_MACD = 'macd'
ITEM_BB = 'bb'

# 単純移動平均
ITEM_SHO = 'short'
ITEM_MID = 'middle'
ITEM_LON = 'long'

_INI_FILE = 'config.ini'

_SEC_ACT = 'activate'
_SEC_SMA = 'sma'
_SEC_LIST = [_SEC_ACT, _SEC_SMA]

_config_def = {
    # アクティベート
    ITEM_SMA: '0',
    ITEM_MACD: '0',
    ITEM_BB: '0',
    # 単純移動平均
    ITEM_SHO: '5',
    ITEM_MID: '20',
    ITEM_LON: '75'
}
_cfg = configparser.ConfigParser(_config_def)
_config = {}
_config = _config_def

if not os.path.exists(_INI_FILE):
    sys.stderr.write("{}ファイルがありません。初期値を設定します。" .format(_INI_FILE))


def read():
    _cfg.read(_INI_FILE)
    for item in _SEC_LIST:
        if not _cfg.has_section(item):
            _cfg.add_section(item)

    _config[ITEM_SMA] = _cfg.getint(_SEC_ACT, ITEM_SMA)
    _config[ITEM_MACD] = _cfg.getint(_SEC_ACT, ITEM_MACD)
    _config[ITEM_BB] = _cfg.getint(_SEC_ACT, ITEM_BB)
    _config[ITEM_SHO] = _cfg.getint(_SEC_SMA, ITEM_SHO)
    _config[ITEM_MID] = _cfg.getint(_SEC_SMA, ITEM_MID)
    _config[ITEM_LON] = _cfg.getint(_SEC_SMA, ITEM_LON)


def write():
    for item in _SEC_LIST:
        if not _cfg.has_section(item):
            _cfg.add_section(item)
    _cfg.set(_SEC_ACT, ITEM_SMA, str(_config[ITEM_SMA]))
    _cfg.set(_SEC_ACT, ITEM_MACD, str(_config[ITEM_MACD]))
    _cfg.set(_SEC_ACT, ITEM_BB, str(_config[ITEM_BB]))
    _cfg.set(_SEC_SMA, ITEM_SHO, str(_config[ITEM_SHO]))
    _cfg.set(_SEC_SMA, ITEM_MID, str(_config[ITEM_MID]))
    _cfg.set(_SEC_SMA, ITEM_LON, str(_config[ITEM_LON]))
    with open(_INI_FILE, 'w') as f:
        _cfg.write(f)


def set_conf(item, value):
    _config[item] = value


def set_conf_act(value):
    if (0 in value):
        _config[ITEM_SMA] = 1
    else:
        _config[ITEM_SMA] = 0

    if (1 in value):
        _config[ITEM_MACD] = 1
    else:
        _config[ITEM_MACD] = 0

    if (2 in value):
        _config[ITEM_BB] = 1
    else:
        _config[ITEM_BB] = 0


def get_conf(item):
    return _config[item]


def get_conf_act():
    list_ = []
    if _config[ITEM_SMA] == 1:
        list_.append(0)
    if _config[ITEM_MACD] == 1:
        list_.append(1)
    if _config[ITEM_BB] == 1:
        list_.append(2)
    return list_


if __name__ == "__main__":
    print("start")
    print("read")
    read()
    print(_config)
    print("1")
    set_conf(ITEM_SHO, 3)
    set_conf(ITEM_MID, 15)
    set_conf(ITEM_LON, 60)
    print("2")
    print(_config)
    print("write")
    write()
