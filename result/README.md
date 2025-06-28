
## Results Directory

This folder contains the output files generated during the crawling and entity analysis process.

---

### 📄 `articles.csv`

**Description:**  
This file contains the list of crawled news articles from [https://baomoi.com/](https://baomoi.com/).

**Fields:**

| Field          | Description                                           |
|----------------|-------------------------------------------------------|
| `crawled_time` | The timestamp when the article was crawled (ISO 8601, GMT+7). |
| `published_time` | The original publish time of the article (ISO 8601, GMT+7). |
| `title`        | The article title.                                   |
| `content`      | Full text content of the article, including the sapo and body text. |
| `author`       | The author's name (if available).                    |
| `url`          | The full URL of the article.                         |

---

### 📄 `entities.csv`

**Description:**  
This file contains the named entity recognition (NER) result, showing the frequency of entities appearing across all crawled articles.

**Fields:**

| Field         | Description                                      |
|---------------|--------------------------------------------------|
| `entity_text` | The text of the recognized entity.               |
| `entity_type` | The entity type as classified by the NER model (e.g., LOCATION, LOCATION, ORGANIZATION). |
| `count`       | Total number of times this entity appeared across the dataset. |

**NER Model Used:**  
[NlpHUST/ner-vietnamese-electra-base](https://huggingface.co/NlpHUST/ner-vietnamese-electra-base)

---

### 📄 `cached_urls.db`

**Description:**  
SQLite database used for caching URLs that have already been crawled, to avoid duplication in future runs.

---
