import time
from termcolor import colored

start = time.time()
number = 0
for i in range(100000000):
    number +=i
print(colored("finished","green"))
print(f"ellapsed time:{time.time()-start}s")
