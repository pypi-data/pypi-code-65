from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
import re


class OverviewSpider(Spider):
	name = 'pyleapo'
	allowed_domains = ['leapcard.ie']
	start_urls = ['https://www.leapcard.ie/en/Login.aspx']

	def parse(self, response):
		username_form_key = response.xpath('//*[@id="ContentPlaceHolder1_UserName"]/@name').get()
		password_form_key = response.xpath('//*[@id="ContentPlaceHolder1_Password"]/@name').get()
		login_form_key = response.xpath('//*[@id="ContentPlaceHolder1_btnlogin"]/@name').get()
		__EVENTVALIDATION_form_key = response.xpath('//*[@id="__EVENTVALIDATION"]/@name').get()
		__PREVIOUSPAGE_form_key = response.xpath('//*[@id="__PREVIOUSPAGE"]/@name').get()
		__VIEWSTATEENCRYPTED_form_key = response.xpath('//*[@id="__VIEWSTATEENCRYPTED"]/@name').get()
		__SCROLLPOSITIONY_form_key = response.xpath('//*[@id="__SCROLLPOSITIONY"]/@name').get()
		__SCROLLPOSITIONX_form_key = response.xpath('//*[@id="__SCROLLPOSITIONX"]/@name').get()
		__VIEWSTATEGENERATOR_form_key = response.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@name').get()
		__VIEWSTATE_form_key = response.xpath('//*[@id="__VIEWSTATE"]/@name').get()
		__EVENTARGUMENT_form_key = response.xpath('//*[@id="__EVENTARGUMENT"]/@name').get()
		__EVENTTARGET_form_key = response.xpath('//*[@id="__EVENTTARGET"]/@name').get()
		_URLLocalization_Var001_form_key = response.xpath('//*[@id="_URLLocalization_Var001"]/@name').get()
		AjaxScriptManager_HiddenField_form_key = response.xpath('//*[@id="AjaxScriptManager_HiddenField"]/@name').get()

		username_form_value = self.username
		password_form_value = self.password
		login_form_value = response.xpath('//*[@id="ContentPlaceHolder1_btnlogin"]/@value').get()
		__EVENTVALIDATION_form_value = response.xpath('//*[@id="__EVENTVALIDATION"]/@value').get()
		__PREVIOUSPAGE_form_value = response.xpath('//*[@id="__PREVIOUSPAGE"]/@value').get()
		__VIEWSTATEENCRYPTED_form_value = response.xpath('//*[@id="__VIEWSTATEENCRYPTED"]/@value').get()
		__SCROLLPOSITIONY_form_value = response.xpath('//*[@id="__SCROLLPOSITIONY"]/@value').get()
		__SCROLLPOSITIONX_form_value = response.xpath('//*[@id="__SCROLLPOSITIONX"]/@value').get()
		__VIEWSTATEGENERATOR_form_value = response.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@value').get()
		__VIEWSTATE_form_value = response.xpath('//*[@id="__VIEWSTATE"]/@value').get()
		__EVENTARGUMENT_form_value = response.xpath('//*[@id="__EVENTARGUMENT"]/@value').get()
		__EVENTTARGET_form_value = response.xpath('//*[@id="__EVENTTARGET"]/@value').get()
		_URLLocalization_Var001_form_value = response.xpath('//*[@id="_URLLocalization_Var001"]/@value').get()
		AjaxScriptManager_HiddenField_form_value = response.xpath('//*[@id="AjaxScriptManager_HiddenField"]/@value').get()

		yield FormRequest('https://www.leapcard.ie/en/Login.aspx', formdata={
			username_form_key: username_form_value,
			password_form_key: password_form_value,
			login_form_key: login_form_value,
			__EVENTVALIDATION_form_key: __EVENTVALIDATION_form_value,
			__PREVIOUSPAGE_form_key: __PREVIOUSPAGE_form_value,
			__VIEWSTATEENCRYPTED_form_key: __VIEWSTATEENCRYPTED_form_value,
			__SCROLLPOSITIONY_form_key: __SCROLLPOSITIONY_form_value,
			__SCROLLPOSITIONX_form_key: __SCROLLPOSITIONX_form_value,
			__VIEWSTATEGENERATOR_form_key: __VIEWSTATEGENERATOR_form_value,
			__VIEWSTATE_form_key: __VIEWSTATE_form_value,
			__EVENTARGUMENT_form_key: __EVENTARGUMENT_form_value,
			__EVENTTARGET_form_key: __EVENTTARGET_form_value,
			_URLLocalization_Var001_form_key: _URLLocalization_Var001_form_value,
			AjaxScriptManager_HiddenField_form_key: AjaxScriptManager_HiddenField_form_value
		}, callback=self.parse_card_overview)

	def parse_card_overview(self, response):
		card_overview_element = response.xpath('//*[@id="ContentPlaceHolder1_TabContainer2_MyCardsTabPanel_ContentPlaceHolder1_ctrlCardOverViewBODetails_CardDetails"]')
		card = {}

		for element in card_overview_element.css('.row'):
			element_key = element.xpath('.//div[1]/label/text()').get()
			element_value = element.xpath('.//div[2]/text()').get()

			if element_key:
				element_key = re.sub(r"[^\w\s]", '', element_key).lower().strip() # strip to numbers and lowercase letters
				element_key = re.sub(r"\s+", '_', element_key) # replace remaining spaces with underscores

			if element_value:
				element_value = element_value.strip()

			if element_key == 'travel_credit_balance':
				element_value = element.xpath('.//div[2]/div[@class="float-left"]/text()').get()

			if element_key and element_value:
				card[element_key] = element_value

		yield card


def get_card_overview(username: str, password: str):
	data = {}

	def crawler_results(signal, sender, item, response, spider):
		data.update(item)

	dispatcher.connect(crawler_results, signal=signals.item_scraped)

	process = CrawlerProcess(
		settings = {
			'BOT_NAME': 'pyleapo',
			'ROBOTSTXT_OBEY': True,
			'DOWNLOADER_MIDDLEWARES': {
				'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
				'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400
			},
			'LOG_ENABLED': False
		}
	)

	process.crawl(OverviewSpider, username=username, password=password)
	process.start()
	
	return data
