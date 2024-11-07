import asyncio

from src.habr_scraper import HabrScraper
from src.logs_config import setup_logging

setup_logging()

if __name__ == '__main__':
    scraper = HabrScraper(keyword='aptos')
    asyncio.run(scraper.run())
