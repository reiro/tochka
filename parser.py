#!/usr/bin/env python                                                                                                                                                                
import os
import sys
import requests
import bs4
import django
import pdb
from multiprocessing.dummy import Pool
from datetime import datetime

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '../tochka_test/')))
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '../tochka_test/shares/')))
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '../tochka_test/tochka_test/')))


os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
django.setup()

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from shares.models import *

class BasicScraper(object):
	def __init__(self, filename, pool_size=1):
		self.tickers_path = os.path.join(settings.BASE_DIR, filename)
		self.base_uri = 'https://www.nasdaq.com/symbol/'
		self.pool = Pool(pool_size)

	def convert_date(self, date):
		try:	
			d = datetime.datetime.strptime(date, '%m/%d/%Y')
		except:
			d = datetime.date.today()

		return d.strftime('%Y-%m-%d')

	def FloatOrZero(self, value):
	    try:
	        return float(value)
	    except:
	        return 0.0

	def clear_value_format(self, row, num):
		return row.select('td')[num].get_text().split()[0].replace(',', '')

	def run(self):
		file = open(self.tickers_path)
		names = [line.split()[0] for line in file]
		file.close()
		self.pool.map(self.scrape, names)
		self.pool.close()
		self.pool.join()

	def scrape(self, name):
		pass

class Scraper(BasicScraper):
	def __init__(self, filename, pool_size=1):
		super().__init__(filename, pool_size)
		self.scrape_suffix = '/historical'

	def scrape(self, name):
		share, created = Share.objects.get_or_create(name=name)
		url = self.base_uri + name + self.scrape_suffix
		print('scraping... ' + url)

		response = requests.get(url)
		soup = bs4.BeautifulSoup(response.text, "html.parser")
		for row in soup.select('div#historicalContainer table tbody tr'):
			if len(row.select('td')[0].get_text().split()) == 0:
				continue

			trade_histiry_data = {'share_id': share.id}
			trade_histiry_data['date'] = self.convert_date(row.select('td')[0].get_text().split()[0])
			trade_histiry_data['open'] = float(self.clear_value_format(row, 1))
			trade_histiry_data['high'] = float(self.clear_value_format(row, 2))
			trade_histiry_data['low'] = float(self.clear_value_format(row, 3))
			trade_histiry_data['close'] = float(self.clear_value_format(row, 4))
			trade_histiry_data['volume'] = int(self.clear_value_format(row, 5))

			event, created = TradeEvent.objects.get_or_create(**trade_histiry_data)


class InsiderScraper(BasicScraper):
	def __init__(self, filename):
		super().__init__(filename)
		self.scrape_suffix = '/insider-trades'

	def scrape(self, name):
		self.page = 1
		self.share, created = Share.objects.get_or_create(name=name)
		url = self.base_uri + name + self.scrape_suffix
		print('scrapping... ' + url)

		response = requests.get(url)
		page = bs4.BeautifulSoup(response.text, "html.parser")
		self.grab_page(page, self.share)

		link = page.select('a#quotes_content_left_lb_NextPage')[0]
		self.scrape_recursive(link)

	def scrape_recursive(self, link):
		self.page += 1
		print('scrapping... ' + link['href'])
		response = requests.get(link['href'])
		page = bs4.BeautifulSoup(response.text, "html.parser")
		self.grab_page(page, self.share)
		links = page.select('a#quotes_content_left_lb_NextPage')

		if self.page < 10 and len(links) > 0:
			self.scrape_recursive(links[0])

	def grab_page(self, page, share):
		for row in page.select('div.genTable table tr'):
			if len(row.select('td')) == 0:
				continue

			insider_name = row.select('td')[0].get_text()
			relation = row.select('td')[1].get_text()
			insider, created = Insider.objects.get_or_create(name=insider_name, relation=relation)

			trade_histiry_data = {'share_id': share.id, 'insider_id': insider.id}
			trade_histiry_data['date'] = self.convert_date(row.select('td')[2].get_text())
			trade_histiry_data['transaction_type'] = row.select('td')[3].get_text()
			trade_histiry_data['owner_type'] = row.select('td')[4].get_text()
			trade_histiry_data['shares_traded'] = int(row.select('td')[5].get_text().replace(',', ''))
			trade_histiry_data['last_price'] = self.FloatOrZero(row.select('td')[6].get_text())
			trade_histiry_data['shares_held'] = int(row.select('td')[7].get_text().replace(',', ''))
			
			event, created = InsiderTradeEvent.objects.get_or_create(**trade_histiry_data)


if __name__ == '__main__':
	if len(sys.argv) == 2:
		threads_count = int(sys.argv[1])
	else:
		threads_count = 1

	scraper = Scraper('tickers.txt', threads_count)
	scraper.run()

	insider_scraper = InsiderScraper('tickers.txt')
	insider_scraper.run()
