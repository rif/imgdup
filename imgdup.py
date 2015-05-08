#! /usr/bin/env python
# inspired by: http://blog.iconfinder.com/detecting-duplicate-images-using-python/

from PIL import Image
from glob import glob
from hashlib import md5
import sys, shutil, os, argparse

DUP_FOLDER = 'duplicates'
KEEP_SUFIX = '_KEPT_'
DELETE_SUFIX = '_GONE_'
KEEP = '%s'+KEEP_SUFIX
DELETE = '%s'+DELETE_SUFIX

def dhash(image, hash_size = 8):
    # Grayscale and shrink the image in one step.
    image = image.convert('L').resize(
        (hash_size + 1, hash_size),
        Image.ANTIALIAS,
    )

    pixels = list(image.getdata())

    # Compare adjacent pixels.
    difference = []
    for row in range(hash_size):
        for col in range(hash_size):
            pixel_left = image.getpixel((col, row))
            pixel_right = image.getpixel((col + 1, row))
            difference.append(pixel_left > pixel_right)

    # Convert the binary array to a hexadecimal string.
    decimal_value = 0
    hex_string = []
    for index, value in enumerate(difference):
        if value:
            decimal_value += 2**(index % 8)
        if (index % 8) == 7:
            hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
            decimal_value = 0

    return ''.join(hex_string)

class ImgInfo:
    def __init__(self, name, size, cmp_func):
        self.name = name
        self.res = size
        self.cmp_func = cmp_func

    def __lt__(self, other):
        self_val = self.cmp_func(self)
        other_val = self.cmp_func(other)
        return self_val < other_val
    
    def __eq__(self, other):
        self_val = self.cmp_func(self)
        other_val = self.cmp_func(other)
        return self_val == other_val

class ImgHash:
    def __init__(self, val, info, sensitivity=0):
        self.val = val
        self.sensitivity = sensitivity
        self.img_info = info
        
    def __eq__(self, other):
        #Return the Hamming distance between equal-length sequences
        if len(self.val) != len(other.val):
            return false
        hamming_distance = sum(ch1 != ch2 for ch1, ch2 in zip(self.val, other.val))        
        return hamming_distance <= self.sensitivity
        

    def __hash__(self):
        return hash(self.val)
    
    def __str__(self):
        return self.val
    
def resolution(self):
    return self.res[0] * self.res[1]
    
def size(self):
    statinfo = os.stat(self.name)
    return statinfo.st_size

def compa(v1, v2, invert):
    return v1 > v2 if not invert else v2 > v1    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare images base on perceptual similarity.')
    parser.add_argument('-c','--cmp', default=resolution,
                        help='compare images by function and keep higher (resolution, size [resolution])')
    parser.add_argument('-s','--sensitivity', default=0, type=int,
                        help='how similar images must be to be considered duplicates (0 - very similar, 5 - shomehow similar)')
    parser.add_argument('-i','--invert', action='store_true',
                        help='invert the compartison function (keep lower)')
    parser.add_argument('-d','--dry_run', action='store_true',
                        help='just print the pairs')
    parser.add_argument('-u','--undo', action='store_true',
                        help='put the moved files back')
    args = parser.parse_args()

    if args.sensitivity < 0 or args.sensitivity > 5:
        print('Invalid sensitivity value %d (0, 5)', args.sensitivity)
        sys.exit(1)
    
    if args.undo:
        images = glob(os.path.join(DUP_FOLDER, '*'))
        for img_path in images:            
            if KEEP_SUFIX in img_path:
                os.remove(img_path)
            if DELETE_SUFIX in img_path:
                file_name = img_path.split(DELETE_SUFIX)[-1]
                shutil.move(img_path, file_name)
                print('recovered %s' % file_name)
        try:
            os.rmdir(DUP_FOLDER)
        except OSError: pass
        sys.exit(0)
    
    img_list = []
    images = []
    
    types = ('*.jpg', '*.png', '*.gif', '*.jpeg')
    for files in types:
        images.extend(glob(files))
        images.extend(glob(files.upper()))
    print('Found %d files.'%len(images))
    
    count = 0
    duplicates = 0
    for img_path in images:
        sys.stdout.write("\r%d%%" % (count*100/len(images)))
        sys.stdout.flush()
        count += 1
        try:
            img = Image.open(img_path)
        
            comp = getattr(sys.modules[__name__], args.cmp) if type(args.cmp) is str else args.cmp
	
            ii1 = ImgInfo(img_path, img.size, comp)
            a = ImgHash(dhash(img), ii1, args.sensitivity)
            try:
                index = img_list.index(a)
            except ValueError:
                index = -1
            if index > -1: # hamming_distance comparison using specified sensitivity
                duplicates += 1
                if not os.path.exists(DUP_FOLDER) and not args.dry_run: os.mkdir(DUP_FOLDER)
                ii2 = img_list[index].img_info
                if not args.dry_run:
                    # prefix files with the same hash to make them a pair
                    prefix = md5((ii1.name + ii2.name).encode('utf-8')).hexdigest()[:5]
                    if compa(ii1, ii2, args.invert):
                        shutil.copy(ii1.name, os.path.join(DUP_FOLDER, KEEP % prefix + ii1.name))
                        shutil.move(ii2.name, os.path.join(DUP_FOLDER, DELETE % prefix + ii2.name))
                        img_list[index] = a # new file was kept
                    else:
                        shutil.move(ii1.name, os.path.join(DUP_FOLDER, DELETE % prefix + ii1.name))
                        shutil.copy(ii2.name, os.path.join(DUP_FOLDER, KEEP % prefix + ii2.name))
                    print("\r%s and %s are too similar" % (ii2.name, ii1.name))
            else:
                img_list.append(a)
        except IOError:
            print("\rerror processing files:", sys.exc_info())

    print("\rFound %d duplicates"%duplicates)
