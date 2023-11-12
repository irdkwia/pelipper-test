from http.server import BaseHTTPRequestHandler
from random import randrange, choice
from base64 import b64decode, b64encode
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import time
from hashlib import sha1

from structure.database import *

TEMP_CHANGE = dict()

CAPTURE = False

class CustomHandler(BaseHTTPRequestHandler):
    def conndigest(self, data, out=False):
        return sha1(SALT+data+(SALT if out else b'')).hexdigest()
    
    def attributes(self):
        self.server_version = "LFL/0.1"

    def upgrade11(self):
        self.protocol_version = "HTTP/1.1"
    
    def parse_form(self):
        length = int(self.headers.get('content-length'))
        denc = parse_qs(self.rfile.read(length).decode("ascii"))
        data = dict()
        for k, v in denc.items():
            s = b64decode(v[0].translate(str.maketrans({'-': '+', '_': '/', '*': '='})))
            if k in ["devname", "ingamesn"]:
                data[k] = s.decode("utf-16")
            else:
                data[k] = s.decode("ascii")
        return data

    def send_form(self, data, headers=dict()):
        buffer = bytearray()
        for k, v in data.items():
            if len(buffer)>0:
                buffer += b'&'
            if isinstance(v, str):
                v = v.encode("ascii")
            buffer += k.encode("ascii")+b'='+b64encode(v).decode("ascii").translate(str.maketrans({'+': '-', '/': '_', '=': '*'})).encode("ascii")
        self.send_response(200)
        self.send_header("Content-Type", "application/x-www-form-urlencoded")
        self.send_header("Content-Length", str(len(buffer)))
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(buffer)
        
    def do_GET(self):
        self.attributes()
        psplit = urlparse(self.path)
        if psplit.path=="/":
            buffer = b'<html><body></body></html>'
            self.send_response(200)
            self.end_headers()
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(buffer)))
            self.wfile.write(buffer)
            return
        sid = psplit.path.find("/", 1)
        if sid!=-1 and psplit.path[sid:].startswith("/web"):
            self.upgrade11()
            hackname = psplit.path[1:sid]
            if hackname==BASEGAME:
                hackname = None
            db = Connection(hackname)
            new_path = psplit.path[sid+4:]
            query = parse_qs(psplit.query)
            pid = int(query["pid"][0])
            prf = db.get_elements(Profile, {"pid": pid})
            if len(prf)==0:
                print("PID Not Found")
                self.send_response(401)
                self.end_headers()
                return
            prf = prf[0]
            if "hash" in query:
                if prf.currenthash is None or self.conndigest(prf.currenthash.encode("ascii"))!=query["hash"][0]:
                    print("Hash Failed")
                    self.send_response(401)
                    self.end_headers()
                    return
                prf.currenthash = None
                data = query["data"][0]
                data = b64decode(data.translate(str.maketrans({'-': '+', '_': '/'})))
                checksum = int.from_bytes(data[:4], 'big')
                nc = sum(data[4:])
                if checksum!=nc^CHECKMASK:
                    print("Checksum Failed")
                    self.send_response(401)
                    self.end_headers()
                    return
                if pid!=int.from_bytes(data[4:8], 'little'):
                    print("PID Failed")
                    self.send_response(401)
                    self.end_headers()
                    return
                if len(data)-12!=int.from_bytes(data[8:12], 'little'):
                    print("Length Failed")
                    self.send_response(401)
                    self.end_headers()
                    return
                data = data[12:]
                if int.from_bytes(data[:4], 'big')!=pid:
                    print("PID2 Failed")
                    self.send_response(401)
                    self.end_headers()
                    return
                select = int.from_bytes(data[4:12], 'big')
                data = data[12:]
                if CAPTURE:
                    print("SELECT: %016X"%select)
                    with open("capture/"+new_path.replace("/", "_").replace(".", "_")+"_"+datetime.utcnow().strftime("%Y%m%d%H%M%S")+".bin", 'wb') as file:
                        file.write(data)

                buffer = bytearray()
                statuscode = 0
                addstatus = True
                if new_path in ["/team/teamExist.asp", "/team/teamEntry.asp"]:
                    td = db.get_elements(TeamData, {"tid": select})
                    if len(td)>0:
                        td = td[0]
                        buffer += b'\x00\x00\x00\x01'+td.getdata(prf.lang if prf.unified else None)[8:]
                    else:
                        buffer += b'\x00\x00\x00\x00'
                elif new_path=="/team/teamList.asp":
                    tlist = db.get_elements(TeamData, {"rank": select&0xFFFFFFFF} if select&0x800000000 else None, ["udate DESC"], int.from_bytes(data[0:8], 'big'))
                    buffer += len(tlist).to_bytes(8, 'big')
                    for td in tlist:
                        buffer += td.getdata(prf.lang if prf.unified else None)
                elif new_path=="/team/teamRegist.asp":
                    db.delete_elements(TeamData, {"pid": prf.pid})
                    td = TeamData()
                    td.pid = prf.pid
                    td.tid = prf.pid*111
                    td.team = prf.team
                    td.rank = select>>32
                    td.lang = prf.lang
                    td.pkmn = data
                    buffer += td.tid.to_bytes(8, 'big')
                    db.insert_elements([td])
                elif new_path in ["/rescue/rescueExist.asp", "/rescue/rescueEntry.asp"]:
                    rq = db.get_elements(RescueRequest, {"rid": select, "completed": 0})
                    if len(rq)>0:
                        rq = rq[0]
                        if new_path=="/rescue/rescueEntry.asp":
                            db.increment_count([rq], ["requested"])
                        buffer += b'\x00\x00\x00\x01'+rq.getdata(prf.lang if prf.unified else None)[8:]
                    else:
                        buffer += b'\x00\x00\x00\x00'
                elif new_path=="/rescue/rescueList.asp":
                    method = int.from_bytes(data[16:20], 'big')
                    rlist = db.get_elements(RescueRequest, {"completed": 0}, ["requested ASC" if method==2 else "udate DESC",], int.from_bytes(data[8:16], 'big'))
                    buffer += len(rlist).to_bytes(8, 'big')
                    for rq in rlist:
                        buffer += rq.getdata(prf.lang if prf.unified else None)[:180]
                elif new_path=="/rescue/rescueRegist.asp":
                    rq = RescueRequest()
                    if select&0x8000000000000000:
                        rq.code = select-0x10000000000000000
                    else:
                        rq.code = select
                    rq.rid = (int.from_bytes(md5(pid.to_bytes(4, 'big')+bytes(randrange(256) for i in range(252))).digest(), 'big')%999999999999)+1
                    rq.uid = rq.rid
                    rq.dungeon = int.from_bytes(data[16:20], 'big')
                    rq.floor = int.from_bytes(data[20:24], 'big')
                    rq.seed = int.from_bytes(data[24:28], 'big')
                    rq.team = prf.team
                    rq.game = prf.game
                    rq.lang = prf.lang
                    rq.title = data[32:68].decode("utf-16-be").replace('\x00', '')
                    rq.message = data[68:140].decode("utf-16-be").replace('\x00', '')
                    buffer += rq.rid.to_bytes(8, 'big')
                    db.insert_elements([rq])
                elif new_path=="/rescue/rescueComplete.asp":
                    rq = db.get_elements(RescueRequest, {"rid": select})
                    if len(rq)>0:
                        rq = rq[0]
                        rq.completed = 1
                        if db.update_elements([rq], {"completed": 0}):
                            aok = RescueAOK()
                            aok.rid = select
                            aok.code = rq.code
                            aok.uresp = int.from_bytes(data[0:8], 'big', signed=True)
                            aok.item = data[24:28]
                            aok.pkmn = data[28:92]
                            aok.team = prf.team
                            aok.game = prf.game
                            aok.lang = prf.lang
                            aok.title = data[92:128].decode("utf-16-be").replace('\x00', '')
                            aok.message = data[128:200].decode("utf-16-be").replace('\x00', '')
                            db.insert_elements([aok])
                            buffer += b'\x00\x00\x00\x01'
                        else:
                            buffer += b'\x00\x00\x00\x00'
                    else:
                        statuscode = 1
                elif new_path=="/rescue/rescueCheck.asp":
                    aok = db.get_elements(RescueAOK, {"rid": select})
                    if len(aok)>0:
                        aok = aok[0]
                        buffer += b'\x00\x00\x00\x64'+aok.getdata(prf.lang if prf.unified else None)[8:]
                    else:
                        buffer += b'\x00\x00\x00\x00'
                elif new_path=="/rescue/rescueThanks.asp":
                    thk = RescueThanks()
                    thk.rid = select
                    thk.item = data[0:4]
                    thk.title = data[4:40].decode("utf-16-be").replace('\x00', '')
                    thk.message = data[40:112].decode("utf-16-be").replace('\x00', '')
                    db.insert_elements([thk])
                    buffer += b'\x00\x00\x00\x00'
                elif new_path=="/rescue/rescueReceive.asp":
                    thk = db.get_elements(RescueThanks, {"rid": select})
                    if len(thk)>0:
                        thk = thk[0]
                        if thk.claimed:
                            buffer += b'\x00\x00\x00\x00'
                        else:
                            buffer += b'\x00\x00\x00\x01'+thk.getdata()[8:]
                    else:
                        buffer += b'\x00\x00\x00\x00'
                elif new_path=="/common/setProfile.asp":
                    action = select>>32
                    prf.lang = select&0xFFFFFFFF
                    prf.flags = int.from_bytes(data[0x38:0x3C], 'big')
                    prf.team = data[0x3C:0x50].decode('utf-16').replace('\x00', '')
                    ccode = int.from_bytes(data[0x50:0x52], 'big')
                    email = data[:0x38].decode("ascii").replace('\x00', '')
                    scode = int.from_bytes(data[0x52:0x54], 'big')
                    if scode==0xFFFF:
                        buffer += b'\x00\x00\x00\x01'
                        scode = randrange(9999)+1
                        print("Code: %03d-%04d"%(ccode,scode))
                        TEMP_CHANGE[pid] = [email, scode, 0]
                    elif scode==0x0000:
                        prf.email = ""
                        prf.ccode = 0
                        prf.scode = 0
                    elif pid in TEMP_CHANGE:
                        if TEMP_CHANGE[pid][0]!=email or TEMP_CHANGE[pid][1]!=scode:
                            buffer += b'\x00\x00\x00\x01'
                            TEMP_CHANGE[pid][2] += 1
                            if TEMP_CHANGE[pid][2]>=3:
                                statuscode = 1
                                del TEMP_CHANGE[pid]
                        else:
                            buffer += b'\x00\x00\x00\x00'
                            prf.email = email
                            prf.ccode = ccode
                            prf.scode = scode
                            del TEMP_CHANGE[pid]
                else:
                    self.send_response(204)
                    self.end_headers()
                    return 
                if addstatus:
                    buffer = bytearray(statuscode.to_bytes(4, 'big'))+buffer
                buffer += self.conndigest(b64encode(buffer).decode("ascii").translate(str.maketrans({'+': '-', '/': '_'})).encode("ascii"), True).encode("ascii")
                db.update_elements([prf])
                self.send_response(200)
                self.send_header("Content-Length", str(len(buffer)))
                self.end_headers()
                self.wfile.write(buffer)
            else:
                prf.currenthash = ''.join([choice(TOKENPOOL) for i in range(32)])
                db.update_elements([prf])
                self.send_response(200)
                self.send_header("Content-Length", "32")
                self.end_headers()
                self.wfile.write(prf.currenthash.encode('ascii'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        self.attributes()
        psplit = urlparse(self.path)
        if psplit.path=="/ac":
            ctype = self.headers.get('content-type')
            if ctype=="application/x-www-form-urlencoded":
                data = self.parse_form()
                if data["action"]=="acctcreate":
                    res = dict()
                    res["returncd"] = "001" #MAX 3
                    res["token"] = "" #MAX 300
                    res["locator"] = "myserver.com" #MAX 50
                    res["challenge"] = "" #MAX 8
                    res["datetime"] = datetime.utcnow().strftime("%Y%m%d%H%M%S") #MAX 14
                    self.send_form(res)
                elif data["action"]=="login":
                    db = Connection()
                    res = dict()
                    gbsr = data["gsbrcd"]
                    gamecd = data["gamecd"]
                    elist = db.get_elements(GlobalProfile, {"gbsr": gbsr})
                    if len(elist)>0:
                        gprofile = elist[0]
                        profile = db.get_elements(Profile, {"pid": gprofile.profileid})[0]
                    else:
                        uid = int.from_bytes(md5(gbsr.encode('ascii')).digest(), 'big')&0x7FFFFFFF
                        gprofile = GlobalProfile()
                        gprofile.gbsr = gbsr
                        gprofile.game = gamecd
                        gprofile.userid = uid
                        gprofile.uniquenick = gbsr
                        gprofile.profileid = uid
                        profile = Profile()
                        profile.pid = uid
                        db.insert_elements([gprofile, profile])
                    if gamecd in ["C2SE", "C2SP", "C2SJ"]:
                        profile.game = GAME_SKY
                    elif gamecd in ["YFYE", "YFYP", "YFYJ"]:
                        profile.game = GAME_DARKNESS
                    elif gamecd in ["YFTE", "YFTP", "YFTJ"]:
                        profile.game = GAME_TIME
                    else:
                        profile.game = 0
                    gprofile._token = gbsr+''.join([choice(TOKENPOOL) for i in range(48)])
                    gprofile._challenge = ''.join([choice(TOKENPOOL) for i in range(8)])
                    db.update_elements([gprofile, profile])
                    res["returncd"] = "001" #MAX 3
                    res["token"] = gprofile._token #MAX 300
                    res["locator"] = "myserver.com" #MAX 50
                    res["challenge"] = gprofile._challenge #MAX 8
                    res["datetime"] = datetime.utcnow().strftime("%Y%m%d%H%M%S") #MAX 14
                    self.send_form(res)
                else:
                    self.send_response(404)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
