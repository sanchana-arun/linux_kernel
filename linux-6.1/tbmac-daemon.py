import time
import os
import subprocess

PROC_FILE = "/proc/file_open_approval"
RULES_FILE = "/var/fm/active_rules.txt"

previous_state = {}

def get_active_rules():
    global previous_state
    rules_dict = {}
    current_time = time.time()

    if not os.path.exists(RULES_FILE):
        return rules_dict
        
    with open(RULES_FILE, 'r') as f:
        lines = f.readlines()

    latest_rules = {}
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            filepath = parts[0]
            expiry = float(parts[-1])
            action = "no" if "DENY" in line else "yes"
            latest_rules[filepath] = {"action": action, "expiry": expiry, "line": line}

    valid_rules = []
    modified = False

    for filepath, rule in latest_rules.items():
        prev_action = previous_state.get(filepath)
     
        if prev_action == "yes" and rule["action"] == "no":
            print(f"[REVOKED] State explicitly changed to DENY for {filepath}. Force closing...")
            subprocess.run(['fuser', '-k', '-9', filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if current_time < rule["expiry"]:
            valid_rules.append(rule["line"])
            rules_dict[filepath] = rule
        else:
            modified = True
            if rule["action"] == "yes":
                print(f"[REVOKED] Time expired for {filepath}. Force closing...")
                subprocess.run(['fuser', '-k', '-9', filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for filepath, prev_action in previous_state.items():
        if prev_action == "yes" and filepath not in latest_rules:
            print(f"[REVOKED] Rule removed for {filepath}. Force closing...")
            subprocess.run(['fuser', '-k', '-9', filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if modified or len(lines) != len(valid_rules):
        with open(RULES_FILE, 'w') as f:
            f.writelines(valid_rules)

    previous_state = {fp: r["action"] for fp, r in rules_dict.items()}

    return rules_dict

def main():    
    while True:
        try:
            current_rules = get_active_rules()

            if os.path.exists(PROC_FILE):
                with open(PROC_FILE, 'r') as f:
                    status = f.read()

                if "FILE OPEN PENDING:" in status:
                    filename = status.split("FILE OPEN PENDING: ")[1].split("\n")[0].strip()

                    if filename in current_rules:
                        rule = current_rules[filename]
                        
                        with open(PROC_FILE, 'w') as f:
                            f.write(rule["action"])
                        
                        msg = "AUTO-APPROVED" if rule["action"] == "yes" else "EXPLICIT-DENY"
                        print(f"[{msg}] {filename} (Granted by active rule)")
                    else:
                        pass
        except Exception:
            pass 
            
        time.sleep(0.5) 

if __name__ == "__main__":
    main()