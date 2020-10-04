from typing import Optional
import logging

from bs4 import BeautifulSoup
import requests


class TVScraper:
	_logger = logging.getLogger(__name__)
	_base_url = 'https://www.imdb.com'

	@classmethod
	def scrape_imdb_id(cls, imdb_id: str) -> Optional[dict]:
		"""
		Returns a dict with series title, number of seasons, and list of episode data for each season
		"""
		series_url = cls._create_series_url(imdb_id=imdb_id)
		series_html = cls._get_html(url=series_url)
		series_data = cls._scrape_series(html=series_html)
		if series_data is None:
			return None
		series_title = series_data['title']
		
		seasons_data = []
		for season in range(1, series_data['seasons'] + 1):
			season_url = cls._create_season_url(series_url=series_url, season_number=season)
			season_html = cls._get_html(url=season_url)
			season_data = cls._scrape_season(html=season_html)
			seasons_data.append(season_data)

		return {'title': series_title, 'seasons': seasons_data}
		
	@classmethod
	def _scrape_series(cls, html: str) -> Optional[dict]:
		"""
		Returns a dict with keys title and seasons
		"""
		if not html:
			cls._logger.error('No html provided.')
			return None

		soup = BeautifulSoup(html, 'html.parser')
		
		title_element = soup.find('div', class_='title_wrapper')
		if title_element is None:
			cls._logger.error('No series title element found')
			return None

		try:
			title = title_element.contents[1].string.rstrip()
		except Exception as e:
			cls._logger.error(f'Error parsing title element: {title_element}')
			cls._logger.error(e)
			return None

		if not title:
			cls._logger.error('Series title not found.')
			return None
		
		seasons_and_years_element = soup.find('div', class_='seasons-and-year-nav')
		if seasons_and_years_element is None:
			cls._logger.error('Seasons information not found.')
			return None

		try:
			seasons = int(seasons_and_years_element.find('a').string)
		except Exception as e:
			cls._logger.error(f'Error parsing seasons element: {seasons_and_years_element}')
			cls._logger.error(e)
			return None

		return {'title': title, 'seasons': seasons}

	@classmethod
	def _scrape_season(cls, html: str) -> list:
		"""
		Returns a list of dicts with titles and ratings
		"""
		if not html:
			cls._logger.error('No html provided.')
			return []

		soup = BeautifulSoup(html, 'html.parser')
		info = soup.find('div', class_='list detail eplist')
		if info is None:
			cls._logger.error('Error finding episode elements.')
			return []

		try:
			episodes = int(info.find_all('meta')[-1]['content'])
		except Exception as e:
			cls._logger.error('Unable to determine the number of episodes.')
			cls._logger.error(e)
			return []

		titles = [title.text for title in info.find_all('strong')]
		if not titles:
			cls._logger.error('Unable to find episode titles.')
			return []

		try:
			ratings = [float(rating.contents[3].string) for rating in info.find_all('div', class_='ipl-rating-star small')]
		except Exception as e:
			cls._logger.error('Unable to find episode ratings.')
			cls._logger.error(e)
			return []

		if len(titles) != len(ratings):
			cls._logger.error('Number of titles differs from number of ratings.')
			return []
			
		return [{'title': title, 'rating': rating} for title, rating in zip(titles, ratings)]

	@classmethod
	def _create_series_url(cls, imdb_id: str) -> str:
		return f'{cls._base_url}/title/{imdb_id}'

	@staticmethod
	def _create_season_url(series_url: str, season_number: str) -> str:
		return f'{series_url}/episodes?season={season_number}'

	@classmethod
	def _get_html(cls, url: str) -> Optional[str]:
		cls._logger.debug(f'Making get request to {url}')

		try:
			response = requests.get(url=url)
		except Exception as e:
			cls._logger.error(f'Unexpected error requesting url: {url}')
			cls._logger.error(e)
			return None

		if not response.ok:
			cls._logger.error(f'Status code {response.status_code} for {url}')
			return None

		return response.text
