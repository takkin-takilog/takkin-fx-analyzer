import configparser
import os
import sys

# アクティベート
ITEM_SMA_ACT = 'sma_act'
ITEM_MACD_ACT = 'macd_act'
ITEM_BB_ACT = 'bb_act'

# 単純移動平均
ITEM_SMA_SHO = 'sma_short'
ITEM_SMA_MID = 'sma_middle'
ITEM_SMA_LON = 'sma_long'
# MACD
ITEM_MACD_SHO = 'macd_short'
ITEM_MACD_LON = 'macd_long'
ITEM_MACD_SIG = 'macd_signal'
# ボリンジャーバンド
ITEM_BB_PRD = 'bb_period'

_INI_FILE = 'config.ini'

_SEC_ACT = 'activate'
_SEC_SMA = 'sma'
_SEC_MACD = 'macd'
_SEC_BB = 'bb'
_SEC_LIST = [_SEC_ACT, _SEC_SMA, _SEC_MACD, _SEC_BB]

_config_def = {
    # アクティベート
    ITEM_SMA_ACT: '0',
    ITEM_MACD_ACT: '0',
    ITEM_BB_ACT: '0',
    # 単純移動平均
    ITEM_SMA_SHO: '5',
    ITEM_SMA_MID: '20',
    ITEM_SMA_LON: '75',
    # MACD
    ITEM_MACD_SHO: '12',
    ITEM_MACD_LON: '26',
    ITEM_MACD_SIG: '9',
    # ボリンジャーバンド
    ITEM_BB_PRD: '20',
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

    # アクティベート
    _config[ITEM_SMA_ACT] = _cfg.getint(_SEC_ACT, ITEM_SMA_ACT)
    _config[ITEM_MACD_ACT] = _cfg.getint(_SEC_ACT, ITEM_MACD_ACT)
    _config[ITEM_BB_ACT] = _cfg.getint(_SEC_ACT, ITEM_BB_ACT)
    # 単純移動平均
    _config[ITEM_SMA_SHO] = _cfg.getint(_SEC_SMA, ITEM_SMA_SHO)
    _config[ITEM_SMA_MID] = _cfg.getint(_SEC_SMA, ITEM_SMA_MID)
    _config[ITEM_SMA_LON] = _cfg.getint(_SEC_SMA, ITEM_SMA_LON)
    # MACD
    _config[ITEM_MACD_SHO] = _cfg.getint(_SEC_MACD, ITEM_MACD_SHO)
    _config[ITEM_MACD_LON] = _cfg.getint(_SEC_MACD, ITEM_MACD_LON)
    _config[ITEM_MACD_SIG] = _cfg.getint(_SEC_MACD, ITEM_MACD_SIG)
    # ボリンジャーバンド
    _config[ITEM_BB_PRD] = _cfg.getint(_SEC_BB, ITEM_BB_PRD)


def write():
    for item in _SEC_LIST:
        if not _cfg.has_section(item):
            _cfg.add_section(item)
    _cfg.set(_SEC_ACT, ITEM_SMA_ACT, str(_config[ITEM_SMA_ACT]))
    _cfg.set(_SEC_ACT, ITEM_MACD_ACT, str(_config[ITEM_MACD_ACT]))
    _cfg.set(_SEC_ACT, ITEM_BB_ACT, str(_config[ITEM_BB_ACT]))
    _cfg.set(_SEC_SMA, ITEM_SMA_SHO, str(_config[ITEM_SMA_SHO]))
    _cfg.set(_SEC_SMA, ITEM_SMA_MID, str(_config[ITEM_SMA_MID]))
    _cfg.set(_SEC_SMA, ITEM_SMA_LON, str(_config[ITEM_SMA_LON]))
    _cfg.set(_SEC_MACD, ITEM_MACD_SHO, str(_config[ITEM_MACD_SHO]))
    _cfg.set(_SEC_MACD, ITEM_MACD_LON, str(_config[ITEM_MACD_LON]))
    _cfg.set(_SEC_MACD, ITEM_MACD_SIG, str(_config[ITEM_MACD_SIG]))
    _cfg.set(_SEC_BB, ITEM_BB_PRD, str(_config[ITEM_BB_PRD]))
    with open(_INI_FILE, 'w') as f:
        _cfg.write(f)


def set_conf(item, value):
    _config[item] = value


def set_conf_act(value):
    if (0 in value):
        _config[ITEM_SMA_ACT] = 1
    else:
        _config[ITEM_SMA_ACT] = 0

    if (1 in value):
        _config[ITEM_MACD_ACT] = 1
    else:
        _config[ITEM_MACD_ACT] = 0

    if (2 in value):
        _config[ITEM_BB_ACT] = 1
    else:
        _config[ITEM_BB_ACT] = 0


def get_conf(item):
    return _config[item]


def get_conf_act():
    list_ = []
    if _config[ITEM_SMA_ACT] == 1:
        list_.append(0)
    if _config[ITEM_MACD_ACT] == 1:
        list_.append(1)
    if _config[ITEM_BB_ACT] == 1:
        list_.append(2)
    return list_


if __name__ == "__main__":
    print("start")
    print("read")
    read()
    print(_config)
    print("1")
    set_conf(ITEM_SMA_SHO, 3)
    set_conf(ITEM_SMA_MID, 15)
    set_conf(ITEM_SMA_LON, 60)
    print("2")
    print(_config)
    print("write")
    write()
