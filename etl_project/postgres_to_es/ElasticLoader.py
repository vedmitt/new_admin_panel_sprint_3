import logging
import time
from typing import Iterator, Optional, Tuple

import backoff
from elasticsearch import Elasticsearch, helpers

from settings import BACKOFF_CONFIG, ElasticConfig
from State import State

logger = logging.getLogger(__name__)


class ElasticLoader:
    def __init__(
        self,
        config: ElasticConfig,
        state: State,
        elastic_connection: Optional[Elasticsearch] = None,
    ) -> None:
        self._config = config
        self._es_conn = elastic_connection
        self._state = state

    @property
    def es_connection(self) -> Elasticsearch:
        """Восстанавливает соединение с elastic"""
        if self._es_conn is None or not self._es_conn.ping():
            self._es_conn = self._create_connection()
        return self._es_conn

    @backoff.on_exception(**BACKOFF_CONFIG)
    def _create_connection(self) -> Elasticsearch:
        """Создает новое подключение для ES"""
        return Elasticsearch([f"{self._config.host}:{self._config.port}"])

    @backoff.on_exception(**BACKOFF_CONFIG)
    def _docs_iterator(self, data: Iterator[Tuple[dict, str]], iter_size: int, index: str) -> Iterator[dict]:
        """
        Возвращает итератор документов для ES. Записывает в state updated_at
        """
        i = 0
        last_updated_at = ""
        key = f"loaded_from_{index}"

        for movie, updated_at in data:
            i += 1
            last_updated_at = updated_at
            yield movie

            if i % iter_size == 0:
                self._state.set_key(key, last_updated_at)

        if last_updated_at:
            self._state.set_key(key, last_updated_at)

    @backoff.on_exception(**BACKOFF_CONFIG)
    def upload_data(self, data: Iterator[Tuple[dict, str]], iter_size: int, index: str) -> None:
        """Загружает данные в ES через итератор"""
        t = time.perf_counter()
        docs_generator = self._docs_iterator(data, iter_size, index)
        lines, _ = helpers.bulk(
            client=self.es_connection,
            actions=docs_generator,
            index=index,
            chunk_size=iter_size,
        )
        elapsed = time.perf_counter() - t
        if lines == 0:
            logger.info("Nothing to update for index %s", index)
        else:
            logger.info("%s lines saved in %s for index %s", lines, elapsed, index)
