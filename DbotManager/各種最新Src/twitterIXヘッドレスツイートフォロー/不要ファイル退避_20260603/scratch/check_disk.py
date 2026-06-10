import shutil
import os

def get_disk_usage(path):
    total, used, free = shutil.disk_usage(path)
    print(f"Path: {path}")
    print(f"Total: {total / (1024**3):.2f} GB")
    print(f"Used: {used / (1024**3):.2f} GB")
    print(f"Free: {free / (1024**3):.2f} GB")
    print(f"Usage: {used/total:.2%}")

get_disk_usage("C:")
get_disk_usage("E:")
