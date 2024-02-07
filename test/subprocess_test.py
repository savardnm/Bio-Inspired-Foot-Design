import subprocess

test_script = "/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/test/test.sh"

def main():
    print(subprocess.run([test_script], capture_output=True).stdout.decode())

if __name__ == "__main__":
    main()