import asyncio
import os
from urllib.parse import quote_plus

import aiohttp
from bs4 import BeautifulSoup
import csv
from loguru import logger


class HabrScraper:
    def __init__(self, base_url: str = 'https://habr.com/ru/search', last_page: int = 3, keyword: str = 'python'):
        self.base_url = base_url
        self.last_page = last_page
        self.keyword = keyword
        self.results = []
        self.logger = logger

    @logger.catch
    async def fetch_html(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    @logger.catch
    async def get_article_info(self, article):
        title_el = article.find('h2').find('a')
        title = title_el.get_text(strip=True)
        link = 'https://habr.com' + title_el['href']
        date = article.find('time')['datetime']
        author = article.find('a', {'class': 'tm-user-info__username'}).get_text(strip=True)
        description = article.find('div', {'class': 'tm-article-body tm-article-snippet__lead'}).get_text(strip=True)

        return {
            'link': link,
            'title': title,
            'date': date,
            'author': author,
            'description': description,
        }

    @logger.catch
    async def scrape_page(self, page):
        query = quote_plus(self.keyword)
        url = f'{self.base_url}?q={query}&target_type=posts&order=relevance&page={page}'

        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')

        articles = soup.find_all('article', {'class': 'tm-articles-list__item'})

        for article in articles:
            article_info = await self.get_article_info(article)
            self.results.append(article_info)

    @logger.catch
    async def scrape(self):
        self.logger.info(f'starting scraping for keyword: {self.keyword}')
        tasks = []
        for page in range(1, self.last_page + 1):
            task = asyncio.create_task(self.scrape_page(page))
            tasks.append(task)

        await asyncio.gather(*tasks)

    @logger.catch
    def save_to_csv(self, filename='results.csv'):
        self.logger.info(f'saving results to {filename}')
        os.makedirs('result', exist_ok=True)

        filepath = os.path.join('result', filename)

        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['link', 'title', 'date', 'author', 'description'])
            writer.writeheader()
            writer.writerows(self.results)

    @logger.catch
    async def run(self):
        self.logger.info("scraper started")
        await self.scrape()
        self.save_to_csv()
        self.logger.info("scraper finished")
