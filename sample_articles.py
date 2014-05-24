import requests
import re
import shutil
from trove_python.trove_core import trove
from trove_python.trove_harvest.harvest import TroveHarvester
import credentials
from bs4 import BeautifulSoup
from PIL import Image
import cStringIO

class PageHarvester(TroveHarvester):

	def process_results(self, results):
		'''
		Processes a page full of results.
		Saves image for each result.
		'''
		try:
			articles = results[0]['records']['article']
			for article in articles:
				try:
					#Check it's online
					url = article['troveUrl']
				except KeyError:
					pass
				else:
					self.save_image(article)
			self.harvested += self.get_highest_n(results)
			print 'Harvested: {}'.format(self.harvested)
		except KeyError:
			pass

	def save_image(self, article):
		'''
		Scrapes image urls from 'jpg' page in web ui.
		If there are multiple images, stitches them together.
		'''
		id = article['id']
		date = article['date'].replace('-', '')
		title_id = article['title']['id']
		url = 'http://trove.nla.gov.au/ndp/del/printArticleJpg/{}/5'.format(id)
		response = requests.get(url)
		soup = BeautifulSoup(response.text)
		images = soup.find_all('img')
		image_filename = '../data/articles/{}-{}-{}.jpg'.format(date, title_id, id)
		if len(images) == 1:
			img_src = images[0]['src']
			img_url = 'http://trove.nla.gov.au{}'.format(img_src)
			response = requests.get(img_url, stream=True)
			with open(image_filename, 'wb') as out_file:
				shutil.copyfileobj(response.raw, out_file)
			del response
		else:
			# Stitch together multiple images
			parts = []
			total_height = 0
			width = 0
			last = len(images) - 1
			for index, image_part in enumerate(images):
				part_src = image_part['src']
				part_url = 'http://trove.nla.gov.au{}'.format(part_src)
				print part_url
				response = requests.get(part_url)
				print response.status_code
				try:
					img = Image.open(cStringIO.StringIO(response.content))
				except IOError:
					del response
				else:
					width, height = img.size
					if height == 900 and index != last:
						img = img.crop((0, 0, width, height-20))
						height = 880
					parts.append((img, height))
					total_height += height
					del response
			combined_image = Image.new('RGB', (width, total_height))
			y_offset = 0
			for part in parts:
				combined_image.paste(part[0], (0, y_offset))
				y_offset += part[1]
			try:
				combined_image.save(image_filename)
			except SystemError:
				pass

	def save_page(self, pdf_link, date, title_id):
		url = pdf_link.replace('print', 'level3')
		page_id = re.search(r'page(\d+)', pdf_link).group(1)
		response = requests.get(url, stream=True)
		with open('../data/pages/{}-{}-{}.jpg'.format(date, title_id, page_id), 'wb') as out_file:
			shutil.copyfileobj(response.raw, out_file)
		del response
		#process_image('data/pages/{}.jpg'.format(page_id))

def do_harvest():
	query = 'http://api.trove.nla.gov.au/result?zone=newspaper&l-category=Article&l-word=0&l-illustrated=y&l-illtype=photo&encoding=json&reclevel=full'
	for year in range(1870, 1955):
		year_query = '{}&q=date:[{year}+TO+{year}]'.format(query, year=year)
		trove_api = trove.Trove(credentials.TROVE_API_KEY)
		harvester = PageHarvester(trove_api, query=year_query)
		harvester.number = 100
		harvester.maximum = 200
		harvester.harvest()

