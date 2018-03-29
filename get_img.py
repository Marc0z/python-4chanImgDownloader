import os
import sys
import getopt
import shutil
import time
import json
import requests
from collections import defaultdict
from pprint import pprint
from threading import Thread

# 4chan board to check
default_subsite = 'wg'

shared_img_array = None
shared_img_array = defaultdict(dict)
collecting_end = False

def main():

	collectSpecified = specifiedThreadArgs()
	directory, allThreads, subsite = gatherThreadsData(collectSpecified)

	collect = Thread(target=collectThreadInfo, args=(allThreads, subsite))
	download = Thread(target=ImgDownload, args=(directory, subsite))

	collect.start()
	download.start()
	collect.join()
	download.join()
	
	pass

def specifiedThreadArgs():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "b:t:")
	except getopt.GetoptError as err:
		print(err)
		print('get_img.py -b <board> -t <threads>')
		sys.exit(2)
	if opts:
		for o, a in opts:
			if o == "-b":
				board = a
			elif o == "-t":
				thread = a.split(',')
				thread = [element.strip() for element in thread]
				if not all(item.isdigit() for item in thread):
					raise Exception("Propper thread number not assigned")
					sys.exit(2)
			else:
				raise Exception("Unhandled option")
				sys.exit(2)
		
		return [board, thread]
	else:
		return False

def gatherThreadsData(collectSpecified):
	
	if collectSpecified:
		allThreads = collectSpecified.pop()
		subsite = collectSpecified.pop()
	else:
		try:
			r = requests.get('http://a.4cdn.org/{0}/catalog.json'.format(subsite))
		except Exception as e:
			pprint(e)

		allThreads = extractThreads(json.loads(r.content))
		subsite = default_subsite
		
	directory = os.path.abspath(os.path.dirname(sys.argv[0])) + '/4chan/{0}/'.format(subsite)

	return directory, allThreads, subsite

def collectThreadInfo(allThreads, subsite):
	global shared_img_array
	global collecting_end

	pprint('! Start collecting thread image info...')

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
					shared_img_array[thread] = [
						str(collection['tim']) + str(collection['ext'])]
				else:
					shared_img_array[thread].append(
						str(collection['tim']) + str(collection['ext']))
		pprint('+ thread ({2}) collected {0} from {1}'.format(
			str(iterator+1), str(len(allThreads)), thread))

	collecting_end = True
	pprint('! Thread image info collected...')


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


def ImgDownload(directory, subsite):
	global shared_img_array

	pprint('! Start image download from threads...')

	while True:

		if collecting_end is True and bool(shared_img_array) is False:
			pprint('!! All downloads complete!')
			break

		elif bool(shared_img_array):
			thread_content = shared_img_array.popitem()
			thread_key = thread_content[0]
			iterator = 0

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

			pprint(
				'++ from thread {0} downloaded {1} element(s)'.format(str(thread_key), str(iterator)))

		else:
			pprint('.. Collector waiting for data')
			time.sleep(2)


if __name__ == "__main__":
	main()
