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
                v = str(v)
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
            self.profile = Connection.get_elements(GlobalProfile, {"token": data["authtoken"]})[0]
            print("Log in")
            assert data["response"]==self.challenge(self.profile._challenge, data["authtoken"], data["challenge"], self.mmchal)
            buddylist = [str(b.buddy) for b in Connection.get_elements(BuddyList, {"pid": self.profile.profileid})]
            self.sendmessage([("bdy", len(buddylist)), ("list", ",".join(buddylist))])
            #for b in buddylist:
            #    self.sendmessage([("bm", "100"),("f", b),("msg","|s|0|ss|Offline")])
            self.sendmessage([("lc", "2"), ("sesskey", "1"), ("proof", self.challenge(self.profile._challenge, data["authtoken"], self.mmchal, data["challenge"])), ("userid", self.profile.userid), ("profileid", self.profile.profileid), ("uniquenick", self.profile.uniquenick), ("lt", "1"), ("id", data["id"])])
        elif action=="getprofile":
            print("Get profile")
            self.sendmessage([("pi", "2")]+[(k, v) for k, v in self.profile.__dict__.items() if not k.startswith("_")]+[("id", data["id"])])
        elif action=="updatepro":
            print("Update profile")
            for k, v in data.items():
                if k in self.profile.__dict__:
                    setattr(self.profile, k, v)
            Connection.update_elements([self.profile])
        elif action=="status":
            print("Status",actinfo)
            buddylist = [str(b.buddy) for b in Connection.get_elements(BuddyList, {"pid": self.profile.profileid})]
            #for b in buddylist:
            #    self.sendmessage([("bm", "100"),("f", b),("msg","|s|0|ss|Offline")])
        elif action=="addbuddy":
            print("Add buddy",data["newprofileid"])
            if len(Connection.get_elements(BuddyList, {"pid": self.profile.profileid, "buddy": int(data["newprofileid"])}))>0:
                self.sendmessage([("error", ""),("err", 1539),("errmsg","The profile requested is already a buddy.")])
            else:
                pass
                #bd = BuddyList()
                #bd.pid = self.profile.profileid
                #bd.buddy = int(data["newprofileid"])
                #Connection.insert_elements([bd])
                #msg = "\r\n\r\n"
                #msg += "|signed|" + "d41d8cd98f00b204e9800998ecf8427f"
                #self.sendmessage([("bm", "4"),("f", data["newprofileid"]),("msg","")])
                #self.sendmessage([("bm", "100"),("f", data["newprofileid"]),("msg","|s|0|ss|Offline")])
                #self.sendmessage([("bm", "1"),("f", "1480046773"),("msg","I have authorized your request to add me to your list")])
                #self.sendmessage([("bm", "2"),("f", data["newprofileid"]),("msg",msg)])
            
        elif action=="logout":
            print("Log out")
        elif action=="ka":
            print("Keep alive")
            self.sendmessage([("ka", "")])
        else:
            print("Unknown action", action, actinfo)
        return True
        
    def handle(self):
        self.profile = None
        self.mmchal = ''.join([choice(TOKENPOOL) for i in range(10)])
        self.sendmessage([("lc", "1"), ("challenge", self.mmchal), ("id", "1")])
        # self.request is the client connection
        while self.parsemessage():pass

tcpserv = TCPServer((SERVER_ADDR, 29900), CustomHandler)

print("Starting TCP server...")
tcpserv.serve_forever()
