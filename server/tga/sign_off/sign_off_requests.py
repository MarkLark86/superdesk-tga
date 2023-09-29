from typing import Dict, Any, Optional, List
from time import time
import logging

from authlib.jose import JsonWebToken
from authlib.jose.errors import ExpiredTokenError, DecodeError
from flask import Blueprint, request, render_template, current_app as app, url_for, jsonify
from flask_babel import _
from bson import ObjectId
from bson.errors import InvalidId

from superdesk import get_resource_service
from superdesk.errors import SuperdeskApiError
from superdesk.auth.decorator import blueprint_auth
from superdesk.emails import send_email
from superdesk.upload import handle_cors


logger = logging.getLogger(__name__)
sign_off_request_bp = Blueprint("sign_off_requests", __name__)


JWT_ALGORITHM = "HS256"


@sign_off_request_bp.route("/api/sign_off_requests/approve", methods=["GET", "OPTIONS"])
def sign_off_approval():
    def render_html_page(error: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
        return render_template("sign_off_approval.html", error=error, data=data)

    token = request.args.get("token")
    if not token:
        return render_html_page(error="no_token")

    try:
        token_data = JsonWebToken([JWT_ALGORITHM]).decode(token, app.config["SIGN_OFF_REQUESTS_SHARED_SECRET"])
        token_data.validate_exp(now=time(), leeway=0)
    except ExpiredTokenError as err:
        logger.exception(err)
        logger.error("Token expired")
        return render_html_page(error="expired")
    except DecodeError as err:
        logger.exception(err)
        logger.error("Failed to decode token")
        return render_html_page(error="invalid")
    except Exception as err:
        logger.exception(err)
        logger.error("Failed to process token")
        return render_html_page(error=str(err))

    return render_html_page(data=token_data)


@sign_off_request_bp.route("/api/sign_off_request", methods=["POST", "OPTIONS"])
@blueprint_auth()
def send_sign_off_request_emails():
    if request.method == "OPTIONS":
        return handle_cors()

    data = request.json
    item = _get_item(data)

    for user in _get_users(data):
        token = gen_jwt_for_approval_request(item["_id"], user["_id"], "approval_request")
        admins = app.config["ADMINS"]
        base_url = url_for("sign_off_requests.sign_off_approval", _external=True)

        data = dict(
            app_name=app.config["APPLICATION_NAME"],
            approval_url=f"{base_url}?token={token}",
            expires_in=int(app.config["SIGN_OFF_REQUESTS_EXPIRATION"] / 3600),  # hours
            item=item,
        )
        text_body = render_template("email_sign_off_request.txt", **data)
        html_body = render_template("email_sign_off_request.html", **data)
        item_name = item.get("headline") or item.get("slugline")

        send_email.delay(
            subject=f"Author Approval Request for '{item_name}'",
            sender=admins[0],
            recipients=[user["email"]],
            text_body=text_body,
            html_body=html_body,
        )

    return jsonify({"_status": "OK"}), 201


def _get_item(data):
    archive_service = get_resource_service("archive")
    item_id: str = data.get("item_id")
    if not item_id:
        raise SuperdeskApiError.badRequestError(_("item_id field is required"))
    item = archive_service.find_one(req=None, _id=item_id)
    if not item:
        raise SuperdeskApiError.notFoundError(_("Content not found"))

    return item


def _get_users(data) -> List[Dict[str, Any]]:
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


def gen_jwt_for_approval_request(item_id: str, author_id: ObjectId, scope: str):
    header = {"alg": JWT_ALGORITHM}
    payload = {
        "iss": "Superdesk Author Approvals",
        "iat": int(time()),
        "exp": int(time() + app.config["SIGN_OFF_REQUESTS_EXPIRATION"]),
        "scope": scope,
        "author_id": str(author_id),
        "item_id": item_id,
    }

    token = JsonWebToken([JWT_ALGORITHM]).encode(header, payload, app.config["SIGN_OFF_REQUESTS_SHARED_SECRET"])

    return token.decode("UTF-8")
