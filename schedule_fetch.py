import subprocess
import datetime

# Log the execution time
current_time = datetime.datetime.now()
print(f"Running smart_fetch.py at {current_time}")

# Run smart_fetch.py
subprocess.run(["python3", "smart_fetch.py"])
