#!/bin/bash

python3 dnsserver.py &
DNS_PID=$!
python3 oldshttpserver.py &
HTTP_PID=$!
python3 shttpserver.py &
SHTTP_PID=$!
python3 tcpserver.py &
TCP_PID=$!
python3 tcpserver2.py &
TCP2_PID=$!
python3 udpserver.py &
UDP_PID=$!

stop_servers() {
    echo "Stopping servers..."
    kill $DNS_PID $HTTP_PID $SHTTP_PID $TCP_PID $TCP2_PID $UDP_PID
    wait $DNS_PID $HTTP_PID $SHTTP_PID $TCP_PID $TCP2_PID $UDP_PID
    echo "Servers stopped."
}

# Trap SIGINT (Ctrl+C) signal and call stop_servers function
trap stop_servers SIGINT

# Wait for all background processes to finish
wait