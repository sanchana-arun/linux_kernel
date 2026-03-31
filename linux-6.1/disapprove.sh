#!/bin/bash

PROC_FILE="/proc/file_open_approval"

while true; do
    STATUS=$(cat "$PROC_FILE")
    if echo "$STATUS" | grep -q "FILE OPEN PENDING"; then
        echo "$STATUS"
        echo "no" > "$PROC_FILE"
        echo "Disapproved."
        break
    fi
    sleep 0.5
done