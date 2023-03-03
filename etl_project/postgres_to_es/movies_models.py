from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class FilmChoice(str, Enum):
    movie = "movie"
    tv_show = "tv_show"


class PersonChoice(str, Enum):
    actor = "actor"
    director = "director"
    writer = "writer"


class UUIDModel(BaseModel):
    id: UUID

class GenresModel(UUIDModel):
    name: str

class MoviePerson(UUIDModel):
    name: str


class PersonsModel(MoviePerson):
    role: Optional[List[PersonChoice]] = None
    film_ids: Optional[List[UUID]] = None


class MoviesModel(UUIDModel):
    title: str
    imdb_rating: Optional[float] = None
    type: FilmChoice
    description: Optional[str] = None
    genres: Optional[List[GenresModel]] = None
    directors: Optional[List[MoviePerson]] = None
    actors: Optional[List[MoviePerson]] = None
    writers: Optional[List[MoviePerson]] = None
    file_path: Optional[str] = None
