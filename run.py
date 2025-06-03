import subprocess
import os
import time

path = os.path.dirname(os.path.abspath(__file__))

subprocess.Popen(f'start cmd /k "cd /d {path} && python server.py"', shell=True)

time.sleep(2)

subprocess.Popen(f'start cmd /k "cd /d {path} && python client.py"', shell=True)
subprocess.Popen(f'start cmd /k "cd /d {path} && python client.py"', shell=True)
