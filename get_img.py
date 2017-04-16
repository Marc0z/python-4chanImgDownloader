import os
import requests
import time
import json
import sys
import shutil
from pprint import pprint
from collections import defaultdict


def checkAndMakeDirectory(di):
    if not os.path.exists(di):
        os.makedirs(di)


subsite = 'wg'
directory = os.path.abspath(os.path.dirname(sys.argv[0])) + '/4chan/' + subsite + '/'
img_arr = defaultdict(dict)

r = requests.get('http://a.4cdn.org/' + subsite + '/catalog.json')
json_d = json.loads(r.content)

thread_arr = []
for collection in json_d:
    for thread in collection['threads']:
        thread_arr.append(thread['no'])
del json_d

pprint('! collecting thread img data...')

tCount = 0
for thread in thread_arr:
    tCount += 1
    time.sleep(0.4)  # requested by 4chan API, or killed if 2 soon
    try:
        url = 'http://a.4cdn.org/' + subsite + '/thread/' + str(thread) + '.json'
        r_inner = requests.get(url)
        json_d = json.loads(r_inner.content)
        pCount = 0
        for collection in json_d['posts']:
            if 'tim' in collection:
                img_arr[thread][pCount] = str(collection['tim']) + str(collection['ext'])
                pCount += 1
        pprint('thread ' + str(tCount) + ' from ' + str(len(thread_arr)) + ' done')
    # TODO: propper error print
    except Exception:
        pprint(Exception)

pprint('! downloading img\'s from threads...')

checkAndMakeDirectory(directory)

tDoneCount = 0
for key, thread_content in img_arr.iteritems():
    if len(thread_content):
        checkAndMakeDirectory(directory + str(key))
    for iterator, post_img in thread_content.iteritems():
        if os.path.isfile(directory + str(key) + '/' + post_img):
            continue
        try:
            url = 'http://i.4cdn.org/' + subsite + '/' + post_img
            response = requests.get(url, stream=True)
            with open(directory + str(key) + '/' + post_img, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
        # TODO: propper error print
        except Exception:
            pprint(Exception)
    tDoneCount += 1
    pprint('thread ' + str(tDoneCount) + ' from ' + str(len(thread_arr)) + ' downloaded')
