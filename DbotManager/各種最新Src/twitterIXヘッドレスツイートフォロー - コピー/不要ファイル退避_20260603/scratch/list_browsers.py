import psutil
import json

procs = []
for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
    try:
        name = proc.info['name']
        if 'chrom' in name.lower() or 'ix' in name.lower() or 'browser' in name.lower():
            procs.append(proc.info)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

print(json.dumps(procs, indent=2))
