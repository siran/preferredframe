import os
import glob
import subprocess
from pprint import pprint
from tqdm import tqdm
import traceback
import json

# configuration
destination_dir = "../tobo-ordenado"
pictures = os.listdir(destination_dir)
source_s3 = "s3://anmichel/usb/experimentos/one-way/fotos"
profile = "--profile eduweb-anrodriguez"

DATE_RANGE_MIN = '2010-05-21'
DATE_RANGE_MAX = '2030-06-19'

IGNORE_LAST_DIRECTORY = False

# load cache
downloaded_sessions_cache_filename = "downloaded_sessions.txt"
with open(downloaded_sessions_cache_filename, "r") as fp: downloaded_sessions = json.loads(fp.read())

command_top = f'aws {profile} s3 ls {source_s3}/ '
print(command_top)
directories = subprocess.check_output(command_top, shell=True).decode().split('\n')
for _directory in tqdm(directories):
    # , desc=f"Directory {_directory.strip()[4:-1]}"
    directory = _directory.strip()[4:-1]

    if "size-zero" in directory or "tobo-ordenado" in directory:
        continue

    if directory < DATE_RANGE_MIN:
        tqdm.write(f"skipping {directory}")
        continue

    if directory > DATE_RANGE_MAX:
        tqdm.write(f"skipping {directory}")
        continue

    if IGNORE_LAST_DIRECTORY:
        if directory < pictures[-1]:
            tqdm.write(f"skipping {directory}")
            continue



    tqdm.write(directory)
    command = f'aws {profile} s3 ls  s3://anmichel/usb/experimentos/one-way/fotos/{directory}/'
    tqdm.write(command)
    sub_directories = subprocess.check_output(command, shell=True).decode().split('\n')
    sub_directories = list(filter(None, sub_directories))
    for _subdirectory in tqdm(sub_directories):
        if _subdirectory == '':
            continue

        if IGNORE_LAST_DIRECTORY:
            # not transferring the last subdirectory as it might be incomplete
            if _subdirectory == sub_directories[-1] and directory == directories[-1]:
                break

        if _subdirectory[-4:] == ".jpg":
            continue

        subdirectory = _subdirectory.strip()[4:-1]

        session_cache_name = f"{directory} {subdirectory}"
        if session_cache_name in downloaded_sessions:
            tqdm.write(f"Directory already downloaded: {session_cache_name}")
            continue

        tqdm.write(f'Downloading direcory {session_cache_name}')
        command = f'aws {profile} s3 sync  --no-progress {source_s3}/{directory}/{subdirectory}/ {destination_dir}/{directory}/{subdirectory}/'
        tqdm.write(command)
        try:

            process = subprocess.Popen(command, shell=True,
                                stdout=subprocess.PIPE,
                                universal_newlines=True)
            downloaded_sessions.append(session_cache_name)

            # write cache
            with open(downloaded_sessions_cache_filename, "w") as fp:
                fp.write(json.dumps(sorted(downloaded_sessions), indent=4))

        except Exception as err:
            print(traceback.print_exc())
            continue

        while True:
            output = process.stdout.readline()
            tqdm.write(output.strip())
            # Do something else
            return_code = process.poll()
            if return_code is not None:
                # print('RETURN CODE', return_code)
                # Process has finished, read rest of the output
                for output in process.stdout.readlines():
                    print(output.strip())
                break

