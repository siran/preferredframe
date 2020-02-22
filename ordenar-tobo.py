### ordenar archivos en tobo

import glob
import os
from exif import Image
from pprint import pprint
from tqdm import tqdm
import shutil
import sys

files = glob.glob(os.path.join('..', 'tobo','*.jpg'))
# srcdir = os.path.join('..', 'tobo-ordenado','*', '*', '*.jpg')
# print(srcdir)
# files = glob.glob(srcdir)
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
		datetime = image.get("datetime")
		if not datetime:	
			print('no date time')
			print(src)
			break

		# datetime = image.datetime
		datestr = datetime.split(" ")[0]
		timestr = datetime.split(" ")[1]
		year,month,day = datestr.split(":")
		hour,minutes,seconds = timestr.split(":")
		basedir = 'tobo-ordenado'
		dirname = f"{year}-{month}-{day}"
		
		minutes = '00' if int(minutes) < 30 else '30'

		
		subdirname = f"n{year[-2:]}{month}{day}_{hour}{minutes}"
		dstdir = os.path.join('..', basedir, dirname, subdirname)
		# tqdm.write(dstdir)
		
		if not os.path.exists(dstdir):
			os.makedirs(dstdir)
		
		try:
			# tqdm.write(f"{src}->{dstdir}")
			shutil.move(src, dstdir)
			# sys.exit()
		except Exception as error:
			if "already exists" in str(error):
				print(f"Ignoring: {error}")
		
		# if c>100:
			# break

		# break
	except Exception as err:
		tqdm.write(file)
		# tqdm.write(dir(image))
		tqdm.write(err)
		raise(err)
		
