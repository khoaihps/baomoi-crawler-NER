import os
import csv
import pandas as pd
from common import config

class Writer:
    def __init__(self, filepath=config.DEFAULT_ARTICLE_OUTPUT_FP):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, delimiter="|")
                writer.writerow(["crawled_time", "published_time", "title", "content", "author", "url"])

    def write_article(self, article):
        with open(self.filepath, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="|")
            writer.writerow([
                article.get("crawled_time", ""),
                article.get("published_time", ""),
                article.get("title", ""),
                article.get("content", ""),
                article.get("author", ""),
                article.get("url", ""),
            ])

    def read_as_dataframe(self):
        return pd.read_csv(self.filepath, delimiter="|", encoding="utf-8")
