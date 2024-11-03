# This program keeps track of how frequently we webscrape data from a website.
#  It automatically runs alongside any script that we run within the
#  "NBA Database" folder. If we send X number of requests per minute, this
#  program will place a system-wide sleep timer to prevent servers from
#  rate-limiting//IP banning us.
from collections import deque
import time
from datetime import datetime, timedelta

REQUEST_LIMIT = 20                    # Max num of requests per interval
MAX_INTERVAL = timedelta(seconds=60)  # Max seconds a request should stay in our deque
TIMEOUT = 60                          # Timeout when deque has maxed out
dq = deque()


# Adds +1 to dequeue. If oldest dequeue item is longer than 60 sec -> pop out.
#  If size of dequeue is larger than REQUEST_LIMIT -> put program to
#  sleep -> clear dequeue. Returns nothing.
def addRequest():
    currentTime = datetime.now()
    dq.appendleft(currentTime)

    while currentTime - dq[-1] > MAX_INTERVAL:  # pop expired requests
        dq.pop()

    if len(dq) >= REQUEST_LIMIT:  # Sleep if too many recent requests made
        notifyUser()
        dq.clear()
        print("DQ Requests Cleared.\n")
        time.sleep(TIMEOUT)

    return None


# Prints our DQ in a formatted way. Function usually called before
#  clearing & sleeping the DQ when it is maxed out from addRequest().
def printDQ():
    print(f"Screenshot DQ Request Stack:")
    i = 1
    for item in dq:
        print(f"{i}. {item}")
        i += 1
    return None


# Notifies user that Deque has maxed out, and we're putting the program
#  to sleep.
def notifyUser():
    print(f"\n>> MAX NUMBER OF REQUESTS MADE - TIMEOUT {TIMEOUT} SECONDS <<")
    printDQ()
    return None


# Used for testing :)
#  Fakes the number of requests made.
def fakeRequests(api_calls):
    print(f"Making {api_calls} fake api calls.")
    for i in range(api_calls):
        print(f"  > fake call #{i+1}")
        addRequest()
    return None


if __name__ == "__main__":
    print()
