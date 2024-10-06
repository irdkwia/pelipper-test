from structure.constants import *
from structure.tools import escape_string

def unificate(langorg, langtarget=None):
    if langorg==0:
        return 0
    elif langtarget is not None:
        return langtarget
    return langorg

def val(b):
    return int.from_bytes(b, 'big')
def dat(n, l):
    return n.to_bytes(l, 'big')
def parse(b, l):
    x = []
    for i in range(0, len(b), l):
        x.append(val(b[i:i+l]))
    return x


class GlobalProfile:
    key = ["gbsr", "userid"]
    def __init__(self):
        self._token = None
        self._challenge = None
        self._gbsr = ""
        self._game = ""
        self.userid = 0
        self.profileid = 0
        self.nick = None
        self.uniquenick = None
        self.email = None
        self.firstname = None
        self.lastname = None
        self.icquin = None
        self.homepage = None
        self.zipcode = None
        self.countrycode = None
        self.lon = None
        self.lat = None
        self.loc = None
        self.birthday = None #YYYY/MM/DD
        self.sex = None #M/F
        self.pmask = None
        self.aim = None
        self.pic = None
        self.occ = None
        self.ind = None
        self.mar = None
        self.chc = None
        self.i1 = None
        self.o1 = None
        self.conn = None
        self.sig = "d41d8cd98f00b204e9800998ecf8427e"

class Profile:
    key = ["pid"]
    
    def __init__(self):
        self.currenthash = None
        self.pid = 0
        self.game = ""
        self.lang = 8
        self.email = ""
        self.flags = 0
        self.team = ""
        self.devname = ""
        self.ccode = 0
        self.scode = 0
        self.unified = 1

class TeamData:
    key = ["pid"]
    def __init__(self):
        self.pid = 0
        self.tid = 0
        self.rank = 0
        self.lang = 8
        self.team = ""
        self.pkmn = bytes(256)
        self.private = 0
        
    def getdata(self, langtarget):
        subbuffer = bytearray(36)
        subbuffer[0:8] = self.tid.to_bytes(8, 'big')
        subbuffer[8:28] = (escape_string(self.team)+'\x00'*(10-len(self.team))).encode("utf-16-le")
        subbuffer[28:32] = self.rank.to_bytes(4, 'big')
        subbuffer[32:36] = unificate(self.lang, langtarget).to_bytes(4, 'big')
        subbuffer += self.pkmn
        return subbuffer
    
class RescueRequest:
    key = ["rid"]
    def __init__(self):
        self.pid = 0
        self.rid = 0
        self.uid = 0
        self.code = 0
        self.seed = 0
        self.dungeon = 0
        self.floor = 0
        self.game = GAME_SKY
        self.lang = 8
        self.team = ""
        self.title = ""
        self.message = ""
        self.completed = 0
        self.requested = 0
        self.private = 0

    def getdata(self, langtarget, entry=0):
        subbuffer = bytearray(200+entry*8)
        subbuffer[0:8] = self.rid.to_bytes(8, 'big')
        subbuffer[8:16] = self.uid.to_bytes(8, 'big')
        subbuffer[32:52] = (escape_string(self.team)+'\x00'*(10-len(self.team))).encode("utf-16-le")
        subbuffer[52:56] = self.dungeon.to_bytes(4, 'big')
        subbuffer[56:60] = self.floor.to_bytes(4, 'big')
        subbuffer[60:64] = self.seed.to_bytes(4, 'big')
        subbuffer[64:68] = self.game.to_bytes(4, 'big')
        subbuffer[68:72] = unificate(self.lang, langtarget).to_bytes(4, 'big')
        subbuffer[72:108] = (escape_string(self.title)+'\x00'*(18-len(self.title))).encode("utf-16-be")
        subbuffer[108:180] = (escape_string(self.message)+'\x00'*(36-len(self.message))).encode("utf-16-be")
        subbuffer[180:188] = (entry).to_bytes(4, 'big')+(entry).to_bytes(4, 'big')
        return subbuffer

class RescueAOK:
    key = ["rid"]
    def __init__(self):
        self.rid = 0
        self.uresp = 0
        self.code = 0
        self.item = bytes(4)
        self.pkmn = bytes(64)
        self.game = GAME_SKY
        self.lang = 8
        self.team = ""
        self.title = ""
        self.message = ""
        self.rescuerpid = 0

    def getdata(self, langtarget):
        subbuffer = bytearray(260)
        subbuffer[0:8] = self.rid.to_bytes(8, 'big')
        subbuffer[8:16] = self.uresp.to_bytes(8, 'big', signed=True)
        subbuffer[32:40] = self.code.to_bytes(8, 'big', signed=True)
        subbuffer[56:76] = (escape_string(self.team)+'\x00'*(10-len(self.team))).encode("utf-16-le")
        subbuffer[76:80] = self.item
        subbuffer[80:144] = self.pkmn
        subbuffer[144:148] = self.game.to_bytes(4, 'big')
        subbuffer[148:152] = unificate(self.lang, langtarget).to_bytes(4, 'big')
        subbuffer[152:188] = (escape_string(self.title)+'\x00'*(18-len(self.title))).encode("utf-16-be")
        subbuffer[188:260] = (escape_string(self.message)+'\x00'*(36-len(self.message))).encode("utf-16-be")
        return subbuffer

class RescueThanks:
    key = ["rid"]
    def __init__(self):
        self.rid = 0
        self.code = 0
        self.item = bytes(4)
        self.title = ""
        self.message = ""
        self.claimed = 0
    
    def getdata(self):
        subbuffer = bytearray(144)
        subbuffer[0:8] = self.rid.to_bytes(8, 'big')
        subbuffer[8:16] = self.code.to_bytes(8, 'big', signed=True)
        subbuffer[32:36] = self.item
        subbuffer[36:72] = (escape_string(self.title)+'\x00'*(18-len(self.title))).encode("utf-16-be")
        subbuffer[72:144] = (escape_string(self.message)+'\x00'*(36-len(self.message))).encode("utf-16-be")
        return subbuffer

class BuddyList:
    key = ["pid", "buddy"]
    def __init__(self):
        self.pid = 0
        self.buddy = 0

class WMGameList:
    key = ["passwd"]
    def __init__(self):
        self.passwd = ""
        self.prefix = ""
        self.lang = ""
        self.version = GAME_SKY

class WMPassList:
    key = ["wid"]
    def __init__(self):
        self.wid = 0
        self.data = bytes(17)
        self.version = GAME_SKY

class DungeonData:
    key = ["did"]
    def __init__(self):
        self.did = 0
        self.name = ""
        self.direction = DIR_DOWN

class ProfileChange:
    key = ["pid"]
    def __init__(self):
        self.pid = 0
        self.team = ""
        self.devname = ""

