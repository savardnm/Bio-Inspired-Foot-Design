def log(file, *args):
    with open(file, "a") as f:
        print("[Log]", *args)
        print(*args, file=f)