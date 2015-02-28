# -*- coding: utf-8 -*-
import codecs
from urllib2 import unquote
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.spider import Spider
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy import Selector

import re
from platform import system
from scrapy import log
from scrapy.log import ScrapyFileLogObserver
import json
from bs4 import BeautifulSoup

from selenium import webdriver
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time


class jglobalresearcher_spider(CrawlSpider):
	name = "jglobaldownload_spider"

	def __init__(self,name=None,**kwargs):
		super(jglobalresearcher_spider, self).__init__(name, **kwargs)


		self.moreButtonXpath = "//img[contains(@src,'/common/images/btn_more.png')]"
		self.nextPagexpath = "//a[contains(@id,'JD_P_NEXT')]/img"
		allowed_domains = ["http://jglobal.jst.go.jp"]
		self.start_urls=[
						# "http://jglobal.jst.go.jp/detail.php?JGLOBAL_ID=200901027338990336&q=%E4%BA%AC%E9%83%BD%E5%A4%A7%E5%AD%A6&t=1"
						"http://jglobal.jst.go.jp/detail.php?JGLOBAL_ID=200901079241931254&q=%E4%BA%AC%E9%83%BD%E5%A4%A7%E5%AD%A6&t=1"
						# ,"http://jglobal.jst.go.jp/detail.php?JGLOBAL_ID=200901069127676630&q=%E4%BA%AC%E9%83%BD%E5%A4%A7%E5%AD%A6&t=1"
						# ,"http://jglobal.jst.go.jp/detail.php?JGLOBAL_ID=200901064753496323&q=%E4%BA%AC%E9%83%BD%E5%A4%A7%E5%AD%A6&t=1"
		 				]
		self.DIV_IDS=	{'JD_CS_2':'Affiliation_Department',
						'JD_CS_3': 'Job_Title',
						'JD_CS_4': 'Other_Affiiation',
						'JD_RFD_J': 'Field_Of_Study',
						'JD_RFKW_2': 'Research_Keywords',
						'JD_THM': 'Grants',
						'JD_AR': 'MISC',
						'JD_PA': 'Papers',
						'JD_BKNAM': 'Books',
						'JD_PT': ' Patents',
						'JD_PR': 'Presentations',
						'JD_OA': 'Works',
						'JD_GS': 'Education',
						'JD_AC': 'Degrees',
						'JD_RC': 'Career',
						'JD_BJH': 'Committees',
						'JD_SO': 'Affiliations',
						'JD_EA': 'Cited_Papers',
						'JD_EP': 'Cited_Patents'}

		self.JGLOBAL_DOMAIN = "http://jglobal.jst.go.jp"

					
		self.JGLOBAL_ID = None

	def returnJGlobalID(self,url):
		#return id after GLOBAL_ID
		return url.split('=')[1][0:-2]

	def setGlobalID(self, url):
			self.JGLOBAL_ID = self.returnJGlobalID(url)

	def initDriver(self,browser='Chrome'):
		if system() == 'Darwin':
			driver = webdriver.Chrome("./chromedriver")
			# self.driver = webdriver.Firefox()

		elif system() =='Windows':
			# driver  = webdriver.PhantomJS('phantomjs.exe')
			driver = webdriver.Chrome("chromedriver.exe")
			# self.driver = webdriver.Firefox()
	
		return driver
	

	def nextButtonValid(self, driver2):
		nextButtonXpath = "//img[contains(@src,'/common/images/pager_arrow_next.png')]"
		nextButtonGreyXpath  ="//img[contains(@src,'/common/images/pager_arrow_next_no.png')]"

		try:
			elem = driver2.find_element_by_xpath("//div[contains(@id,'JD_PAGER')]")
			if self.is_element_present(elem,nextButtonXpath):
				return True
			elif self.is_element_present(elem,nextButtonGreyXpath):
				return False
			else:
				return False

		except NoSuchElementException:
			return False

	def scroll_element_into_view(self,driver, element):
   	 
	    y = element.location['y']
	    driver.execute_script('window.scrollTo(0, {0})'.format(y))

	def downloadAllAdditionlPages(self,link,blockName):

		nextButtonXpath = "//img[contains(@src,'/common/images/pager_arrow_next.png')]"
		driver2=self.initDriver()
		driver2.get(link)
		driver2.set_window_size(1920, 1000)

		conditionFlag = True
		count = 0
		while  conditionFlag:
	
			WebDriverWait(driver2 , 60).until(
				EC.invisibility_of_element_located((By.ID, 'JD_MAIN_LD'))
				# lambda x: x.find_element(By.ID,'JD_MAIN_LD')
				)
			time.sleep(1.5)
			mainElem = driver2.find_element(By.ID,'JD_MAIN')
			mainElemHTML = mainElem.get_attribute('innerHTML')
			soup = BeautifulSoup(mainElemHTML)
			fileName = self.JGLOBAL_ID+'_'+blockName+'_'+str(count)
			self.writeSoupToHTML(soup,fileName)
			count += 1
			if self.nextButtonValid(driver2):
				nextButton = driver2.find_element_by_xpath(nextButtonXpath)
				self.scroll_element_into_view(driver2,nextButton)
				nextButton.click()
			else:
				conditionFlag = False


		driver2.close()

	def isMoreButtonPresent(self,soup):
		a = soup.find('img',{'src':'/common/images/btn_more.png'})
		if a is None:
			return False
		else:
			return True

	def returnProperSoup(self,elem,blockName):
		innerHTML = elem.get_attribute('innerHTML')
		soup = BeautifulSoup(innerHTML)
		soupArray = []
		flag = self.isMoreButtonPresent(soup)

		if flag:
			html = elem.get_attribute('innerHTML')
			soup = BeautifulSoup(html)
			link = self.JGLOBAL_DOMAIN + soup.find('p',{'class':'txtAR'}).find('a')['href']
			self.downloadAllAdditionlPages(link,blockName)
			return soupArray
		else:
			soupArray.append(soup)
			return soupArray




	def is_element_present(self,elem,xpath):
		try: 
			newElem = elem.find_element_by_xpath(xpath)
		except NoSuchElementException: 
			return False
		return True





	def writeSoupToHTML(self,soup,fileName):
		with open('./downloadedHTML/'+fileName+'.html','wb') as f:
			f.write(str(soup))


	def parse(self, response):
		driver = self.initDriver()
		driver.get(response.url)
		driver.set_window_size(1920, 1000)

		self.setGlobalID(response.url)
	


		WebDriverWait(driver,60).until(
				lambda x: len(x.find_element(By.ID,'JD_NMRJ').text)>0
			)

		mainElem = driver.find_element(By.ID,'JD_CONTAINER')
		soup = BeautifulSoup(mainElem.get_attribute('innerHTML'))
		self.writeSoupToHTML(soup,self.JGLOBAL_ID)


 		for k,v in self.DIV_IDS.iteritems():
			elem = driver.find_element(By.ID,k)
			innerHTML = elem.get_attribute('innerHTML')
			soup = BeautifulSoup(innerHTML)
			flag = self.isMoreButtonPresent(soup)

			if flag:
				link = self.JGLOBAL_DOMAIN + soup.find('p',{'class':'txtAR'}).find('a')['href']
				self.downloadAllAdditionlPages(link,v)
			else:
				continue


		driver.close()
