import logging
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from underthesea import sent_tokenize, text_normalize
from collections import Counter, defaultdict
from common.writer import Writer
import pandas as pd

_logger = logging.getLogger(__name__)


class NEREntityCounter:
    def __init__(self, max_entities: int, output_fp: str) -> None:
        self.max_entities = max_entities
        self.output_fp = output_fp
        model_name = "NlpHUST/ner-vietnamese-electra-base"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForTokenClassification.from_pretrained(model_name)
        self.nlp = pipeline("ner", model=model, tokenizer=tokenizer)
        self.writer = Writer()

    def aggregate_entities(self, ner_results: list) -> list:
        entities = []
        current_entity = ""
        current_type = None

        for token in ner_results:
            word = token["word"]
            entity_type = token["entity"]

            if entity_type.startswith("B-"):
                if current_entity:
                    entities.append(
                        {"text": current_entity.strip(), "type": current_type}
                    )
                current_entity = word
                current_type = entity_type[2:]

            elif entity_type.startswith("I-") and current_type == entity_type[2:]:
                if word.startswith("##"):
                    current_entity += word[2:]
                else:
                    current_entity += " " + word
            else:
                if current_entity:
                    entities.append(
                        {"text": current_entity.strip(), "type": current_type}
                    )
                    current_entity = ""
                    current_type = None

        if current_entity:
            entities.append({"text": current_entity.strip(), "type": current_type})

        return entities

    def count_entities_in_text(self, text: str) -> dict:
        text = text_normalize(text)
        segs = sent_tokenize(text)
        ner_results_batch = self.nlp(segs)

        all_entities = []
        for ner_results in ner_results_batch:
            entities = self.aggregate_entities(ner_results)
            all_entities.extend(entities)

        counter = defaultdict(Counter)
        for entity in all_entities:
            normalized_text = entity["text"].strip()
            entity_type = entity["type"]
            counter[entity_type][normalized_text] += 1

        return counter

    def count_entities_in_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        total_counter = defaultdict(Counter)

        for idx, row in df.iterrows():
            _logger.info("⏳ Entity Counter for article %d / %d", idx, len(df))
            text = row.get("content", "")
            if pd.isna(text) or not text.strip():
                continue
            entity_counter = self.count_entities_in_text(text)
            for entity_type, type_counter in entity_counter.items():
                total_counter[entity_type].update(type_counter)

        rows = []
        for entity_type, type_counter in total_counter.items():
            for entity_text, count in type_counter.items():
                rows.append(
                    {
                        "entity_text": entity_text,
                        "entity_type": entity_type,
                        "count": count,
                    }
                )

        df_entities = pd.DataFrame(rows)
        return df_entities

    def run(self) -> None:
        df = self.writer.read_as_dataframe()
        df_result = self.count_entities_in_dataframe(df)

        df_result_sorted = df_result.sort_values(by="count", ascending=False)

        df_result_sorted.head(self.max_entities).to_csv(
            self.output_fp, sep="|", index=False, encoding="utf-8"
        )
        _logger.info("✅ Entities counts saved to %s", self.output_fp)
