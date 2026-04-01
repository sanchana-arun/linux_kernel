import time
import os

PROC_FILE = "/proc/file_open_approval"
RULES_FILE = "/var/fm/f_list.txt" # Where your 'approve' command writes rules

def get_active_rules():
    """Reads the rules file and returns a dictionary of approved files/PIDs and their expiry epoch times."""
    rules = {}
    if not os.path.exists(RULES_FILE):
        return rules
        
    with open(RULES_FILE, 'r') as f:
        for line in f:
            # Expected format: [filepath] [expiry_epoch_timestamp]
            # Example: /etc/shadow 1712000000
            parts = line.strip().split()
            if len(parts) == 2:
                rules[parts[0]] = float(parts[1])
    return rules

def main():
    print(f"Starting Automated Time-Bound MAC Service...")
    
    if not os.path.exists(PROC_FILE):
        print(f"Error: Kernel module not loaded ({PROC_FILE} missing).")
        return

    while True:
        try:
            with open(PROC_FILE, 'r') as f:
                status = f.read()

            if "FILE OPEN PENDING:" in status:
                # Extract the filename from the proc output
                filename = status.split("FILE OPEN PENDING: ")[1].split("\n")[0].strip()
                
                # Load the current time-bound rules
                current_rules = get_active_rules()
                current_time = time.time()

                # Automatically evaluate the policy
                if filename in current_rules and current_time < current_rules[filename]:
                    decision = "yes"
                    print(f"[AUTO-APPROVED] {filename} (Time remaining: {int(current_rules[filename] - current_time)}s)")
                else:
                    decision = "no"
                    print(f"[AUTO-DENIED] {filename} (No active rule or time expired)")

                # Write the decision back to the kernel immediately
                with open(PROC_FILE, 'w') as f:
                    f.write(decision)
                    
        except Exception as e:
            pass # Suppress read/write collisions
            
        # Poll rapidly to minimize latency for the user
        time.sleep(0.05) 

if __name__ == "__main__":
    main()