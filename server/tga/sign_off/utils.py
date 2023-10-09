from typing import Dict, List, Optional, Any
import pathlib
from copy import deepcopy
import re
from time import time

from authlib.jose import JsonWebToken
from bson import ObjectId
from bson.errors import InvalidId
from flask import g, current_app as app
from flask_babel import _

from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError
from superdesk.utc import utcnow
from superdesk.notification import push_notification

from .form import UserSignOffForm


JWT_ALGORITHM = "HS256"


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
        for size_name, rendition in (association.get("renditions") or {}).items():
            rendition_href = rendition["href"]
            asset_filename = rendition_href[rendition_href.index(url_prefix) + url_prefix_len :]
            asset_token = gen_jwt_for_approval_request(asset_filename, author_id, "upload-raw", token_expiration=3600)
            rendition["href"] = rendition_href.replace(
                url_prefix + asset_filename, f"/api/sign_off_requests/upload-raw/{asset_token}"
            )


def update_item_publish_approval(item: Dict[str, Any], form: UserSignOffForm):
    data = deepcopy(item.get("extra") or {})
    data["publish_sign_off"] = {
        "user_id": ObjectId(form.user_id.data),
        "funding_source": form.funding_source.data,
        "affiliation": form.affiliation.data,
        "consent_publish": form.consent_publish.data,
        "consent_disclosure": form.consent_disclosure.data,
        "sign_date": utcnow(),
        "version_signed": form.version_signed.data,
    }

    g.user = get_resource_service("users").find_one(req=None, _id=ObjectId(form.user_id.data))
    updates = {"extra": data}
    get_resource_service("archive").system_update(item["_id"], updates, item)
    get_resource_service("archive_history").on_item_updated(updates, item, "author_approval")
    del g.user

    push_notification(
        "author_approval:updated", extension="tga-sign-off", item_id=item["_id"], new_sign_off=data["publish_sign_off"]
    )


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
    for user_id in authors:
        user = users_service.find_one(req=None, _id=user_id)
        if not user:
            raise SuperdeskApiError.notFoundError(_("User not found"))
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
