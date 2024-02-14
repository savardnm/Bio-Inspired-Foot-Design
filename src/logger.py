log_file_dir = '/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/results/'

def log(*args, file=None):
    if file==None: # if not file is provided, print and return
        print(*args)
        return
    
    file = log_file_dir + file

    with open(file, "a") as f:
        print("[Log]", *args)
        print(*args, file=f)