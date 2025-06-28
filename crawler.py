import logging
import argparse
from common import config
from crawler.baomoi_crawler import BaomoiCrawler

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="Crawler arguments")

    parser.add_argument("--min_pages", type=int, default=config.DEFAULT_MIN_PAGES, help="Number of articles to crawl")
    parser.add_argument("--topic", type=str, default=config.DEFAULT_TOPIC, help="Topic to crawl")
    parser.add_argument("--age_days", type=int, default=config.DEFAULT_MAX_ARTICLE_AGE_DAYS, help="Topic to crawl")

    args = parser.parse_args()

    logging.info("Starting crawler with arguments: {}".format(args))

    crawler = BaomoiCrawler(
        min_pages=args.min_pages,
        topic=args.topic,
        max_article_age_days=args.age_days,
    )
    crawler.run()
    crawler.close()