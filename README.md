# python-chanImgDownloader

Downloads whole img content of a board <br />
Dir is created @ script location <br />
Excludes already downloaded files so it's able to update a library (executed by cron maybe?) <br />
Set by default on /wg/ board <br />

## Update 29.03
Script is now able to download a specified thread or threads from set board:
```
get_img.py -b <board> -t <threads IDs>
```
so by running:
```
> python get_img.py -b wg -t 7356456,3546345
```
You will fetch 2 threads from /wg/
