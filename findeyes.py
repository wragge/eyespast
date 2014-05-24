import os
import re
import time
from datetime import datetime
from pymongo import MongoClient, GEO2D
import requests
from credentials import TROVE_API_KEY
import calendar
import random

rootdir = '../data/crops2'

def populate_db():
	'''
	Populates a Mongo database with metadata from the filenames
	of the faces and eyes located in rootdir.
	'''
	for root, dirs, files in os.walk(rootdir, topdown=True):
		client = MongoClient()
		db = client.findeyes2
		faces = db.faces
		faces.remove()
		faces.ensure_index([('random_id', GEO2D)])
		for f in files:
			f_name, ext = os.path.splitext(f)
			if ext == '.jpg':
				print 'Processing {}'.format(f_name)
				details = f_name.split('-')
				date_str = details[0]
				title_id = details[1]
				article_id = details[2]
				face_id = details[3]
				eye_id = details[4]
				if eye_id == '0':
					#face['eyes'] = face['eyes'].append(eye_id)
					date_obj = datetime(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8]))
					f_date = '{} {} {}'.format(date_str[6:8].lstrip('0'), calendar.month_abbr[int(date_str[4:6])], date_str[:4])
					print date_obj
					r = requests.get('http://api.trove.nla.gov.au/newspaper/title/{}?encoding=json&key={}'.format(title_id, TROVE_API_KEY))
					results = r.json()
					title = results['newspaper']['title']
					title = re.search(r'(.*)\(.*\)', title).group(1).strip()
					face = {}
					face['_id'] = '{}-{}'.format(article_id, face_id)
					face['image'] = f_name[:-1]
					face['date'] = date_obj
					face['f_date'] = f_date
					face['article_id'] = article_id
					face['title'] = title
					face['face_id'] = face_id
					face['eyes'] = []
					face['random_id'] = [random.random(), 0]
					faces.save(face)
					time.sleep(1)
				else:
					faces.update({'_id': '{}-{}'.format(article_id, face_id)}, { '$push': {'eyes': eye_id}}, True)