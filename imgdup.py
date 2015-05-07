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

#not used yet, can be used to compare dict values
def hamming_distance(s1, s2):
    #Return the Hamming distance between equal-length sequences
    if len(s1) != len(s2):
        raise ValueError("Undefined for sequences of unequal length")
    return sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2))

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
    parser.add_argument('-i','--invert', action='store_true',
                        help='invert the compartison function (keep lower)')
    parser.add_argument('-d','--dry_run', action='store_true',
                        help='just print the pairs')
    parser.add_argument('-u','--undo', action='store_true',
                        help='put the moved files back')
    args = parser.parse_args()    
    if args.undo:
        images = glob(os.path.join(DUP_FOLDER, '*'))
        for img_path in images:            
            if KEEP_SUFIX in img_path:
                os.remove(img_path)
            if DELETE_SUFIX in img_path:
                file_name = img_path.split(DELETE_SUFIX)[-1]
                shutil.move(img_path, file_name)
                print('recovered', file_name)
        try:
            os.rmdir(DUP_FOLDER)
        except OSError: pass
        sys.exit()
    
    img_dict = {}
    images = []
    
    types = ('*.jpg', '*.JPG', '*.png', '*.PNG')
    for files in types: images.extend(glob(files))
    
    i = 0
    for img_path in images:        
        sys.stdout.write("\r%d%%" % (i*100/len(images)))
        sys.stdout.flush()
        i+=1
        try:
            img = Image.open(img_path)
        
            comp = getattr(sys.modules[__name__], args.cmp) if type(args.cmp) is str else args.cmp
	
            ii1 = ImgInfo(img_path, img.size, comp)
            a = dhash(img)
            
            if a in img_dict:                
                if not os.path.exists(DUP_FOLDER) and not args.dry_run: os.mkdir(DUP_FOLDER)
                ii2 = img_dict[a]
                if not args.dry_run:
                    prefix = md5((ii1.name + ii2.name).encode('utf-8')).hexdigest()[:5]
                    if compa(ii1, ii2, args.invert):
                        shutil.copy(ii1.name, os.path.join(DUP_FOLDER, KEEP % prefix + ii1.name))
                        shutil.move(ii2.name, os.path.join(DUP_FOLDER, DELETE % prefix + ii2.name))
                        img_dict[a] = ii1
                    else:
                        shutil.move(ii1.name, os.path.join(DUP_FOLDER, DELETE % prefix + ii1.name))
                        shutil.copy(ii2.name, os.path.join(DUP_FOLDER, KEEP % prefix + ii2.name))
                    print("\r%s and %s are too similar" % (ii2.name, ii1.name))
            else:
                img_dict[a] = ii1
        except:
            print ("error processing files (%s, %s): %s" % (ii1.name, ii2.name, sys.exc_info()))

