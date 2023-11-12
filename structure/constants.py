GAME_TIME = 0
GAME_DARKNESS = 1
GAME_SKY = 2

UNIFIED_TABLES = ["globalprofile", "profile", "buddylist"]

SALT = b'TXqjDDOLhPySKSztgBHY'
CHECKMASK = 0x613c4964
BASEGAME = 'pokedungeonds'

TOKENPOOL = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

SERVER_ADDR = "192.168.56.1" # Change this to your server public address

RESOLVER = {
    "conntest.nintendowifi.net": SERVER_ADDR,
    "pokedungeonds.available.gs.nintendowifi.net": SERVER_ADDR,
    "nas.nintendowifi.net": SERVER_ADDR,
    "gpcm.gs.nintendowifi.net": SERVER_ADDR,
    "pokedungeonds.master.gs.nintendowifi.net": SERVER_ADDR,
    "gamestats2.gs.nintendowifi.net": SERVER_ADDR,
}
