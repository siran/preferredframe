""" infinite loop to sync to cloud """

import subprocess
import time


while True:
	subprocess.call("python ordenar-tobo.py", shell=True)
	subprocess.call("python sync-aws.py", shell=True)
	time.sleep(60*10)