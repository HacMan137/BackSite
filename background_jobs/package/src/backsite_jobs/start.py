import time
import sys
from backsite_jobs.email import EmailJobs

def start():
    print("Starting job listeners...")
    EmailJobs.start()
    while True:
        sys.stdout.flush()
        time.sleep(5)
    EmailJobs.stop()

if __name__ == "__main__":
    start()