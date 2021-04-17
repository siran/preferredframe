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

__SOURCE__      =  '../tobo-local'
__DESTINATION__ = '../tobo-local-ordenado'

srcdir = os.path.join(__SOURCE__,'*', '*.jpg')
# print(srcdir)
files = glob.glob(srcdir, recursive=True)
# print(len(files))
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
			zerodir = os.path.join(basedir, 'size-zero')
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
		except Exception as error:
			print(error)
			# time.sleep(5)
			continue

		# datetime = image.datetime
		datestr = datetime.split(" ")[0]
		timestr = datetime.split(" ")[1]
		year,month,day = datestr.split(":")
		hour,minutes,seconds = timestr.split(":")
		basedir = __DESTINATION__
		dirname = f"{year}-{month}-{day}"

		minutes = '00' if int(minutes) < 30 else '30'


		subdirname = f"n{year[-2:]}{month}{day}_{hour}{minutes}"
		dstdir = os.path.join(__DESTINATION__, dirname, subdirname)
		# tqdm.write(dstdir)

		if not os.path.exists(dstdir):
			os.makedirs(dstdir)

		try:
			# tqdm.write(f"{src}->{dstdir}")
			destinations = [
				os.path.join(dstdir, basename),
				# os.path.join(__SOURCE__, basename),
				# os.path.join(__SOURCE__, basename) + f'.{uuid.uuid1()}.jpg',
			]
			for destination in destinations:
				if not os.path.exists(destination):
					shutil.move(src, destination)
					tqdm.write(f'moved to {destination}')
					break
			else:
				print(f'File already exists in destination. Not doing anything. {src}')
			# sys.exit()
		except Exception as error:
			if "already exists" in str(error):
				print(f"Ignoring error: {error}")

		# if c>100:
			# break

		# break
	except Exception as err:
		tqdm.write(file)
		# tqdm.write(dir(image))
		tqdm.write(err)
		raise(err)

