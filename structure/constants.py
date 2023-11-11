GAME_TIME = 0
GAME_DARKNESS = 1
GAME_SKY = 2

WEB_REDIRECT = "/pokedungeonds/web"
REDIRECT_START = "/redirect/"
SALT = b'TXqjDDOLhPySKSztgBHY'
RNGMUL = 0x0001bd95
RNGADD = 0x00007d99
RNGMOD = 0x00000200
CHECKMASK = 0x613c4964
GAMENAME = b'pokedungeonds'

PROFILE_RQ = dict()

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
