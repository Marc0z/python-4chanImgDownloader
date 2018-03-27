import json
import os
import shutil
import sys
import time
from collections import defaultdict
from pprint import pprint
from threading import Thread

import requests

shared_img_array = None
#subsite = 'wg'

subsite = 'sci'
directory = os.path.abspath(os.path.dirname(sys.argv[0])) + '/4chan/{0}/'.format(subsite)
collecting_end = False
shared_img_array = defaultdict(dict)

def main(argv):

    collect = Thread( target=collectThreadInfo, args=() )
    download = Thread( target=ImgDownload, args=() )

    collect.start()
    download.start()
    collect.join()
    download.join()

    pass

def collectThreadInfo():
    global shared_img_array
    global collecting_end

    pprint('! collecting thread img data...')
    try:
        r = requests.get('http://a.4cdn.org/{0}/catalog.json'.format(subsite))
    except Exception as e:
        pprint(e)

    allThreads = extractThreads(json.loads(r.content))
    
    for iterator, thread in enumerate(allThreads):
        time.sleep(0.4)  # requested by 4chan API, or killed if 2 soon
        url = 'http://a.4cdn.org/{0}/thread/{1}.json'.format(subsite, str(thread))
        
        resp = None
        try:
            r = requests.get(url)
            resp = json.loads(r.content)
        # TODO: propper error print
        except Exception as e: 
            print(e)

        for collection in resp['posts']:
            if 'tim' in collection:
                if not thread in shared_img_array:
                    shared_img_array[thread] = [str(collection['tim']) + str(collection['ext'])]
                else:
                    shared_img_array[thread].append(str(collection['tim']) + str(collection['ext']))
        pprint('+ thread ({2}) collected {0} from {1}'.format(str(iterator), str(len(allThreads)), thread) )


    collecting_end = True
    pprint('! Thread img data collected...')

def extractThreads(jsonData):
    thr = []
    for collection in jsonData:
        for thread in collection['threads']:
            thr.append(thread['no'])
    return thr


def checkAndMakeDirectory(di):
    try:
        if not os.path.exists(di):
            os.makedirs(di)
    # TODO: propper error print
    except Exception as e:
        pprint(e)

def ImgDownload():
    pprint('! downloading img\'s from threads...')
    global shared_img_array
    
    while True:
        
        if collecting_end is True and bool(shared_img_array) is False:
            pprint('!! All downloads complete!')
            break

        elif bool(shared_img_array):
            thread_content = shared_img_array.popitem()
            thread_key = thread_content[0]
            count = 0

            if len(thread_content[1]):
                checkAndMakeDirectory(directory + str(thread_key))
            for iterator, post_img in enumerate(thread_content[1]):
                if os.path.isfile(directory + str(thread_key) + '/' + post_img):
                    continue
                try:
                    url = 'http://i.4cdn.org/{0}/{1}'.format(subsite, post_img)
                    resp = requests.get(url, stream=True)
                    with open(directory + str(thread_key) + '/' + post_img, 'wb') as out_file:
                        shutil.copyfileobj(resp.raw, out_file)
                    del resp
                # TODO: propper error print
                except Exception as e:
                    pprint(e)
                
            pprint('++ from thread {0} downloaded {1} element(s)'.format(str(thread_key), str(count+1)))
        
        else:
            pprint('?? colector empty')
            time.sleep(2)

if __name__ == "__main__":
    main(sys.argv)