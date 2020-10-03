from scrapy.spiders import Spider
from scrapy.http import Request, FormRequest
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
import re


class HistorySpider(Spider):
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
		travel_credit_history_url = response.xpath('//a[@id="ContentPlaceHolder1_TabContainer2_MyCardsTabPanel_Link_ViewJourneyHistory"]/@href').get()
		yield Request(response.urljoin(travel_credit_history_url), callback=self.parse_travel_credit_history)

	def parse_travel_credit_history(self, response):
		travel_credit_history_events = []

		travel_credit_history_table = response.xpath('//table[@id="gvCardJourney"]/tr')

		columns = travel_credit_history_table.xpath('.//th/text()').getall()
		columns = [re.sub(r"\s+", '_', column).lower().strip() for column in columns]

		for row in travel_credit_history_table:
			event = {}
			
			for index, column in enumerate(row.xpath('.//td/text()').getall()):
				if column:
					event[columns[index]] = column

			if event:
				travel_credit_history_events.append(event)
				yield event

		travel_credit_history_table_pagination = response.xpath('//tr[@class="grid-pager"]')
		current_page_number = int(travel_credit_history_table_pagination.xpath('.//span/text()').get())
		next_page_number = current_page_number + 1
		page_links = travel_credit_history_table_pagination.xpath('.//td/a')

		for link in page_links:
			if next_page_number == int(link.xpath('./text()').get()):
				AjaxScriptManager_HiddenField_key = response.xpath('//*[@id="AjaxScriptManager_HiddenField"]/@name').get()
				_URLLocalization_Var001_key = response.xpath('//*[@id="_URLLocalization_Var001"]/@name').get()
				__EVENTTARGET_key = response.xpath('//*[@id="__EVENTTARGET"]/@name').get()
				__EVENTARGUMENT_key = response.xpath('//*[@id="__EVENTARGUMENT"]/@name').get()
				ContentPlaceHolder1_TabContainer2_ClientState_key = response.xpath('//*[@id="ContentPlaceHolder1_TabContainer2_ClientState"]/@name').get()
				__LASTFOCUS_key = response.xpath('//*[@id="__LASTFOCUS"]/@name').get()
				ContentPlaceHolder1_TabContainer2_MyCardsTabPanel_ContentPlaceHolder1_CardJourneyTabContainer_ClientState_key = response.xpath('//*[@id="ContentPlaceHolder1_TabContainer2_MyCardsTabPanel_ContentPlaceHolder1_CardJourneyTabContainer_ClientState"]/@name').get()
				__VIEWSTATE_key = response.xpath('//*[@id="__VIEWSTATE"]/@name').get()
				__VIEWSTATEGENERATOR_key = response.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@name').get()
				__SCROLLPOSITIONX_key = response.xpath('//*[@id="__SCROLLPOSITIONX"]/@name').get()
				__SCROLLPOSITIONY_key = response.xpath('//*[@id="__SCROLLPOSITIONY"]/@name').get()
				__VIEWSTATEENCRYPTED_key = response.xpath('//*[@id="__VIEWSTATEENCRYPTED"]/@name').get()
				__PREVIOUSPAGE_key = response.xpath('//*[@id="__PREVIOUSPAGE"]/@name').get()
				ctl00_ctl00_ContentPlaceHolder1_TabContainer2_MyCardsTabPanel_ddlMyCardsList_key = response.xpath('//*[@id="ContentPlaceHolder1_TabContainer2_MyCardsTabPanel_ddlMyCardsList"]/@name').get()

				AjaxScriptManager_HiddenField_value = response.xpath('//*[@id="AjaxScriptManager_HiddenField"]/@value').get()
				_URLLocalization_Var001_value = response.xpath('//*[@id="_URLLocalization_Var001"]/@value').get()
				ContentPlaceHolder1_TabContainer2_ClientState_value = response.xpath('//*[@id="ContentPlaceHolder1_TabContainer2_ClientState"]/@value').get()
				__LASTFOCUS_value = response.xpath('//*[@id="__LASTFOCUS"]/@value').get()
				ContentPlaceHolder1_TabContainer2_MyCardsTabPanel_ContentPlaceHolder1_CardJourneyTabContainer_ClientState_value = response.xpath('//*[@id="ContentPlaceHolder1_TabContainer2_MyCardsTabPanel_ContentPlaceHolder1_CardJourneyTabContainer_ClientState"]/@value').get()
				__VIEWSTATE_value = response.xpath('//*[@id="__VIEWSTATE"]/@value').get()
				__VIEWSTATEGENERATOR_value = response.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@value').get()
				__SCROLLPOSITIONX_value = response.xpath('//*[@id="__SCROLLPOSITIONX"]/@value').get()
				__SCROLLPOSITIONY_value = response.xpath('//*[@id="__SCROLLPOSITIONY"]/@value').get()
				__VIEWSTATEENCRYPTED_value = response.xpath('//*[@id="__VIEWSTATEENCRYPTED"]/@value').get()
				__PREVIOUSPAGE_value = response.xpath('//*[@id="__PREVIOUSPAGE"]/@value').get()
				ctl00_ctl00_ContentPlaceHolder1_TabContainer2_MyCardsTabPanel_ddlMyCardsList_value = response.xpath('//*[@id="ContentPlaceHolder1_TabContainer2_MyCardsTabPanel_ddlMyCardsList"]/option/@value').get()

				yield FormRequest(response.url, formdata={
					AjaxScriptManager_HiddenField_key: AjaxScriptManager_HiddenField_value,
					_URLLocalization_Var001_key: _URLLocalization_Var001_value,
					__EVENTTARGET_key: link.xpath('./@href').get().split("'")[1],
					__EVENTARGUMENT_key: link.xpath('./@href').get().split("'")[3],
					ContentPlaceHolder1_TabContainer2_ClientState_key: ContentPlaceHolder1_TabContainer2_ClientState_value,
					__LASTFOCUS_key: __LASTFOCUS_value,
					ContentPlaceHolder1_TabContainer2_MyCardsTabPanel_ContentPlaceHolder1_CardJourneyTabContainer_ClientState_key: ContentPlaceHolder1_TabContainer2_MyCardsTabPanel_ContentPlaceHolder1_CardJourneyTabContainer_ClientState_value,
					__VIEWSTATE_key: __VIEWSTATE_value,
					__VIEWSTATEGENERATOR_key: __VIEWSTATEGENERATOR_value,
					__SCROLLPOSITIONX_key: __SCROLLPOSITIONX_value,
					__SCROLLPOSITIONY_key: __SCROLLPOSITIONY_value,
					__VIEWSTATEENCRYPTED_key: __VIEWSTATEENCRYPTED_value,
					__PREVIOUSPAGE_key: __PREVIOUSPAGE_value,
					ctl00_ctl00_ContentPlaceHolder1_TabContainer2_MyCardsTabPanel_ddlMyCardsList_key: ctl00_ctl00_ContentPlaceHolder1_TabContainer2_MyCardsTabPanel_ddlMyCardsList_value
				}, callback=self.parse_travel_credit_history)


def get_card_history(username: str, password: str):
	data = []

	def crawler_results(signal, sender, item, response, spider):
		data.append(item)

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

	process.crawl(HistorySpider, username=username, password=password)
	process.start()
	
	return data
