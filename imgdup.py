#! /usr/bin/env python
# inspired by: http://blog.iconfinder.com/detecting-duplicate-images-using-python/

from PIL import Image
from glob import glob
import sys, shutil, os.path
import argparse

DUP_FOLDER = 'duplicates'
KEEP = '%_KEEP_'
DELETE = '%d_KEEP_'


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

    def __cmp__(self, other):
        self_val = self.cmp_func()
        other_val = other.cmp_func()
        if self_val < other.val: return -1
        elif self_val > other.val: return 1
        return 0

def resolution(self):
    return self.res[0] * self.res[1]
    
def size(self):
    statinfo = os.stat(self.name)
    return statinfo.st_size

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare images base on perceptual similarity.')
    parser.add_argument('-c','--cmp', default=resolution,
                    help='compare images by function and keep higher (default resolution)')
    parser.add_argument('-i','--invert', action='store_true',
                        help='invert the compartison function (keep lower)')
    parser.add_argument('-d','--dry_run', action='store_true',
                        help='just print the pairs')
    parser.add_argument('-u','--undo', action='store_true',
                        help='put the moved files back')
    args = parser.parse_args()
    img_dict = {}
    images = glob('*.jpg')    
    i = 0
    d = 0
    for img_path in images:        
        sys.stdout.write("\r%d%%" % (i*100/len(images)))
        sys.stdout.flush()
        i+=1
        img = Image.open(img_path)
        ii1 = ImgInfo(img_path, img.size, args.cmp)
        a = dhash(img)
        if a in img_dict:
            if not os.path.exists(dups): os.mkdir(dups)
            ii2 = img_dict[a]
            if ii1 > ii2:
                shutil.copy(ii1.name, os.path.join(DUP_FOLDER, KEEP%d + ii1.name))
                shutil.move(ii2.name, os.path.join(DUP_FOLDER, DELETE%d + ii2.name))
            else:
                shutil.move(ii1.name, os.path.join(DUP_FOLDER, DELETE%d + ii1.name))
                shutil.copy(ii2.name, os.path.join(DUP_FOLDER, KEEP%d + ii2.name))
            print("\r",ii2.name, 'and', ii1.name, 'too similar!')
            d += 1
        else:
            img_dict[a] = ii1

