""" infinite loop to sync to cloud """

import subprocess
import time


while True:
  subprocess.call("python ordenar-tobo.py", shell=True)
  subprocess.call("python sync-aws.py", shell=True)
  print('-----------------------------------------------------------')
  print('')
  print('Here we go again: 0) sleep 30m 1) ordenar-tobo, 2) sync-aws  OR ctrl-break to continue. Close window to stop program.')
  print('')
  print('-----------------------------------------------------------')
  try:
    for _ in range(30*60):
      time.sleep(1)
  except Exception:
    input('continuar'?)