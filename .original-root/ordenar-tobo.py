### ordenar archivos en tobo

import uuid
import glob
import os
from exif import Image
from pprint import pprint
from tqdm import tqdm
import shutil
import sys
import time
<<<<<<< HEAD
import traceback

print("inicio")
__SOURCE__      =  '../tobo-local'
# __SOURCE__ = '../tobo-local-duplicates'
__DESTINATION__ = '../tobo-ordenado'

srcdir = os.path.join(__SOURCE__, '**', '*.jpg')
# print(srcdir)
files = glob.glob(srcdir, recursive=True)
print(f"{len(files)} loaded")
# sys.exit()
# print(len(files))
=======
import traceback as tb

print("Ordenando el tobo de fotos...")

# source
srcdir = os.path.join('..', 'tobo', '**', '*.jpg')

# # cambio para transferir 2019
# srcdir = os.path.join('..', 'tobo-ordenado-2019-no-transferido','**', '*.jpg')

# destination
DESTINATION = 'tobo-ordenado-2019-no-transferido'
DESTINATION = 'tobo-ordenado'

print(f'{srcdir=}')
files = glob.glob(srcdir, recursive=True)
print(f'{len(files)=}')
print(files[1:10])
>>>>>>> 1a0289011a19c37f3bcfe4880a6653a66776ba59
# sys.exit()
c=0
for file in tqdm(files):
	try:
		c+=1
		src = file
		basename = os.path.basename(src)
		basedir = os.path.dirname(src)
		fsize = os.path.getsize(src)
		if fsize == 0:
			zerodir = os.path.join('..', DESTINATION, 'size-zero')
			if not os.path.exists(zerodir):
				os.mkdir(zerodir)

			dst = os.path.join(zerodir, basename)
			# print(f"{src}->{dst}")
			shutil.move(src, dst)
			continue

		image = Image(open(file,'rb'))
		# pprint(dir(image))
		# print(image)
		try:
			datetime = image.get("datetime")
			if not datetime:
				print('no date time')
				print(src)
				continue
				# break
		except KeyError:
			# tb.print_exc()
			tqdm.write(f'KeyError getting timestamp from file {file} ... skipping')
			continue

		# datetime = image.datetime
		datestr = datetime.split(" ")[0]
		timestr = datetime.split(" ")[1]
		year,month,day = datestr.split(":")
		hour,minutes,seconds = timestr.split(":")
<<<<<<< HEAD
		basedir = __DESTINATION__
=======
		
>>>>>>> 1a0289011a19c37f3bcfe4880a6653a66776ba59
		dirname = f"{year}-{month}-{day}"

		minutes = '00' if int(minutes) < 30 else '30'

		subdirname = f"n{year[-2:]}{month}{day}_{hour}{minutes}"
<<<<<<< HEAD
		dstdir = os.path.join(__DESTINATION__, dirname, subdirname)
=======
		dstdir = os.path.join('..', DESTINATION, dirname, subdirname)
		dstfilename = os.path.join(dstdir, basename)
		# tqdm.write(src)
>>>>>>> 1a0289011a19c37f3bcfe4880a6653a66776ba59
		# tqdm.write(dstdir)
		# tqdm.write(dstfilename)
		# sys.exit()

		if not os.path.exists(dstdir):
			os.makedirs(dstdir)

		try:
<<<<<<< HEAD
			# tqdm.write(f"{src}->{dstdir}")
			destinations = [
				os.path.join(dstdir, basename),
				# os.path.join(__SOURCE__, basename),
				# os.path.join(__SOURCE__, basename) + f'.{uuid.uuid1()}.jpg',
			]
			for destination in destinations:
				if not os.path.exists(destination):
					# shutil.move(src, destination)
					tqdm.write(f'gotta be moved to {destination}')
					sys.exit()
					break
			else:
				pass
				# tqdm.write('. ', end='')
				# print(f'File already exists in destination. Not doing anything. {src}')
			# sys.exit()
=======
			if not os.path.exists(dstfilename):
				# tqdm.write(f"{src}->{dstdir}")
				shutil.move(src, dstfilename)
				# sys.exit()
			else:
				print(f'File {dstfilename} already exists. Not moving {src}')
>>>>>>> 1a0289011a19c37f3bcfe4880a6653a66776ba59
		except Exception as error:
			if "already exists" in str(error):
				print(f"Ignoring error: {error}")
			else:
				traceback.print_exc()
				a=1
				# print(error)

	except Exception as err:
		tqdm.write(file)
		tqdm.write(err)
		raise(err)

