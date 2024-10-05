# Pelipper Test

Python WFC re-implementation for PMD:Explorers.
And now PMD:WiiWare.

## How to use

### Pre-config

Clone this repository.
You need python3 installed.
Once installed, run `pip install -r requirements.txt`.

In `structure/constants.py`, change `SERVER_ADDR` to your server's public ip
(or local ip if you want to test it locally **Note: Never set it as 127.0.0.1 or localhost, use one of your network interface ip instead**)

**NEW:** In `structure/constants.py`, you can also select `SERVER_MODE` between `MODE_DS` and `MODE_WII` for which game you want to support. **IMPORTANT** This decision must be made at setup time, you cannot support both games with the same setup.

Run `python createdb.py` to create a new empty database. You can also run `python populatedb.py` to populate your database with some minimal data for Wonder Mail S support.

Then run `runservers.sh` or `runservers.bat` according to your operating system.

**For Python 3 users below 3.5.5**
You can alternatively run `runservers35.sh` or `runservers35.bat` according to your operating system.

**If you can't run these scripts**
Then run each of these scripts: 
- `python dnsserver.py` - Minimal DNS Server
- `python httpserver.py` - Main HTTP Server
- `python shttpserver.py` - Main HTTPS Server (forwards to HTTP for DS requests, Second HTTPS for others)
- `python shttpserver2.py` - Second HTTPS Server
- `python tcpserver.py` - TCP Server
- `python tcpserver2.py` - Second TCP Server
- `python udpserver.py` - UDP Server

If you are below 3.5.5, run `python oldshttpserver.py` instead of `python shttpserver.py`.

Your Nintendo DS system must be connected to your server setting the
DNS as the ip you set for SERVER_ADDR (which, since the NDS doesn't let
you configure it as 127.0.0.1, needs to be one of your network interface)