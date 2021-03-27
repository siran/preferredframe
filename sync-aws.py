""" uploads photos to s3 """
import glob
import os
from exif import Image
from pprint import pprint
from tqdm import tqdm
import shutil
import sys
import subprocess

dest_bucket = "s3://anmichel/usb/experimentos/one-way/fotos"

print(dest_bucket)

directories = files = glob.glob(os.path.join('..','tobo-ordenado','*'))
print(len(directories))
ignore_dirs = ['size-zero']
fecha_minima = '2021-03-06'
for directory in tqdm(directories):
	if os.path.basename(directory) in ignore_dirs:
		continue

	tqdm.write(os.path.basename(directory))
	if os.path.basename(directory) < fecha_minima:
		tqdm.write(f"Transferring only > {fecha_minima}")
		continue

	basedir = os.path.basename(directory)

	tqdm.write(directory)
	dryrun="--dryrun"
	dryrun=""
	command = f"aws s3 {dryrun} sync {directory} {dest_bucket}/{basedir}"

	tqdm.write(command)

	# sys.exit()


	a = subprocess.call(command, shell=True)
	# p = subprocess.Popen('dir ..', stdout=subprocess.PIPE, stderr = None, shell=True)

	# for line in iter(p.stdout.readline, ''):
		# print(line)
		# input()

	# p.stdout.flush()
	# p.stdout.close()

	# print ("Done")
	print(a)