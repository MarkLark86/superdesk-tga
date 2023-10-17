from typing import Dict, List, Optional, Any
from typing_extensions import TypedDict
import pathlib
from copy import deepcopy
import re
from datetime import datetime, timedelta
from time import time

from authlib.jose import JsonWebToken
from bson import ObjectId
from bson.errors import InvalidId
from eve.utils import config
from flask import g, current_app as app
from flask_babel import _

from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError
from superdesk.utc import utcnow
from superdesk.notification import push_notification

from tga.author_profiles import get_author_profiles_by_user_id
from .form import UserSignOffForm


JWT_ALGORITHM = "HS256"


class AuthorSignOffData(TypedDict):
    user_id: ObjectId
    sign_date: datetime
    version_signed: int
    funding_source: str
    affiliation: str
    consent_publish: bool
    consent_disclosure: bool


class AuthorSignOffRequest(TypedDict):
    user_id: ObjectId
    sent: datetime
    expires: datetime


class PublishSignOffData(TypedDict):
    requester_id: ObjectId
    request_sent: datetime
    pending_reviews: List[AuthorSignOffRequest]
    sign_offs: List[AuthorSignOffData]


def _get_publish_sign_off_data(item: Dict[str, Any]) -> Optional[PublishSignOffData]:
    if (item.get("extra") or {}).get("publish_sign_off"):
        if item["extra"]["publish_sign_off"].get("requester_id"):
            # This is the newer format
            # Make sure all User IDs are an instance of ``ObjectId``
            publish_sign_off: PublishSignOffData = item["extra"]["publish_sign_off"]

            if publish_sign_off.get("requester_id"):
                publish_sign_off["requester_id"] = ObjectId(publish_sign_off["requester_id"])

            for review in publish_sign_off["pending_reviews"]:
                review["user_id"] = ObjectId(review["user_id"])

            for sign_off in publish_sign_off["sign_offs"]:
                sign_off["user_id"] = ObjectId(sign_off["user_id"])

            return publish_sign_off
        elif item["extra"]["publish_sign_off"].get("user_id"):
            # This is the legacy format (AuthorSignOffData), change it to PublishSignOffData
            author_sign_off: AuthorSignOffData = item["extra"]["publish_sign_off"]
            author_sign_off["user_id"] = ObjectId(author_sign_off["user_id"])

            return PublishSignOffData(
                requester_id=author_sign_off["user_id"],
                request_sent=author_sign_off["sign_date"],
                pending_reviews=[],
                sign_offs=[author_sign_off],
            )

    return None


def fix_item_publish_sign_off_format(item: Dict[str, Any]):
    publish_sign_off = _get_publish_sign_off_data(item)
    if publish_sign_off is not None:
        item["extra"]["publish_sign_off"] = publish_sign_off


def fix_resource_publish_sign_off_formats(docs):
    for item in docs.get(config.ITEMS, []):
        fix_item_publish_sign_off_format(item)


def fix_archive_lock_sign_off_formats(items):
    for item in items:
        fix_item_publish_sign_off_format(item)


def fix_item_on_archive_update(updates: Dict[str, Any], original: Dict[str, Any]):
    publish_sign_off = _get_publish_sign_off_data(updates) or _get_publish_sign_off_data(original)
    if publish_sign_off is not None:
        updates.setdefault("extra", deepcopy(original.get("extra") or {}))
        updates["extra"]["publish_sign_off"] = publish_sign_off


def get_css_filename():
    try:
        dist_path = pathlib.Path(pathlib.Path(__file__).parent.parent.parent.parent, "client/dist")
        css_filename = [f.name for f in dist_path.glob("app.bundle.*.css")][0]
        return f"/{css_filename}"
    except (IndexError, ValueError):
        return "/app.bundle.css"


def modify_asset_urls(item, author_id: ObjectId):
    pattern = re.compile('\/api\/upload-raw\/(.*?)"')
    new_body_html = item["body_html"]
    url_prefix = "/api/upload-raw/"
    url_prefix_len = len(url_prefix)

    for asset_filename in re.findall(pattern, item["body_html"]):
        asset_token = gen_jwt_for_approval_request(asset_filename, author_id, "upload-raw", token_expiration=3600)
        new_body_html = new_body_html.replace(
            url_prefix + asset_filename, f"/api/sign_off_requests/upload-raw/{asset_token}"
        )

    item["body_html"] = new_body_html

    for key, association in (item.get("associations") or {}).items():
        if association is None:
            continue
        for size_name, rendition in (association.get("renditions") or {}).items():
            rendition_href = rendition["href"]
            asset_filename = rendition_href[rendition_href.index(url_prefix) + url_prefix_len :]
            asset_token = gen_jwt_for_approval_request(asset_filename, author_id, "upload-raw", token_expiration=3600)
            rendition["href"] = rendition_href.replace(
                url_prefix + asset_filename, f"/api/sign_off_requests/upload-raw/{asset_token}"
            )


def remove_sign_off_from_item(item: Dict[str, Any], user_id: ObjectId):
    publish_sign_off = _get_publish_sign_off_data(item)

    if publish_sign_off is None:
        raise SuperdeskApiError.badRequestError(_("No sign offs found on the item"))

    publish_sign_off["sign_offs"] = [
        sign_off for sign_off in publish_sign_off["sign_offs"] if sign_off["user_id"] != user_id
    ]
    _update_publish_sign_off(item, publish_sign_off)


def update_item_publish_approval(item: Dict[str, Any], form: UserSignOffForm):
    user_id = ObjectId(form.user_id.data)
    publish_sign_off = _get_publish_sign_off_data(item) or PublishSignOffData(
        requester_id=user_id, request_sent=utcnow(), pending_reviews=[], sign_offs=[]
    )

    # Remove any previous sign off from this user, and add the new sign off
    publish_sign_off["sign_offs"] = [
        sign_off for sign_off in publish_sign_off["sign_offs"] if sign_off["user_id"] != user_id
    ] + [
        AuthorSignOffData(
            user_id=user_id,
            funding_source=form.funding_source.data,
            affiliation=form.affiliation.data,
            consent_publish=form.consent_publish.data,
            consent_disclosure=form.consent_disclosure.data,
            sign_date=utcnow(),
            version_signed=form.version_signed.data,
        )
    ]

    # Remove user from ``pending_reviews``
    publish_sign_off["pending_reviews"] = [
        review for review in publish_sign_off["pending_reviews"] if review["user_id"] != user_id
    ]

    g.user = get_resource_service("users").find_one(req=None, _id=user_id)
    _update_publish_sign_off(item, publish_sign_off)
    del g.user


def _update_publish_sign_off(original: Dict[str, Any], publish_sign_off: PublishSignOffData):
    extra = deepcopy(original.get("extra") or {})
    extra["publish_sign_off"] = publish_sign_off
    updates = {"extra": extra}
    get_resource_service("archive").system_update(original["_id"], updates, original)
    get_resource_service("archive_history").on_item_updated(updates, original, "author_approval")
    push_notification(
        "author_approval:updated", extension="tga-sign-off", item_id=original["_id"], new_sign_off=publish_sign_off
    )


def update_item_with_request_details(item: Dict[str, Any], current_user_id: ObjectId, user_ids: List[ObjectId]):
    publish_sign_off = _get_publish_sign_off_data(item)
    if publish_sign_off is None:
        publish_sign_off = PublishSignOffData(
            requester_id=current_user_id, request_sent=utcnow(), pending_reviews=[], sign_offs=[]
        )
    else:
        publish_sign_off["requester_id"] = current_user_id
        publish_sign_off["request_sent"] = utcnow()

    publish_sign_off["pending_reviews"] = [
        review for review in publish_sign_off["pending_reviews"] if review["user_id"] not in user_ids
    ] + [
        AuthorSignOffRequest(
            user_id=user_id,
            sent=utcnow(),
            expires=utcnow() + timedelta(seconds=app.config["SIGN_OFF_REQUESTS_EXPIRATION"]),
        )
        for user_id in user_ids
    ]

    _update_publish_sign_off(item, publish_sign_off)


def get_item_from_token_data(data):
    archive_service = get_resource_service("archive")
    item_id: str = data.get("item_id")
    if not item_id:
        raise SuperdeskApiError.badRequestError(_("item_id field is required"))
    item = archive_service.find_one(req=None, _id=item_id)
    if not item:
        raise SuperdeskApiError.notFoundError(_("Content not found"))

    return item


def get_users_from_token_data(data) -> List[Dict[str, Any]]:
    users_service = get_resource_service("users")
    try:
        authors: List[ObjectId] = [ObjectId(authorId) for authorId in data.get("authors") or []]
    except InvalidId:
        raise SuperdeskApiError.badRequestError(_("authors field must be a list of ObjectIds"))
    if not len(authors):
        raise SuperdeskApiError.badRequestError(_("authors field is required"))

    users = []
    profiles = get_author_profiles_by_user_id(authors)
    for user_id in authors:
        user = users_service.find_one(req=None, _id=user_id)
        if not user:
            raise SuperdeskApiError.notFoundError(_("User not found"))

        try:
            user["email"] = profiles[user_id]["extra"]["profile_email"]
        except KeyError:
            pass

        users.append(user)

    return users


def gen_jwt_for_approval_request(item_id: str, author_id: ObjectId, scope: str, token_expiration: Optional[int] = None):
    header = {"alg": JWT_ALGORITHM}
    payload = {
        "iss": "Superdesk Author Approvals",
        "iat": int(time()),
        "exp": int(time() + (token_expiration or app.config["SIGN_OFF_REQUESTS_EXPIRATION"])),
        "scope": scope,
        "author_id": str(author_id),
        "item_id": item_id,
    }

    token = JsonWebToken([JWT_ALGORITHM]).encode(header, payload, app.config["SIGN_OFF_REQUESTS_SHARED_SECRET"])

    return token.decode("UTF-8")
