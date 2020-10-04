"""Console script for imdb_tv_scraper."""
import json
import sys

import click

from imdb_tv_scraper import TVScraper

@click.command()
@click.argument('title_id', type=click.STRING)
def main(title_id):
	"""Console script for imdb_tv_scraper.

    TITLE_ID is the IMDB title identifier like ttXXXXXXX"""
	data = TVScraper.scrape_imdb_id(imdb_id=title_id)
	json_data = json.dumps(data)
	click.echo(json_data)
	return 0


if __name__ == "__main__":
	sys.exit(main())  # pragma: no cover
