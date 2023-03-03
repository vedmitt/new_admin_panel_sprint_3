import logging
import time
from datetime import datetime

from settings import (
    APP_CONFIG,
    ELASTIC_CONFIG,
    LOGGER_SETTINGS,
    POSTGRES_CONFIG,
    REDIS_CONFIG,
)
from ElasticLoader import ElasticLoader
from PostgresExtractor import PostgresExtractor
from query import get_query_by_index
from State import RedisState

state = RedisState(config=REDIS_CONFIG)
es_loader = ElasticLoader(config=ELASTIC_CONFIG, state=state)
pg_extractor = PostgresExtractor(dsn=POSTGRES_CONFIG)

indexes = APP_CONFIG.elastic_indexes
itersize = APP_CONFIG.batch_size
freq = APP_CONFIG.frequency


def etl_process(index: str, query: str) -> None:
    data_generator = pg_extractor.extract(index, query, itersize)
    es_loader.upload_data(data_generator, itersize, index)


if __name__ == "__main__":
    logging.basicConfig(**LOGGER_SETTINGS)
    logger = logging.getLogger(__name__)
    while True:
        logger.info("Starting etl...")

        for index in indexes:
            load_from = state.get_key(f"loaded_from_{index}", default=str(datetime.min))

            try:
                query = get_query_by_index(index, load_from)
                etl_process(index, query)

            except ValueError as e:
                logger.error("Skipping index %s: %s", index, e)
                continue

        logger.info("Sleep for %s seconds", freq)
        time.sleep(freq)
