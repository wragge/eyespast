import requests
import re
import shutil
from trove_python.trove_core import trove
from trove_python.trove_harvest.harvest import TroveHarvester
import credentials


class PageHarvester(TroveHarvester):

	def process_results(self, results):
		'''
		Processes a page full of results.
		Saves a page image for each result.
		'''
		try:
			articles = results[0]['records']['article']
			for article in articles:
				date = article['date'].replace('-', '')
				title_id = article['title']['id']
				if isinstance(article['pdf'], list):
					for link in article['pdf']:
						self.save_page(link, date, title_id)
				else:
					self.save_page(article['pdf'], date, title_id)
			self.harvested += self.get_highest_n(results)
			print 'Harvested: {}'.format(self.harvested)
		except KeyError:
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

