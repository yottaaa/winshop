from requests_html import HTML
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.service import Service
import pandas as pd
import numpy as np
from time import sleep
from datetime import datetime
import os

'''

Classes for scraping Online Shops.

'''
class AmazonScrape:

	def __init__(self, keyword):
		self.keyword = keyword
		self.shop = "amazon"
		self.base_url = 'https://www.amazon.com'
		chrome_options = Options()

		# set chrome driver options to disable any popup's from the website
		# to find local path for chrome profile, open chrome browser
		# and in the address bar type, "chrome://version"
		chrome_options.binary_location = os.environ['GOOGLE_CHROME_BIN']
		chrome_options.add_argument('disable-notifications')
		chrome_options.add_argument('--disable-infobars')
		chrome_options.add_argument('start-maximized')
		chrome_options.add_argument("--headless")
		chrome_options.add_argument("--log-level=0")

		self.browser = webdriver.Chrome(
			executable_path=os.environ['CHROME_WEBDRIVER'],
			options=chrome_options
		)
		self.browser.get(self.base_url)

		WebDriverWait(self.browser, 5)

		self.search_el = self.browser.find_element(By.ID, 'twotabsearchtextbox')
		self.search_el.send_keys(self.keyword)
		self.search_el.send_keys(Keys.RETURN)
		print(f'Searching for "{self.keyword}" on {self.base_url}')

		self.result = list()

	def ranking(self, res) -> list:
		pass 

	def check_float(self, deci) -> bool:
		try:
			float(deci)
			return True
		except ValueError:
			return False

		return False

	def search_result(self):
		product_img = ''
		product_link = ''
		product_name = ''
		product_price = ''
		product_ratings_avg = 0.0
		product_ratings_count = 0
		product_price_currency = ''

		# get products
		amazon_search_result = HTML(html=self.browser.page_source)
		products = amazon_search_result.find('div[data-component-type="s-search-result"]')

		for product in products:
			# get the product name
			name_el = product.find('a.a-link-normal.s-link-style.a-text-normal', first=True)
			if name_el != None:
				product_name = name_el.full_text

			# get the product link
			link_el = product.find('a.a-link-normal.s-link-style.a-text-normal', first=True)
			if link_el != None:
				product_link = self.base_url + link_el.attrs['href']

			# get img url
			img_el = product.find('img.s-image', first=True)
			if img_el != None:
				product_img = img_el.attrs['src']

			# get ratings
			ratings_el = product.find('span[aria-label]')
			if ratings_el != None:
				if len(ratings_el) == 2:
					# get the average ratings
					r_avg = ratings_el[0].attrs['aria-label'].split()[0]
					if self.check_float(r_avg) == True:
						product_ratings_avg = r_avg
					# get the ratings count
					r_count = ratings_el[1].attrs['aria-label'].replace(',','')
					product_ratings_count = r_count


			# get the price
			price_el = product.find('span.a-price')
			if price_el != None:
				if len(price_el) == 2:
					# get the whole price
					w_price = price_el[0].full_text
					product_price = w_price
					# get the currency
					product_price_currency = w_price[0]

			if product_img != '' and \
				product_name != '' and \
				product_link != '' and \
				product_ratings_avg != 0.0 and \
				product_ratings_count != 0 and \
				product_price != '' and \
				product_price_currency != '':
				self.result.append(
					{
						'name': product_name,
						'img_url': product_img,
						'link': product_link,
						'ratings_avg': float(product_ratings_avg),
						'ratings_count': int(product_ratings_count),
						'price': product_price,
						'currency': product_price_currency,
						'source': self.base_url
					}
				)
		
		print(f'Done scraping {self.base_url}')

	def get_result(self) -> list:
		return self.result

	def convert_to_csv(self):
		# convert search result to csv file
		products_df = pd.DataFrame.from_dict(self.result)
		products_df.to_csv(
			f'{self.shop}_search_{"_".join(self.keyword.split("+"))}.csv', 
			index=False, 
			header=True
		)

class LazadaScrape:

    def __init__(self, keyword):
        self.keyword = keyword
        self.shop = 'lazada'
        self.base_url = 'https://www.lazada.com.ph'
        chrome_options = Options()
        chrome_options.binary_location = os.environ['GOOGLE_CHROME_BIN']
        chrome_options.add_argument('disable-notifications')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('start-maximized')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=0")

        self.browser = webdriver.Chrome(
			executable_path=os.environ['CHROME_WEBDRIVER'],
			options=chrome_options
		)
        self.browser.get(self.base_url)

        self.search_el = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, 'q'))
        )
        self.search_el.send_keys(self.keyword)
        self.search_el.send_keys(Keys.RETURN)
        print(f'Searching for "{self.keyword}" on {self.base_url}')
        
        self.result = list()

    def convert_to_int(self,str_) -> int:
        to_num = str_.split()[0]
        num = 0
        if to_num.isalpha() != True:
            num = to_num
        return num

    # convert ratings count to int
    def convert_ratings_count_int(self, ratings_count) -> int:
        try:
            remove_str = {'ratings':'','Ratings':'','.':'','K':'00'}
            
            for k,v in remove_str.items():
                ratings_count = ratings_count.replace(k,v)
                
            return int(ratings_count)
        except ValueError:
            return 0
		
        return 0

    def convert_to_csv(self):
		# convert search result to csv file
        products_df = pd.DataFrame.from_dict(self.result)
        products_df.to_csv(
			f'{self.shop}_search_{"_".join(self.keyword.split("+"))}.csv', 
			index=False, 
			header=True
		)

    def search_result(self):
        product_img = ''
        product_link = ''
        product_name = ''
        product_price = ''
        product_ratings_avg = 0.0
        product_ratings_count = 0
        product_price_currency = ''

        # get products
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-qa-locator="general-products"]'))
        )
        sleep(3)
        lazada_search_result = HTML(html=self.browser.page_source)
        products = lazada_search_result.find('div[data-qa-locator="product-item"]')
        for product in products:
            # get the product image
            img_el = product.find('img.jBwCF', first=True)
            if img_el != None:
                product_img = f'https:{img_el.attrs["src"]}'

            # get the product name
            name_el = product.find('a[title]', first=True)
            if name_el != None:
                product_name = name_el.full_text

            # get the product link
            link_el = product.find('a[title]', first=True)
            if link_el != None:
                product_link = f'https:{link_el.attrs["href"]}'

            # redirect to product page
            sleep(2)
            self.browser.get(product_link)
            ratings_el = WebDriverWait(self.browser, 20).until(
                EC.presence_of_element_located((By.ID, 'module_product_review'))
            )
            ratings_el.location_once_scrolled_into_view
            sleep(2)
            product_page_source = HTML(html=self.browser.page_source)
            
            # get the ratings average
            ratings_avg = product_page_source.find('span.score-average', first=True)
            if ratings_avg != None:
                product_ratings_avg = float(ratings_avg.full_text)

            # get the ratings count
            ratings_count = product_page_source.find('div.count', first=True)
            if ratings_count != None:
                product_ratings_count = self.convert_ratings_count_int(ratings_count.full_text)

            # get the whole price and currency
            price = product_page_source.find('span.pdp-price.pdp-price_type_normal.pdp-price_color_orange.pdp-price_size_xl', first=True)
            if price != None:
                product_price = price.full_text
                product_price_currency = product_price[0]

            if product_img != '' and \
                product_name != '' and \
                product_link != '' and \
                product_ratings_avg != 0.0 and \
                product_ratings_count != 0 and \
                product_price != '' and \
                product_price_currency != '':
                self.result.append(
                    {
                        'name': product_name,
                        'img_url': product_img,
                        'link': product_link,
                        'ratings_avg': float(product_ratings_avg),
                        'ratings_count': int(product_ratings_count),
                        'price': product_price,
                        'currency': product_price_currency,
                        'source': self.base_url
                    }
                )

        print(f'Done scraping {self.base_url}')

    def get_result(self) -> list:
        return self.result

    # convert scrape data to csv file
    def convert_to_csv(self):
        products_df = pd.DataFrame.from_dict(self.result)
        products_df.to_csv(
            f'{self.shop}_search_{"_".join(self.keyword.split())}.csv', 
            index=False, 
            header=True
        )

class ShopeeScrape:

	def __init__(self, keyword):
		self.keyword = keyword
		self.shop = 'shopee'
		self.base_url = 'https://shopee.ph'
		webdrive_service = Service(os.environ.get('CHROME_WEBDRIVER'))
		chrome_options = Options()

		# set chrome driver options to disable any popup's from the website
		# to find local path for chrome profile, open chrome browser
		# and in the address bar type, "chrome://version"
		chrome_options.binary_location = os.environ['GOOGLE_CHROME_BIN']
		chrome_options.add_argument('disable-notifications')
		chrome_options.add_argument('--disable-infobars')
		chrome_options.add_argument('start-maximized')
		chrome_options.add_argument("--headless")
		chrome_options.add_argument("--log-level=0")

		self.browser = webdriver.Chrome(
			executable_path=os.environ.get('CHROME_WEBDRIVER'),
			options = chrome_options
		)
		self.browser.get(f'{self.base_url}/search?keyword={self.keyword}')
		self.delay = 3 #secods

		WebDriverWait(self.browser, self.delay)
		print(f'Searching for "{self.keyword}" on {self.base_url}')
		sleep(3)

		self.result = list()

	# to check if the element has the specific attribute
	def check_attr(self, el, attr):
		try:
			el.attrs[attr]
			return True
		except KeyError:
			return False

		return True

	# convert ratings count to int
	# convert ratings count to int
	def convert_ratings_count_int(self, ratings_count) -> int:
		try:
			remove_str = {'ratings':'','.':'','K':'00'}
            
			for k,v in remove_str.items():
				ratings_count = ratings_count.replace(k,v)
            
			return int(ratings_count)
		except ValueError:
			return 0
		
		return 0


	# search result
	def search_result(self):
		product_img = ''
		product_name = ''
		product_link = ''
		product_ratings_count = ''
		product_ratings_avg = 0
		product_price = ''
		product_price_currency = ''
		
		# html = browser.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
		shopee = self.browser.page_source

		# get products
		shopee_search_result = HTML(html=shopee)
		products = shopee_search_result.find('a[data-sqe="link"]')


		for product in products:
			# get product url
			link_el = product.find('a[data-sqe="link"]', first=True)
			if link_el != None:
				product_link = self.base_url + link_el.attrs['href']

			# get name
			name_el = product.find('div[data-sqe="name"]', first=True)
			if name_el != None:
				product_name = name_el.full_text

			price_el = product.find('div._3_FVSo', first=True)
			if price_el != None:
				product_price = price_el.full_text
				product_price_currency = price_el.full_text[0]

			sleep(2)
			# get thumbnail image
			img_el = product.find('img._3-N5L6', first=True)
			if self.check_attr(img_el, 'src'):
				product_img = img_el.attrs['src']

			# redirect to the product to get the ratings
			self.browser.get(product_link)
			WebDriverWait(self.browser, self.delay)
			sleep(3)
			s_ratings = self.browser.page_source
			shopee_product_ratings = HTML(html=s_ratings)
			ratings = shopee_product_ratings.find('div.flex._1GknPu')

			if len(ratings) == 0:
				continue
			else:
				# get ratings avg
				product_ratings_avg = float(ratings[0].full_text)

				# get ratings count
				product_ratings_count = self.convert_ratings_count_int(ratings[1].full_text)

			self.result.append(
				{
					'name': product_name,
					'img_url': product_img,
					'link': product_link,
					'ratings_avg': float(product_ratings_avg),
					'ratings_count': int(product_ratings_count),
					'price': product_price,
					'currency': product_price_currency,
					'source': self.base_url
				}
			)

		print(f'Done scraping {self.base_url}')

	def get_result(self) -> list:
		return self.result 

	# convert scrape data to csv file
	def convert_to_csv(self):
		products_df = pd.DataFrame.from_dict(self.result)
		products_df.to_csv(
			f'{self.shop}_search_{"_".join(self.keyword.split())}.csv', 
			index=False, 
			header=True
		)


'''

This is the api for extract, cleaning, and loading data from
scraping Online Shops.

'''
def bayes_average(r_count, r_avg, c, m) -> float:
	return float((r_count*r_avg + m*c)/(r_count+c))

def convert_to_csv(keyword,lst):
	new_df = pd.DataFrame.from_dict(lst)
	new_df.to_csv(
		f'results\\olshop_search_{"_".join(keyword.split())}_{datetime.now().strftime("%m%d%Y_%H%M%S")}.csv', 
		index=False, 
		header=True
	)
	print('\nconvert to csv done.')

def transformed_data(df) -> dict:
	
	products = list()
	count = 0

	# insert the sorted data with bayes average
	data = list()
	m = df['ratings_avg'].mean()
	c = np.percentile(
		[row.ratings_count for row in df.itertuples()], 
		25
	)
	for row in df.itertuples():
		b_avg = bayes_average(row.ratings_count,row.ratings_avg,c,m)
		data.append(
			{
				'name': row.name,
				'img_url': row.img_url,
				'link': row.link,
				'ratings_avg': row.ratings_avg,
				'ratings_count': row.ratings_count,
				'bayes_avg': b_avg,
				'price': row.price,
				'currency': row.currency,
				'source': row.source
			}
		)

	# sort data by bayes average
	data_df = pd.DataFrame.from_dict(data)
	data_df = data_df.sort_values(by='bayes_avg', ascending=False)

	# insert new data
	for idx, row in enumerate(data_df.itertuples()):
		products.append(
			{
				'id': idx,
				'name': row.name,
				'img_url': row.img_url,
				'link': row.link,
				'ratings_avg': row.ratings_avg,
				'ratings_count': row.ratings_count,
				'bayes_avg': row.bayes_avg,
				'price': row.price,
				'currency': row.currency,
				'source': row.source
			}
		)



	return {
		'products': products,
		'count': len(products)
	}

def clean_data(raw_data) -> list:
	new_data = []
	for item in raw_data:
		if item['name'] != '' and \
			item['link'] != '' and \
			item['ratings_avg'] != 0.0 and \
			item['ratings_count'] != 0 and \
			item['price'] != '' and \
			item['currency'] != '':
			new_data.append(item)

	return new_data

def search(keyword) -> dict:
	result = []

	# scraping
	amz = AmazonScrape(keyword)
	amz.search_result()
	amz.browser.quit()
	result += amz.get_result()
	sleep(2)
	shp = ShopeeScrape(keyword)
	shp.search_result()
	shp.browser.quit()
	result += shp.get_result()
	sleep(2)
	laz = LazadaScrape(keyword)
	laz.search_result()
	laz.browser.quit()
	result += laz.get_result()
	sleep(2)

	# clean data
	# cleaned_data = clean_data(result)
	cleaned_data = result

	# convert result to a dataframe
	olshop_df = pd.DataFrame.from_dict(cleaned_data)

	# sort by ratings count
	olshop_df = olshop_df.sort_values(by='ratings_count', ascending=False)

	# transform data to a response data
	new_data = transformed_data(olshop_df)
	return new_data
