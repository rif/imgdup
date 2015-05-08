imgdup
======

Visual similarity image finder and cleaner (image deduplication tool).

Install
-------

```
pip install imgdup
```

or clone the repo and run imgdup.py file directly

Usage
-----

Should be run in the images folder.

It will create a `duplicates` folder containing similar file pairs indicating which file was kept and which one is gone. You can later review similar files in the `duplicates` folder and decide if you delete or restore each `_GONE_` marked file.

```shell
usage: imgdup.py [-h] [-c CMP] [-i] [-d] [-u]

Compare images base on perceptual similarity.

optional arguments:
  -h, --help         show this help message and exit
  -c CMP, --cmp CMP  compare images by function and keep higher (resolution,
                     size [resolution])
  -i, --invert       invert the compartison function (keep lower)
  -d, --dry_run      just print the pairs
  -u, --undo         put the moved files back
```

[Watch example terminal cast here](http://asciinema.org/a/19620)

WARNING
-------

Backup the image set before running this script!
