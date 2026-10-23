from dataclasses import dataclass


@dataclass
class Post:
    id: int
    user_id: int
    title: str
    body: str


@dataclass
class Comment:
    post_id: int
    id: int
    name: str
    email: str
    body: str


@dataclass
class Album:
    user_id: int
    id: int
    title: str


@dataclass
class Photo:
    album_id: int
    id: int
    title: str
    url: str
    thumbnail_url: str


@dataclass
class Todo:
    user_id: int
    id: int
    title: str
    completed: bool


@dataclass
class Geo:
    lat: str
    lng: str


@dataclass
class Address:
    street: str
    suite: str
    city: str
    zipcode: str
    geo: Geo


@dataclass
class Company:
    name: str
    catchphrase: str
    bs: str


@dataclass
class User:
    id: int
    name: str
    username: str
    email: str
    address: Address
    phone: str
    website: str
    company: Company
