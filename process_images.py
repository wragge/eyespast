import os
import extract_features
import cv2

rootdir = '../data/articles'

for root, dirs, files in os.walk(rootdir, topdown=True):
	for file in files:
            if file[-3:] == 'jpg':
		print 'Processing %s' % os.path.join(root, file)
		try:
			extract_features.process_image(os.path.join(root, file))
		except cv2.error:
			pass