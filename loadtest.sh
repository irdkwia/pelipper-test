#!/bin/bash
URL="https://wfc.skytemple.org"

CONCURRENT_REQUESTS=50

while true; do
    echo "$(date): Sending $CONCURRENT_REQUESTS concurrent requests to $URL"

    urls=$(printf "$URL\n%.0s" $(seq 1 $CONCURRENT_REQUESTS))

    echo "$urls" | xargs -n1 -P$CONCURRENT_REQUESTS -I {} curl -o /dev/null -s -w "%{http_code} " {} | tr '\n' ' '
    echo
done