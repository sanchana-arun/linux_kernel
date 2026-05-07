#!/bin/bash
# Usage: approve [filename] [seconds]

FILE=$1
SECONDS=$2
CURRENT_TIME=$(date +%s)
EXPIRY_TIME=$(($CURRENT_TIME + $SECONDS))

# Write the rule to the file the daemon is watching
echo "$FILE $EXPIRY_TIME" >> /var/fm/active_rules.txt
echo "Rule added: $FILE is approved for $SECONDS seconds."
