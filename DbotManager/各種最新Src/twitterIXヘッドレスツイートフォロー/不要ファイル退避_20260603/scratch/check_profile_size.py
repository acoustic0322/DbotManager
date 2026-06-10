import os

def get_dir_size(path):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total

target = r"E:\Browser Data\237c045c90add632b1e3f431ff81843d"
size = get_dir_size(target)
print(f"Size: {size / (1024**2):.2f} MB")
