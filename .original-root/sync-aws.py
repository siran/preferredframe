""" uploads photos to s3 """
import glob
import os
from exif import Image
from pprint import pprint
from tqdm import tqdm
import shutil
import sys
import subprocess
import json

dest_bucket = "s3://anmichel/usb/experimentos/one-way/fotos"

print(dest_bucket)

directories = files = glob.glob(os.path.join('..','tobo-ordenado','*'))

# # cambio para transferir 2019
# directories = files = glob.glob(os.path.join('..','tobo-ordenado-2019-no-transferido','*'))

print(len(directories))
ignore_dirs = ['size-zero']

# load cache
downloaded_sessions_cache_filename = "downloaded_sessions.txt"
with open(downloaded_sessions_cache_filename, "r") as fp: downloaded_sessions = json.loads(fp.read())

fecha_minima = '2020-05-31'
fecha_maxima = '2020-07-17'
for directory in tqdm(directories):
    if os.path.basename(directory) in ignore_dirs or "zero" in directory:
        continue

    tqdm.write(os.path.basename(directory))
    # if not fecha_minima < os.path.basename(directory) < fecha_maxima:
        # tqdm.write(f"Transferring only {fecha_minima} < date < {fecha_maxima}")
        # continue

    basedir = os.path.basename(directory)

    tqdm.write(directory)

    if directory in downloaded_sessions:
        tqdm.write(f"Directory already in cache ({downloaded_sessions_cache_filename=}): {directory}")
        continue
		
    dryrun="--dryrun"
    dryrun=""
    command = f"aws s3 {dryrun} sync {directory} {dest_bucket}/{basedir}"

    tqdm.write(command)
	
    print(f'{directory=}')
    print(f'{directories=}')
	
    a = subprocess.call(command, shell=True)
	
    if directory in downloaded_sessions:
        # dont save cache for last directory
        break

	
    # write cache
    downloaded_sessions.append(directory)
    with open(downloaded_sessions_cache_filename, "w") as fp:
        fp.write(json.dumps(sorted(downloaded_sessions), indent=4))	

    print(a)