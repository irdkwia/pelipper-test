import asyncio
import html
from base64 import b64decode, b64encode
from datetime import datetime
from enum import Enum
from hashlib import md5, sha1
from http.server import BaseHTTPRequestHandler
from random import choice, randrange
from urllib.parse import parse_qs, urlparse

import discord_bot
from structure.dungeon_formatter import *
from structure.models import *
from structure.tools import *

TEMP_CHANGE = dict()

CAPTURE = False


class CustomHandler(BaseHTTPRequestHandler):
    def conndigest(self, data, out=False):
        return sha1(SALT + data + (SALT if out else b"")).hexdigest()

    def attributes(self):
        self.server_version = "LFL/0.1"

    def upgrade11(self):
        self.protocol_version = "HTTP/1.1"

    def parse_form(self):
        length = int(self.headers.get("content-length"))
        denc = parse_qs(self.rfile.read(length).decode("ascii"))
        data = dict()
        for k, v in denc.items():
            s = b64decode(v[0].translate(str.maketrans({"-": "+", "_": "/", "*": "="})))
            if k in ["words"]:
                data[k] = s
            elif k in ["devname", "ingamesn"]:
                data[k] = s.decode(ENCODING)
            else:
                data[k] = s.decode("ascii")
        return data

    def send_form(self, data, headers=dict()):
        buffer = bytearray()
        for k, v in data.items():
            if len(buffer) > 0:
                buffer += b"&"
            if isinstance(v, str):
                v = v.encode("ascii")
            buffer += (
                k.encode("ascii")
                + b"="
                + b64encode(v)
                .decode("ascii")
                .translate(str.maketrans({"+": "-", "/": "_", "=": "*"}))
                .encode("ascii")
            )
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
        if psplit.path == "/":
            if self.headers.get("host") == "conntest.nintendowifi.net":
                # Return a simple page if accessed from Nintendo DS
                with open("static/index.html", "rb") as file:
                    buffer = file.read()
            else:
                buffer = self.render_index_page()

            self.send_response(200)
            self.end_headers()
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(buffer)))
            self.wfile.write(buffer)
            return
        elif psplit.path == "/favicon.ico":
            with open("static/favicon.ico", "rb") as file:
                buffer = file.read()
            self.send_response(200)
            self.end_headers()
            self.send_header("Content-Type", "image/x-icon")
            self.send_header("Content-Length", str(len(buffer)))
            self.wfile.write(buffer)
            return
        elif psplit.path == "/rewire" and REWIRE:
            with open("static/rewire.html", "rb") as file:
                buffer = file.read() % (b"black", b"white", b"")
            self.send_response(200)
            self.end_headers()
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(buffer)))
            self.wfile.write(buffer)
            return
        elif psplit.path == "/friend":
            with open("static/friend.html", "rb") as file:
                buffer = file.read()
            self.send_response(200)
            self.end_headers()
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(buffer)))
            self.wfile.write(buffer)
            return

        sid = psplit.path.find("/", 1)
        if sid != -1 and psplit.path[sid:].startswith("/web"):
            self.upgrade11()
            hackname = psplit.path[1:sid]
            if hackname == BASEGAME:
                hackname = None
            db = Connection(hackname)
            new_path = psplit.path[sid + 4 :]
            query = parse_qs(psplit.query)
            pid = int(query["pid"][0])
            prf = db.get_elements(Profile, {"pid": pid}, limit=1)
            if len(prf) == 0:
                # print("PID Not Found")
                self.send_response(401)
                self.end_headers()
                return
            prf = prf[0]
            if "hash" in query:
                if (
                    prf.currenthash is None
                    or self.conndigest(prf.currenthash.encode("ascii"))
                    != query["hash"][0]
                ):
                    # print("Hash Failed")
                    self.send_response(401)
                    self.end_headers()
                    return
                prf.currenthash = None
                data = query["data"][0]
                data = b64decode(data.translate(str.maketrans({"-": "+", "_": "/"})))
                checksum = int.from_bytes(data[:4], "big")
                nc = sum(data[4:])
                if checksum != nc ^ CHECKMASK:
                    # print("Checksum Failed")
                    self.send_response(401)
                    self.end_headers()
                    return
                if pid != int.from_bytes(data[4:8], "little"):
                    # print("PID Failed")
                    self.send_response(401)
                    self.end_headers()
                    return
                if len(data) - 12 != int.from_bytes(data[8:12], "little"):
                    # print("Length Failed")
                    self.send_response(401)
                    self.end_headers()
                    return
                data = data[12:]
                if int.from_bytes(data[:4], "big") != pid:
                    # print("PID2 Failed")
                    self.send_response(401)
                    self.end_headers()
                    return
                select = int.from_bytes(data[4:12], "big")
                data = data[12:]
                if CAPTURE:
                    # print("SELECT: %016X"%select)
                    datecapture = datetime.utcnow()
                    with open(
                        "capture/"
                        + new_path.replace("/", "_").replace(".", "_")
                        + "_"
                        + datecapture.strftime("%Y%m%d%H%M%S")
                        + "_in.bin",
                        "wb",
                    ) as file:
                        file.write(data)

                buffer = bytearray()
                statuscode = 0
                addstatus = True
                adddigest = True
                if new_path in ["/team/teamExist.asp", "/team/teamEntry.asp"]:
                    td = db.get_elements(TeamData, {"tid": select}, limit=1)
                    if len(td) > 0:
                        td = td[0]
                        buffer += (
                            b"\x00\x00\x00\x01"
                            + td.getdata(prf.lang if prf.unified else None)[8:]
                        )
                    else:
                        buffer += b"\x00\x00\x00\x00"
                elif new_path == "/team/teamList.asp":
                    method = int.from_bytes(data[8:12], "big")
                    if method == 0:
                        friends = db.get_elements(
                            BuddyList,
                            {"pid": prf.pid},
                            None,
                            None,
                            None,
                            [("pid", "buddy")],
                        )
                        c = None
                        i = {"pid": [prf.pid] + [b.buddy for b in friends]}
                    else:
                        c = {"private": 0}
                        i = None
                        if select & 0x800000000:
                            c["rank"] = select & 0xFFFFFFFF
                    tlist = db.get_elements(
                        TeamData, c, ["udate DESC"], int.from_bytes(data[0:8], "big"), i
                    )
                    buffer += len(tlist).to_bytes(8, "big")
                    for td in tlist:
                        buffer += td.getdata(prf.lang if prf.unified else None)
                elif new_path == "/team/teamRegist.asp":
                    db.delete_elements(TeamData, {"pid": prf.pid})
                    td = TeamData()
                    td.pid = prf.pid
                    td.tid = prf.pid * 111
                    td.team = prf.team
                    td.rank = select >> 32
                    td.lang = prf.lang
                    td.pkmn = data
                    td.private = select & 0xFFFFFFFF
                    buffer += td.tid.to_bytes(8, "big")
                    db.insert_elements([td])
                elif new_path in ["/rescue/rescueExist.asp", "/rescue/rescueEntry.asp"]:
                    rq = db.get_elements(
                        RescueRequest, {"rid": select, "completed": 0}, limit=1
                    )
                    if len(rq) > 0:
                        rq = rq[0]
                        if new_path == "/rescue/rescueEntry.asp":
                            db.increment_count([rq], ["requested"])
                            buffer += (
                                b"\x00\x00\x00\x01"
                                + rq.getdata(prf.lang if prf.unified else None)[8:]
                            )
                        else:
                            buffer += (
                                b"\x00\x00\x00\x01"
                                + rq.getdata(prf.lang if prf.unified else None, 1)[8:]
                            )
                    else:
                        buffer += b"\x00\x00\x00\x00"
                elif new_path == "/rescue/rescueList.asp":
                    method = int.from_bytes(data[16:20], "big")
                    if method == 0:
                        friends = db.get_elements(
                            BuddyList,
                            {"pid": prf.pid},
                            None,
                            None,
                            None,
                            [("pid", "buddy")],
                        )
                        c = None
                        i = {"pid": [prf.pid] + [b.buddy for b in friends]}
                    else:
                        c = {"completed": 0, "private": 0}
                        i = None
                    rlist = db.get_elements(
                        RescueRequest,
                        c,
                        [
                            "requested ASC" if method == 2 else "udate DESC",
                        ],
                        int.from_bytes(data[8:16], "big"),
                    )
                    buffer += len(rlist).to_bytes(8, "big")
                    for rq in rlist:
                        buffer += rq.getdata(prf.lang if prf.unified else None)
                elif new_path == "/rescue/rescueRegist.asp":
                    rq = RescueRequest()
                    if select & 0x8000000000000000:
                        rq.code = select - 0x10000000000000000
                    else:
                        rq.code = select
                    rq.pid = prf.pid
                    rq.rid = (
                        int.from_bytes(
                            md5(
                                pid.to_bytes(4, "big")
                                + bytes(randrange(256) for i in range(252))
                            ).digest(),
                            "big",
                        )
                        % 999999999999
                    ) + 1
                    rq.uid = rq.rid
                    rq.dungeon = int.from_bytes(data[16:20], "big")
                    rq.floor = int.from_bytes(data[20:24], "big")
                    rq.seed = int.from_bytes(data[24:28], "big")
                    rq.private = int.from_bytes(data[28:32], "big")
                    rq.team = prf.team
                    rq.game = prf.game
                    rq.lang = prf.lang
                    rq.title = data[32:68].decode("utf-16-be").replace("\x00", "")
                    rq.message = data[68:140].decode("utf-16-be").replace("\x00", "")
                    buffer += rq.rid.to_bytes(8, "big")
                    db.insert_elements([rq])

                    rescued_user_name = None
                    (ty, rescued_identifier) = ProfileType.into_parts(prf.email)
                    if ty == ProfileType.DISCORD:
                        rescued_user_name = rescued_identifier

                    if discord_bot.enabled and not rq.private:
                        asyncio.run_coroutine_threadsafe(
                            discord_bot.send_sos_global(
                                rescued_user_name,
                                rq.team,
                                rq.title,
                                rq.message,
                                format_floor(db, rq.dungeon, rq.floor),
                                format_rescue_code(rq.rid),
                            ),
                            discord_bot.bot.loop,
                        )

                    ptr_include = {
                        "flags": [
                            0x20000,
                            0x20000 | 0x40000,
                            0x20000 | 0x80000,
                            0x20000 | 0x40000 | 0x80000,
                        ]
                    }
                    if rq.private:
                        friends = db.get_elements(
                            BuddyList,
                            {"pid": prf.pid},
                            None,
                            None,
                            None,
                            [("pid", "buddy")],
                        )
                        ptr_include.update(
                            {"pid": [prf.pid] + [b.buddy for b in friends]}
                        )

                    potential_rescuers = db.get_elements(Profile, include=ptr_include)
                    for rescuer_prf in potential_rescuers:
                        if rescuer_prf.pid == prf.pid:  # Skip yourself
                            continue
                        (ty, rescuer_identifier) = ProfileType.into_parts(
                            rescuer_prf.email
                        )
                        if ty == ProfileType.DISCORD:  # Discord user name/ID
                            if discord_bot.enabled:
                                asyncio.run_coroutine_threadsafe(
                                    discord_bot.send_sos(
                                        rescued_user_name,
                                        rescuer_identifier,
                                        rq.team,
                                        rq.title,
                                        rq.message,
                                        format_floor(db, rq.dungeon, rq.floor),
                                        format_rescue_code(rq.rid),
                                    ),
                                    discord_bot.bot.loop,
                                )

                elif new_path == "/rescue/rescueComplete.asp":
                    rq = db.get_elements(RescueRequest, {"rid": select}, limit=1)
                    if len(rq) > 0:
                        rq = rq[0]
                        rq.completed = 1
                        if db.update_elements([rq], {"completed": 0}):
                            aok = RescueAOK()
                            aok.rid = select
                            aok.code = rq.code
                            aok.uresp = int.from_bytes(data[0:8], "big", signed=True)
                            aok.item = data[24:28]
                            aok.pkmn = data[28:92]
                            aok.team = prf.team
                            aok.game = prf.game
                            aok.lang = prf.lang
                            aok.rescuerpid = prf.pid
                            aok.title = (
                                data[92:128].decode("utf-16-be").replace("\x00", "")
                            )
                            aok.message = (
                                data[128:200].decode("utf-16-be").replace("\x00", "")
                            )
                            db.insert_elements([aok])
                            buffer += b"\x00\x00\x00\x01"

                            # Sending A-OK
                            rescued_prf = db.get_elements(
                                Profile, {"pid": rq.pid}, limit=1
                            )
                            if len(rescued_prf) > 0:
                                rescuer_user_name = None
                                (rescuer_ty, rescuer_identifier) = (
                                    ProfileType.into_parts(prf.email)
                                )
                                if rescuer_ty == ProfileType.DISCORD:
                                    rescuer_user_name = rescuer_identifier

                                # Sending A-OK to user
                                rescued_prf = rescued_prf[0]
                                rescued_user_name = None
                                (rescued_ty, rescued_identifier) = (
                                    ProfileType.into_parts(rescued_prf.email)
                                )
                                if rescued_ty == ProfileType.DISCORD:
                                    rescued_user_name = rescued_identifier
                                    if rescued_prf.flags & 0x40000:
                                        if discord_bot.enabled:
                                            asyncio.run_coroutine_threadsafe(
                                                discord_bot.send_aok(
                                                    rescued_user_name,
                                                    rescuer_user_name,
                                                    rq.team,
                                                    aok.team,
                                                    aok.title,
                                                    aok.message,
                                                    format_floor(
                                                        db, rq.dungeon, rq.floor
                                                    ),
                                                    format_rescue_code(rq.rid),
                                                ),
                                                discord_bot.bot.loop,
                                            )
                                # Sending A-OK to everyone
                                if discord_bot.enabled:
                                    asyncio.run_coroutine_threadsafe(
                                        discord_bot.send_aok_global(
                                            rescued_user_name,
                                            rescuer_user_name,
                                            rq.team,
                                            aok.team,
                                            aok.title,
                                            aok.message,
                                            format_floor(db, rq.dungeon, rq.floor),
                                            format_rescue_code(rq.rid),
                                        ),
                                        discord_bot.bot.loop,
                                    )
                        else:
                            buffer += b"\x00\x00\x00\x00"
                    else:
                        statuscode = 1
                elif new_path == "/rescue/rescueCheck.asp":
                    aok = db.get_elements(RescueAOK, {"rid": select}, limit=1)
                    if len(aok) > 0:
                        aok = aok[0]
                        buffer += (
                            b"\x00\x00\x00\x64"
                            + aok.getdata(prf.lang if prf.unified else None)[8:]
                        )
                    else:
                        buffer += b"\x00\x00\x00\x00"
                elif new_path == "/rescue/rescueThanks.asp":
                    thk = RescueThanks()
                    thk.rid = select
                    thk.item = data[0:4]
                    thk.title = data[4:40].decode("utf-16-be").replace("\x00", "")
                    thk.message = data[40:112].decode("utf-16-be").replace("\x00", "")
                    db.insert_elements([thk])

                    buffer += b"\x00\x00\x00\x00"

                    # Sending Thank-You
                    aok = db.get_elements(RescueAOK, {"rid": select}, limit=1)

                    if len(aok) > 0:
                        aok = aok[0]
                        rescuer_prf = db.get_elements(
                            Profile, {"pid": aok.rescuerpid}, limit=1
                        )
                        if len(rescuer_prf) > 0:
                            rescuer_prf = rescuer_prf[0]
                            if rescuer_prf.flags & 0x80000:
                                (ty, rescuer_identifier) = ProfileType.into_parts(
                                    rescuer_prf.email
                                )
                                if ty == ProfileType.DISCORD:  # Discord user name/ID
                                    if discord_bot.enabled:
                                        asyncio.run_coroutine_threadsafe(
                                            discord_bot.send_thank_you(
                                                rescuer_identifier,
                                                thk.title,
                                                thk.message,
                                            ),
                                            discord_bot.bot.loop,
                                        )

                elif new_path == "/rescue/rescueReceive.asp":
                    thk = db.get_elements(RescueThanks, {"rid": select}, limit=1)
                    if len(thk) > 0:
                        thk = thk[0]
                        thk.claimed = 1
                        if db.update_elements([thk], {"claimed": 0}):
                            buffer += b"\x00\x00\x00\x01" + thk.getdata()[8:]
                        else:
                            buffer += b"\x00\x00\x00\x00"
                    else:
                        buffer += b"\x00\x00\x00\x00"
                elif new_path == "/common/setProfile.asp":
                    action = select >> 32
                    prf.lang = select & 0xFFFFFFFF
                    prf.flags = int.from_bytes(data[0x38:0x3C], "big")
                    prf.team = data[0x3C:0x50].decode("utf-16-le").replace("\x00", "")
                    ccode = int.from_bytes(data[0x50:0x52], "big")
                    email = data[:0x38].decode("ascii").replace("\x00", "")
                    scode = int.from_bytes(data[0x52:0x54], "big")
                    if scode == 0xFFFF:
                        success = False

                        (ty, identifier) = ProfileType.into_parts(email)
                        if discord_bot.enabled and ty == ProfileType.DISCORD:
                            # If the entered email is not a real email address, treat it as a Discord ID/user name
                            scode = randrange(9999) + 1
                            full_code = "%03d-%04d" % (ccode, scode)
                            print("Code: " + full_code)

                            try:
                                future = asyncio.run_coroutine_threadsafe(
                                    discord_bot.send_signup_code(identifier, full_code),
                                    discord_bot.bot.loop,
                                )
                                future.result(10)

                                success = True
                            except Exception as error:
                                print(error)

                        if success:
                            buffer += b"\x00\x00\x00\x01"
                            TEMP_CHANGE[pid] = [email, scode, 0]
                        else:
                            buffer += b"\x00\x00\x00\x00"

                    elif scode == 0x0000:
                        prf.email = ""
                        prf.ccode = 0
                        prf.scode = 0
                        if pid in TEMP_CHANGE:
                            del TEMP_CHANGE[pid]
                        buffer += b"\x00\x00\x00\x01"
                    elif pid in TEMP_CHANGE:
                        if TEMP_CHANGE[pid][0] != email or TEMP_CHANGE[pid][1] != scode:
                            buffer += b"\x00\x00\x00\x01"
                            TEMP_CHANGE[pid][2] += 1
                            if TEMP_CHANGE[pid][2] >= 3:
                                statuscode = 1
                                del TEMP_CHANGE[pid]
                        else:
                            buffer += b"\x00\x00\x00\x00"
                            prf.email = email
                            prf.ccode = ccode
                            prf.scode = scode
                            del TEMP_CHANGE[pid]
                    else:
                        buffer += b"\x00\x00\x00\x01"
                else:
                    self.send_response(204)
                    self.end_headers()
                    return
                if addstatus:
                    buffer = bytearray(statuscode.to_bytes(4, "big")) + buffer
                if adddigest:
                    buffer += self.conndigest(
                        b64encode(buffer)
                        .decode("ascii")
                        .translate(str.maketrans({"+": "-", "/": "_"}))
                        .encode("ascii"),
                        True,
                    ).encode("ascii")
                if CAPTURE:
                    datecapture = datetime.utcnow()
                    with open(
                        "capture/"
                        + new_path.replace("/", "_").replace(".", "_")
                        + "_"
                        + datecapture.strftime("%Y%m%d%H%M%S")
                        + "_out.bin",
                        "wb",
                    ) as file:
                        file.write(buffer)
                db.update_elements([prf])
                self.send_response(200)
                self.send_header("Content-Length", str(len(buffer)))
                self.end_headers()
                self.wfile.write(buffer)
            else:
                prf.currenthash = "".join([choice(TOKENPOOL) for i in range(32)])
                db.update_elements([prf])
                self.send_response(200)
                self.send_header("Content-Length", "32")
                self.end_headers()
                self.wfile.write(prf.currenthash.encode("ascii"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        self.attributes()
        psplit = urlparse(self.path)
        if psplit.path == "/pr":
            ctype = self.headers.get("content-type")
            if ctype == "application/x-www-form-urlencoded":
                data = self.parse_form()
                res = dict()
                res["returncd"] = "000"  # MAX 3
                res["prwords"] = "0" * len(
                    data["words"].decode(data["wenc"]).split("\t")
                )
                self.send_form(res)
            else:
                self.send_response(404)
                self.end_headers()
        elif psplit.path == "/ac":
            ctype = self.headers.get("content-type")
            if ctype == "application/x-www-form-urlencoded":
                data = self.parse_form()
                if data["action"] in ["acctcreate", "login"]:
                    db = Connection()
                    res = dict()
                    if data["action"] == "acctcreate":
                        gbsr = ""
                    else:
                        gbsr = data["gsbrcd"]
                    userid = int(data["userid"])
                    gamecd = data["gamecd"]
                    elist = db.get_elements(
                        GlobalProfile, {"gbsr": gbsr, "userid": userid}, limit=1
                    )
                    if len(elist) > 0:
                        if gbsr == "":
                            if (
                                len(
                                    db.get_elements(
                                        GlobalProfile, {"userid": userid}, limit=1
                                    )
                                )
                                > 0
                            ):
                                raise ValueError("userid '%d' already exists!" % userid)
                        gprofile = elist[0]
                        profile = db.get_elements(
                            Profile, {"pid": gprofile.profileid}, limit=1
                        )[0]
                    else:
                        elist = db.get_elements(
                            GlobalProfile, {"gbsr": "", "userid": userid}, limit=1
                        )
                        if len(elist) > 0:
                            db.delete_elements(
                                GlobalProfile, {"gbsr": "", "userid": userid}
                            )
                            gprofile = elist[0]
                        else:
                            gprofile = GlobalProfile()
                        uid = (
                            int.from_bytes(
                                md5(
                                    gbsr.encode("ascii")
                                    + data["userid"].encode("ascii")
                                ).digest(),
                                "big",
                            )
                            & 0x7FFFFFFF
                        )
                        while (
                            len(db.get_elements(ProfileChange, {"pid": uid}, limit=1))
                            > 0
                            or len(db.get_elements(Profile, {"pid": uid}, limit=1)) > 0
                        ):
                            uid = (uid + 1) & 0x7FFFFFFF
                        gprofile = GlobalProfile()
                        gprofile._gbsr = gbsr
                        gprofile.game = gamecd
                        gprofile.userid = userid
                        gprofile.uniquenick = gbsr
                        gprofile.profileid = uid
                        profile = Profile()
                        profile.pid = uid
                        db.insert_elements([gprofile, profile])
                    if profile.devname != data.get(
                        "devname", ""
                    ) or profile.team != data.get("ingamesn", ""):
                        profile.devname = data.get("devname", "")
                        profile.team = data.get("ingamesn", "")
                        if REWIRE:
                            pf = db.get_elements(
                                ProfileChange,
                                {"devname": profile.devname, "team": profile.team},
                                limit=1,
                            )
                            if len(pf) > 0:
                                pf = pf[0]
                                db.delete_elements(ProfileChange, {"pid": pf.pid})
                                db.delete_elements(Profile, {"pid": profile.pid})
                                db.delete_elements(
                                    GlobalProfile, {"gbsr": gprofile._gbsr}
                                )
                                gprofile.profileid = pf.pid
                                profile.pid = pf.pid
                                db.insert_elements([gprofile, profile])
                    if gamecd in ["C2SE", "C2SP", "C2SJ"]:
                        profile.game = GAME_SKY
                    elif gamecd in ["YFYE", "YFYP", "YFYJ"]:
                        profile.game = GAME_DARKNESS
                    elif gamecd in ["YFTE", "YFTP", "YFTJ"]:
                        profile.game = GAME_TIME
                    elif gamecd in ["WPAE", "WPAP", "WPAJ"]:
                        profile.game = GAME_ARASHI
                    elif gamecd in ["WPFE", "WPFP", "WPFJ"]:
                        profile.game = GAME_HONOO
                    elif gamecd in ["WPHE", "WPHP", "WPHJ"]:
                        profile.game = GAME_HIKARI
                    else:
                        profile.game = 0
                    gprofile._token = gbsr + "".join(
                        [choice(TOKENPOOL) for i in range(48)]
                    )
                    gprofile._challenge = "".join([choice(TOKENPOOL) for i in range(8)])
                    db.update_elements([gprofile, profile])
                    res["returncd"] = "001"  # MAX 3
                    res["token"] = gprofile._token  # MAX 300
                    res["locator"] = "myserver.com"  # MAX 50
                    res["challenge"] = gprofile._challenge  # MAX 8
                    res["datetime"] = datetime.utcnow().strftime(
                        "%Y%m%d%H%M%S"
                    )  # MAX 14
                    self.send_form(res)
                elif data["action"].lower() == "svcloc":
                    res = dict()
                    res["returncd"] = "007"  # MAX 3
                    res["svchost"] = BASEGAME + ".wondermail.net"  # MAX 64
                    res["statusdata"] = "Y"  # MAX 1
                    res["servicetoken"] = "MyTokenWondermail"  # MAX 300
                    self.send_form(res)
                else:
                    self.send_response(404)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
        elif psplit.path == "/download":
            ctype = self.headers.get("content-type")
            if ctype == "application/x-www-form-urlencoded":
                data = self.parse_form()
                db = Connection()
                elist = db.get_elements(WMGameList, {"passwd": data["passwd"]}, limit=1)
                repllang = None
                if "attr1" in data:
                    repllang = LANGTOID.get(data["attr1"], None)
                if len(elist) == 0:
                    self.send_response(404)
                    self.end_headers()
                elif data["action"] in ["count", "list", "contents"]:
                    wgame = elist[0]
                    db = Connection(None if wgame.prefix == BASEGAME else wgame.prefix)
                    buffer = bytearray()
                    if data["action"] == "count":
                        wmlist = db.get_elements(WMPassList, {"version": wgame.version})
                        buffer += str(len(wmlist) * len(wgame.lang.split(","))).encode(
                            "ascii"
                        )
                    elif data["action"] == "list":
                        wmlist = db.get_elements(WMPassList, {"version": wgame.version})
                        llist = (
                            [int(x) for x in wgame.lang.split(",")]
                            if repllang is None
                            else [repllang]
                        )
                        # ID    BUFFER  NAME  NAME  NAME    NB
                        for wm in wmlist:
                            for l in llist:
                                buffer += (
                                    str(l + wm.wid * 10)
                                    + "\t"
                                    + b64encode(b"")
                                    .decode("ascii")
                                    .translate(
                                        str.maketrans({"+": "-", "/": "_", "=": "*"})
                                    )
                                    + "\t\t\t\t"
                                    + str(len(wm.data) + 32)
                                    + "\r\n"
                                ).encode("ascii")
                    elif data["action"] == "contents":
                        wmlist = db.get_elements(
                            WMPassList, {"wid": int(data["contents"]) // 10}
                        )
                        if len(wmlist) == 0:
                            element = bytes(0)
                        else:
                            element = wmlist[0].data
                        buffer += (
                            0x50443357 if wgame.version == GAME_SKY else 0x50443257
                        ).to_bytes(4, BYTE_ENCODING)
                        buffer += (
                            0x08261522 if wgame.version == GAME_SKY else 0x07070419
                        ).to_bytes(4, BYTE_ENCODING)
                        buffer += (
                            calcsum(SOURCE_WM, element)
                            if wgame.version == GAME_SKY
                            else calcsumsimple(element)
                        ).to_bytes(4, BYTE_ENCODING)
                        # LANG
                        buffer += (int(data["contents"]) % 10).to_bytes(4, BYTE_ENCODING)
                        buffer += bytes(0x10)
                        buffer += element
                    self.send_response(200)
                    self.send_header("Content-Length", str(len(buffer)))
                    self.end_headers()
                    self.wfile.write(buffer)
                else:
                    self.send_response(404)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
        elif psplit.path == "/rewire" and REWIRE:
            with open("static/rewire.html", "rb") as file:
                buffer = file.read()
            ctype = self.headers.get("content-type")
            if ctype == "application/x-www-form-urlencoded":
                try:
                    db = Connection()
                    length = int(self.headers.get("content-length"))
                    denc = parse_qs(self.rfile.read(length).decode("ascii"))
                    if "devname" in denc and "team" in denc and "code" in denc:
                        devname = denc["devname"][0]
                        team = denc["team"][0]
                        if (
                            len(denc["code"][0]) == 14
                            and denc["code"][0][4] == "-"
                            and denc["code"][0][9] == "-"
                        ):
                            code = int(denc["code"][0].replace("-", "")) & 0xFFFFFFFF
                            if (
                                len(
                                    db.get_elements(
                                        Profile,
                                        {"devname": devname, "team": team},
                                        limit=1,
                                    )
                                )
                                > 0
                            ):
                                buffer = buffer % (
                                    b"white",
                                    b"red",
                                    b"You must choose another User Name and Team Name combination.",
                                )
                            elif len(db.get_elements(Profile, {"pid": code})) > 0:
                                buffer = buffer % (
                                    b"white",
                                    b"red",
                                    b"This Friend Code is already used by someone else.",
                                )
                            else:
                                pf = ProfileChange()
                                pf.pid = code
                                pf.team = team
                                pf.devname = devname
                                db.insert_elements([pf])
                                buffer = buffer % (
                                    b"black",
                                    b"lightblue",
                                    b'Successfully registered "%s" "%s" "%s"!'
                                    % (
                                        html.escape(devname).encode("utf-8"),
                                        html.escape(team).encode("utf-8"),
                                        html.escape(denc["code"][0]).encode("utf-8"),
                                    ),
                                )
                        else:
                            buffer = buffer % (
                                b"white",
                                b"red",
                                b"Invalid Friend Code format",
                            )
                    else:
                        buffer = buffer % (b"white", b"red", b"Invalid form data")
                except:
                    buffer = buffer % (b"white", b"red", b"Invalid form data")
            else:
                buffer = buffer % (b"black", b"white", b"")
            self.send_response(200)
            self.end_headers()
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(buffer)))
            self.wfile.write(buffer)
        else:
            self.send_response(404)
            self.end_headers()

    def render_index_page(self):
        with open("static/templates/main.html", encoding="utf-8") as file:
            main_template = file.read()

        with open("static/templates/rescue.html", encoding="utf-8") as file:
            rescue_template = file.read()

        db = Connection()

        # TODO: cache statistics for future accesses (it should be enough to update them every few seconds or so)
        profile_count = db.count_elements(Profile)
        sos_mail_count = db.count_elements(RescueRequest)
        aok_mail_count = db.count_elements(RescueAOK)
        thank_you_mail_count = db.count_elements(RescueThanks)
        wonder_mail_count = db.count_elements(WMPassList)
        trade_team_count = db.count_elements(TeamData)

        limit = 200
        open_rescues = db.get_elements(
            RescueRequest,
            {"completed": 0, "private": 0},
            ordering=["udate DESC"],
            limit=limit,
        )
        open_rescues_count = str(len(open_rescues))
        if open_rescues_count == limit:
            open_rescues_count += "+"

        rescue_cards = []
        for rq in open_rescues:
            if rq.game == GAME_TIME:
                game = "Time"
            elif rq.game == GAME_DARKNESS:
                game = "Darkness"
            elif rq.game == GAME_SKY:
                game = "Sky"
            elif rq.game == GAME_ARASHI:
                game = "Tempest"
            elif rq.game == GAME_HONOO:
                game = "Wildfire"
            elif rq.game == GAME_HIKARI:
                game = "Radiance"
            else:
                game = "INVALID"

            title = rq.title
            if not title:
                title = f"SOS Mail from {rq.team}"
            message = rq.message
            if not message:
                message = "We were defeated! Please help!"

            vars = {
                "title": title,
                "dungeon": format_floor(db, rq.dungeon, rq.floor),
                "code": format_rescue_code(rq.rid),
                "team": rq.team,
                "game": game,
                "message": message,
            }
            card = rescue_template.format(**vars)
            rescue_cards.append(card)

        vars = {
            "server_addr": SERVER_ADDR,
            "profile_count": profile_count,
            "sos_mail_count": sos_mail_count,
            "aok_mail_count": aok_mail_count,
            "thank_you_mail_count": thank_you_mail_count,
            "wonder_mail_count": wonder_mail_count,
            "trade_team_count": trade_team_count,
            "open_rescues_count": open_rescues_count,
            "rescue_cards": "\n".join(rescue_cards),
            "rewire_link": (
                '<li><a href="/rewire">Profile migration tool</a></li>'
                if REWIRE
                else ""
            ),
        }
        return main_template.format(**vars).encode("utf-8")


class ProfileType(Enum):
    UNKNOWN = 0
    EMAIL = 1
    DISCORD = 2

    @staticmethod
    def into_parts(combined_name: str):
        if not combined_name:
            return (ProfileType.UNKNOWN, combined_name)

        if combined_name.startswith("&discord&"):
            return (ProfileType.DISCORD, combined_name[9:])
        elif "@" in combined_name:
            return (ProfileType.EMAIL, combined_name)
        else:
            return (ProfileType.UNKNOWN, combined_name)


def format_rescue_code(rid):
    rid_str = f"{rid:012d}"
    return f"{rid_str[:4]}-{rid_str[4:8]}-{rid_str[8:]}"
