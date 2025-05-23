import subprocess
import time
import sys

CMD = ["ngrok", "http", "--url=intimate-certain-sloth.ngrok-free.app", "5001"]

def run():
    print("Starting ngrok...")
    while True:
        # Start the process
        proc = subprocess.Popen(CMD)

        # Wait for the process to terminate
        proc.wait()

        # If the process ended, restart it
        print("ngrok process exited. Restarting in 3 seconds...")
        time.sleep(3)

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\nScript stopped by user.")
        sys.exit(0)