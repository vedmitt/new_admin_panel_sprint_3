from typing import Iterator, Optional, Tuple, Type

import backoff
import psycopg2
from psycopg2.extensions import connection as pg_conn
from psycopg2.extras import DictCursor

from settings import BACKOFF_CONFIG, PostgresDsn, PG_MODELS
from movies_models import UUIDModel


class PostgresExtractor:
    def __init__(self, dsn: PostgresDsn, pg_conn: Optional[pg_conn] = None) -> None:
        self._dsn = dsn
        self._pg_conn = pg_conn

    @property
    def connection(self) -> pg_conn:
        """Создает новое соединение, если оно было утеряно"""
        if self._pg_conn is None or self._pg_conn.closed:
            self._pg_conn = self._create_connection()
        return self._pg_conn

    @backoff.on_exception(**BACKOFF_CONFIG)
    def _create_connection(self) -> pg_conn:
        """Закрывает старое соединение и создает новое"""
        if self._pg_conn is not None:
            self._pg_conn.close()

        return psycopg2.connect(**self._dsn.dict(), cursor_factory=DictCursor)

    @backoff.on_exception(**BACKOFF_CONFIG)
    def _data_iterator(self, model: Type[UUIDModel], query: str, itersize: int) -> Iterator[Tuple[dict, str]]:
        """Возвращает итератор данных готовых для ES"""
        cur = self.connection.cursor()
        cur.itersize = itersize
        cur.execute(query)

        for row in cur:
            instance = model(**row).dict()
            instance["_id"] = instance["id"]
            yield instance, str(row["updated_at"])


    def extract(self, index: str, query: str, itersize: int) -> Iterator[Tuple[dict, str]]:
        model = PG_MODELS.get(index)
        if not model:
            raise ValueError(f"Невозможно извлечь {index}")
        
        return self._data_iterator(model, query, itersize)
