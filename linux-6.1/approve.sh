#!/bin/bash

PROC_FILE="/proc/file_open_approval"

# wait for a pending request
while true; do
    STATUS=$(cat "$PROC_FILE")
    if echo "$STATUS" | grep -q "FILE OPEN PENDING"; then
        echo "$STATUS"
        read -p "Approve? (yes/no): " RESPONSE
        echo "$RESPONSE" > "$PROC_FILE"
        break
    fi
    sleep 0.5
done