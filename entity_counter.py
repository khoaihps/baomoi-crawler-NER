import logging
import argparse
from common import config
from nlp.ner import NEREntityCounter

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="NER Entity Counter arguments")

    parser.add_argument(
        "--output_fp",
        type=str,
        default=config.DEFAULT_NER_OUTPUT_FP,
        help="Output file path",
    )
    parser.add_argument(
        "--max_entities",
        type=int,
        default=config.DEFAULT_MAX_ENTITIES,
        help="Number of most frequent entities to return",
    )

    args = parser.parse_args()

    logging.info("Starting crawler with arguments: {}".format(args))

    counter = NEREntityCounter(
        max_entities=args.max_entities,
        output_fp=args.output_fp,
    )
    counter.run()
