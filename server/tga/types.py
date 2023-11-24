from typing import List
from typing_extensions import TypedDict
from datetime import datetime

from bson import ObjectId


class SignOffAuthor(TypedDict):
    name: str
    title: str
    institute: str
    email: str
    country: str
    orcid_id: str


class SignOffWarrants(TypedDict):
    no_copyright_infringements: bool
    indemnify_360_against_loss: bool
    ready_for_publishing: bool


class SignOffConsent(TypedDict):
    signature: str
    contact: bool
    personal_information: bool
    multimedia_usage: bool


class AuthorSignOffData(TypedDict):
    user_id: ObjectId
    sign_date: datetime
    version_signed: int

    article_name: str
    funding_source: str
    affiliation: str
    copyright_terms: str

    author: SignOffAuthor
    warrants: SignOffWarrants
    consent: SignOffConsent


class AuthorSignOffRequest(TypedDict):
    user_id: ObjectId
    sent: datetime
    expires: datetime


class PublishSignOffData(TypedDict):
    requester_id: ObjectId
    request_sent: datetime
    pending_reviews: List[AuthorSignOffRequest]
    sign_offs: List[AuthorSignOffData]
