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

# load cache
downloaded_sessions_cache_filename = "downloaded_sessions.txt"
with open(downloaded_sessions_cache_filename, "r") as fp: downloaded_sessions = json.loads(fp.read())

command_top = f'aws {profile} s3 ls {source_s3}/ | grep 2022-06-1'
print(command_top)
directories = subprocess.check_output(command_top, shell=True).decode().split('\n')
for _directory in tqdm(directories):
    # , desc=f"Directory {_directory.strip()[4:-1]}"
    if not _directory:
        continue
    directory = _directory.strip()[4:-1]

    # if directory < '2021-03-27':
    #     tqdm.write(f"skipping {directory}")
    #     continue

    # if directory in pictures and not directory == pictures[-1]: # and directory not in ['2019-11-19','2019-11-18']:
    #     tqdm.write(f"skipping {directory}")
    #     continue



    tqdm.write(directory)
    command = f'aws {profile} s3 sync s3://anmichel/usb/experimentos/one-way/fotos/{directory}/ {destination_dir}/{directory}/'
    tqdm.write(command)

    session_cache_name = f"{directory}"
    if session_cache_name in downloaded_sessions:
        tqdm.write(f"Directory already downloaded: {session_cache_name}")
        continue

    tqdm.write(f'Downloading direcory {session_cache_name}')
    try:

        process = subprocess.Popen(command, shell=True,
                            stdout=subprocess.PIPE,
                            universal_newlines=True)
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

    downloaded_sessions.append(session_cache_name)
    # write cache
    with open(downloaded_sessions_cache_filename, "w") as fp:
        fp.write(json.dumps(sorted(downloaded_sessions), indent=4))

