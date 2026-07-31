#!/usr/bin/env bash
set -e

ESP_A="88:57:21:2D:33:42"
ESP_B="88:57:21:2D:E1:3E"

# kill old processes
sudo pkill -f "rfcomm connect" || true

connect() {
    local IDX=$1
    local MAC=$2

    printf "[BT] Connecting rfcomm$IDX → $MAC\n"
    [ -e /dev/rfcomm0 ] && rfcomm release rfcomm0
    printf "[BT] released stale connections\n"

    while true; do
        sudo setsid rfcomm connect $IDX $MAC 1 >/tmp/rfcomm_$IDX.log 2>&1 < /dev/null &
        sleep 2

        STATE=$(rfcomm | grep "rfcomm$IDX" | tr -d '\r' || true)
        printf "[BT] rfcomm$IDX state: $STATE\n"

        if printf "$STATE" | grep -q "connected"; then
            printf "[BT] rfcomm$IDX CONNECTED\n"
            break
        fi
    done
}

connect 0 "$ESP_A"
connect 1 "$ESP_B"

# to fix any tty issues that might arise
[ -t 0 ] &&stty sane || true

printf "[BT] BOTH LINKS LIVE — safe to launch ROS\n"
