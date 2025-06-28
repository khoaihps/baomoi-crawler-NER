# Baomoi News Crawler and NER Entity Counter

## Requirements

* Python 3.11+

## Installation

Install required Python packages:

```bash
pip install -r requirements.txt
```

---

## 📌 News Crawler

This module crawls news articles from [https://baomoi.com/](https://baomoi.com/).

### Run the crawler:

```bash
python crawler.py
```

### Available arguments:

| Argument      | Description                                                                     | Default   |
| ------------- |---------------------------------------------------------------------------------|-----------|
| `--min_pages` | Minimum number of pages to crawl                                                | '200'     |
| `--topic`     | Topic slug (e.g., `tin-moi`, `the-gioi`, ... You can find more on its website.) | 'tin-moi' |
| `--age_days`  | Max allowed article age (in days)                                               | '4'       |

Default output file path: `./result/articles.csv`
Can be changed in `common/config.py`
---

## 📌 Entity Counter

This module performs NER (Named Entity Recognition) on the crawled articles and return the most frequent entities.

### Model used:

* [`NlpHUST/ner-vietnamese-electra-base`](https://huggingface.co/NlpHUST/ner-vietnamese-electra-base)

### Run entity counter:

```bash
python entity_counter.py
```

### Available arguments:

| Argument         | Description                                | Default               |
| ---------------- | ------------------------------------------ |-----------------------|
| `--output_fp`    | Output file path                           | `result/entities.csv` |
| `--max_entities` | Number of most frequent entities to return | `50`                  |

Default output file path: `./result/entities.csv`
Can be changed in `common/config.py`
---

## Output

All output files are saved under:

```
./result/
```
