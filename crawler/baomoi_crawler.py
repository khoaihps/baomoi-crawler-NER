import logging
import requests
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from dateutil import parser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from common.db import SQLiteHook
from common.writer import Writer

_logger = logging.getLogger("__main__")

class BaomoiCrawler:
    BASE_URL = "https://baomoi.com"
    LOCAL_TIMEZONE = timezone(timedelta(hours=7))

    def __init__(self, min_pages: int, topic: str, max_article_age_days: int):
        self.TOPIC_URL = f"{self.BASE_URL}/{topic}.epi"
        self.min_pages = min_pages
        self.max_article_age_days = max_article_age_days
        self.count = 0

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        self.cache = SQLiteHook()
        self.writer = Writer()

    def close(self):
        self.driver.quit()
        self.cache.close()

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(requests.RequestException)
    )
    def fetch_html(self, url):
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text

    def fetch_html_js_rendering(self, url):
        self.driver.get(url)
        time.sleep(2)

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_pause_time = 1

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)

            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break

            last_height = new_height

        return self.driver.page_source

    def extract_urls(self, html):
        soup = BeautifulSoup(html, "html.parser")
        urls = set()

        for a_tag in soup.select("div.relative h3 > a[href]"):
            href = a_tag.get("href")
            if href:
                url = urljoin(self.BASE_URL, href)
                urls.add(url)

        return list(urls)

    def extract_next_page_url(self, html):
        soup = BeautifulSoup(html, "html.parser")
        load_more_div = soup.find("div", class_="load-more")

        if load_more_div:
            for a_tag in load_more_div.find_all("a", href=True):
                if a_tag.find(string=lambda text: text and "Xem thêm" in text):
                    return urljoin(self.BASE_URL, a_tag["href"])

        return None

    def parse_article_from_url(self, url) -> dict | None:
        html = self.fetch_html(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        title_tag = soup.find("h1")
        title = title_tag.text.strip() if title_tag else None

        crawled_time = datetime.now(self.LOCAL_TIMEZONE).isoformat()
        time_tag = soup.find("time", datetime=True)
        published_time = None
        if time_tag:
            try:
                dt = parser.isoparse(time_tag["datetime"])
                published_time = dt.astimezone(self.LOCAL_TIMEZONE).isoformat()
            except Exception:
                published_time = None

        content_div = soup.find("div", class_="content-body")
        author_paragraphs = []
        content_paragraphs = []

        sapo_tag = soup.find("h3", class_="sapo")
        if sapo_tag:
            content_paragraphs.append(sapo_tag.text.strip())

        if content_div:
            for p in content_div.find_all("p"):
                if "body-author" in p.get("class", []):
                    author_paragraphs.append(p.text.strip())
                else:
                    content_paragraphs.append(p.text.strip())

        author = " ".join(author_paragraphs) if author_paragraphs else None
        content = " ".join(content_paragraphs) if content_paragraphs else None

        return {
            "title": title,
            "published_time": published_time,
            "crawled_time": crawled_time,
            "content": content,
            "author": author,
            "url": url,
        }

    def process_article_url(self, url) -> None:
        try:
            if self.cache.has_visited(url):
                return

            _logger.info(f"📰 Crawling article: {url}")
            article = self.parse_article_from_url(url)
            if not article:
                return

            if not article.get("published_time"):
                return

            published_time = datetime.fromisoformat(article["published_time"])
            crawled_time = datetime.fromisoformat(article["crawled_time"])
            article_age_days = (crawled_time - published_time).days
            if article_age_days > self.max_article_age_days:
                _logger.info("Skipping %s: Expired article publish date", url)
                return

            if not article.get("content"):
                _logger.info("Skipping %s: No content", url)
                return

            self.cache.mark_visited(url)
            self.writer.write_article(article)
            self.count += 1
        except Exception as e:
            _logger.error("❗ Error scraping %s: %s", url, e)

    def run(self):
        start_url = self.TOPIC_URL

        while self.count < self.min_pages and start_url:
            _logger.info(f"🔎 Rendering page: %s", start_url)
            html = self.fetch_html_js_rendering(start_url)
            article_urls = self.extract_urls(html)
            start_url = self.extract_next_page_url(html)

            for article_url in article_urls:
                self.process_article_url(article_url)

            _logger.info("⏳ Count %d articles processed", self.count)

        _logger.info(f"✅ Finished. Total articles crawled: %d", self.count)


if __name__ == "__main__":
    crawler = BaomoiCrawler()
    crawler.run()

    crawler.close()
