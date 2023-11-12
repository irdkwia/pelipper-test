# Pelipper Test

Python WFC re-implementation for PMD:Explorers.

## How to use

### Pre-config

Clone this repository.
You need python3 installed.
Once installed, run `pip install -r requirements.txt`.

In `structure/constants.py`, change SERVER_ADDR to your server's public ip
(or local ip if you want to test it locally **Note: Never set it as 127.0.0.1 or localhost, use one of your network interface ip instead**)

Run `python createdb.py` to create a new empty database.

Then run `runservers.sh` or `runservers.bat` according to your operating system.

**For Python 3 users below 3.5.5**
You can alternatively run `runservers35.sh` or `runservers35.bat` according to your operating system.

**If you can't run these scripts**
Then run each of these scripts: 
- `python dnsserver.py` - Minimal DNS Server
- `python httpserver.py` - Main HTTP Server
- `python shttpserver.py` - HTTPS Server (redirects to HTTP)
- `python tcpserver.py` - TCP Server
- `python tcpserver2.py` - Second TCP Server
- `python udpserver.py` - UDP Server

If you are below 3.5.5, run `python oldshttpserver.py` instead of `python shttpserver.py`.

Your Nintendo DS system must be connected to your server setting the
DNS as the ip you set for SERVER_ADDR (which, since the NDS doesn't let
you configure it as 127.0.0.1, needs to be one of your network interface)