""" infinite loop to sync to cloud """

import subprocess
import time


while True:
  subprocess.call("python ordenar-tobo.py", shell=True)
  subprocess.call("python sync-aws.py", shell=True)
  print('Here we go again: 0) sleep 30m 1) ordenar-tobo, 2) sync-aws')
  time.sleep(30*60)


