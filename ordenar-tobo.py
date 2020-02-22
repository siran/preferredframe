### ordenar archivos en tobo

import glob
import os
from exif import Image
from pprint import pprint
from tqdm import tqdm
import shutil
import sys

files = glob.glob(os.path.join('tobo','*.jpg'))
# print(files[0])
# sys.exit()
c=0
for file in tqdm(files):
	try:
		c+=1
		src = file
		basename = os.path.basename(src)
		# basedir = os.path.dirname(src)
		basedir = 'tobo-ordenado'
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
		year,month,day = datestr.split(":")
		
		dirname = f"{year}-{month}-{day}"
		dstdir = os.path.join(basedir, dirname)
		if not os.path.exists(dstdir):
			os.mkdir(dstdir)
			
		
		dst = os.path.join(basedir, dirname, basename)
		# print(f"{src}->{dst}")
		shutil.move(src, dst)
		
		# if c>100:
			# break

		# break
	except Exception as err:
		print(file)
		pprint(dir(image))
		print(err)
		raise(err)
		
