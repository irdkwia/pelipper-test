from socketserver import BaseRequestHandler, TCPServer
from random import randrange, choice
from base64 import b64decode, b64encode
from hashlib import md5

from structure.database import *

class CustomHandler(BaseRequestHandler):
    def challenge(self, sschal, sstoken, mmchal, yychal):
        return md5(md5(sschal.encode("ascii")).hexdigest().encode("ascii")+b" "*48+sstoken.encode("ascii")+mmchal.encode("ascii")+yychal.encode("ascii")+md5(sschal.encode("ascii")).hexdigest().encode("ascii")).hexdigest()
    def getfield(self):
        field = bytearray()
        c = self.request.recv(1)
        while c!=b"\\":
            field += c
            c = self.request.recv(1)
        return bytes(field).decode("ascii")
        
    def sendmessage(self, info=[]):
        for k, v in info:
            if v is None:
                continue
            if isinstance(k, str):
                k = k.encode("ascii")
            if isinstance(v, int):
                v = str(v&0x7FFFFFFF) # Force 32-bit unsigned
            if isinstance(v, str):
                v = v.encode("ascii")
            self.request.send(b"\\")
            self.request.send(k)
            self.request.send(b"\\")
            self.request.send(v)
        self.request.send(b"\\final\\")
        
    def parsemessage(self):
        if self.request.recv(1)!=b"\\":
            return False
        action = self.getfield()
        actinfo = self.getfield()
        data = dict()
        f = self.getfield()
        while f!="final":
            data[f] = self.getfield()
            f = self.getfield()
        if action=="login":
            self.profile = self.db.get_elements(GlobalProfile, {"token": data["authtoken"]}, limit=1)[0]
            #print("Log in")
            assert data["response"]==self.challenge(self.profile._challenge, data["authtoken"], data["challenge"], self.mmchal)
            buddylist = [str(b.buddy) for b in self.db.get_elements(BuddyList, {"pid": self.profile.profileid})]
            self.sendmessage([("lc", "2"), ("sesskey", "1"), ("proof", self.challenge(self.profile._challenge, data["authtoken"], self.mmchal, data["challenge"])), ("userid", self.profile.userid), ("profileid", self.profile.profileid), ("uniquenick", self.profile.uniquenick), ("lt", "1"), ("id", data["id"])])
            for b in buddylist:
                self.sendmessage([("bm", "100"),("f", b),("msg","|s|0|ss|Offline")])
        elif action=="getprofile":
            #print("Get profile")
            pid = int(data.get("profileid", self.profile.profileid))
            if pid==self.profile.profileid:
                profile = self.profile
            else:
                profile = self.db.get_elements(GlobalProfile, {"profileid": pid}, limit=1)[0]
            self.sendmessage([("pi", "2")]+[(k, v) for k, v in profile.__dict__.items() if not k.startswith("_")]+[("id", data["id"])])
        elif action=="updatepro":
            #print("Update profile")
            for k, v in data.items():
                if k in self.profile.__dict__:
                    setattr(self.profile, k, v)
            self.db.update_elements([self.profile])
        elif action=="status":
            #print("Status",actinfo)
            buddylist = [str(b.buddy) for b in self.db.get_elements(BuddyList, {"pid": self.profile.profileid})]
        elif action=="addbuddy":
            #print("Add buddy",data["newprofileid"])
            if len(self.db.get_elements(BuddyList, {"pid": self.profile.profileid, "buddy": int(data["newprofileid"])}, limit=1))>0:
                self.sendmessage([("error", ""),("err", 1539),("errmsg","The profile requested is already a buddy.")])
            elif len(self.db.get_elements(Profile, {"pid": int(data["newprofileid"])}, limit=1))==0:
                self.sendmessage([("error", ""),("err", 1539),("errmsg","The profile requested does not exist.")])
            else:
                pass
                bd = BuddyList()
                bd.pid = self.profile.profileid
                bd.buddy = int(data["newprofileid"])
                self.db.insert_elements([bd])
                msg = "\r\n\r\n"
                msg += "|signed|" + "d41d8cd98f00b204e9800998ecf8427e"
                self.sendmessage([("bm", "100"),("f", data["newprofileid"]),("msg","|s|0|ss|Offline")])
                self.sendmessage([("bm", "4"),("f", data["newprofileid"])])
                self.sendmessage([("bm", "2"),("f", data["newprofileid"]),("msg",msg)])
        elif action=="delbuddy":
            self.db.delete_elements(BuddyList, {"pid": self.profile.profileid, "buddy": int(data["delprofileid"])})
        elif action=="authadd":
            #print("Auth Add")
            pass
        elif action=="logout":
            #print("Log out")
            pass
        elif action=="ka":
            #print("Keep alive")
            self.sendmessage([("ka", "")])
        elif action=="otherslist":
            finallist = [("otherslist", "")]
            for pid in data["opids"].split("|"):
                profile = self.db.get_elements(GlobalProfile, {"profileid": int(pid)})[0]
                finallist.append(("o", int(pid)))
                finallist.append(("uniquenick", profile.uniquenick))
            finallist.append(("oldone", ""))
            self.sendmessage(finallist)
        else:
            print("Unknown action", action, actinfo)
        return True
        
    def requestchallenge(self):
        self.mmchal = ''.join([choice(TOKENPOOL) for i in range(10)])
        self.sendmessage([("lc", "1"), ("challenge", self.mmchal), ("id", "1")])
        
    def handle(self):
        self.db = Connection()
        self.profile = None
        self.mmchal = None
        self.requestchallenge()
        # self.request is the client connection
        while self.parsemessage():pass
