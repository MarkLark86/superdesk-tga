from typing import Dict, Any, Optional, List
from time import time
import logging

from authlib.jose import JsonWebToken
from authlib.jose.errors import ExpiredTokenError, DecodeError
from flask import Blueprint, request, render_template, current_app as app, url_for, jsonify

from superdesk.errors import SuperdeskApiError
from superdesk.auth.decorator import blueprint_auth
from superdesk.emails import send_email
from superdesk.upload import handle_cors
from superdesk.upload import generate_response_for_file

from .form import UserSignOffForm
from .utils import (
    get_css_filename,
    JWT_ALGORITHM,
    get_item_from_token_data,
    get_users_from_token_data,
    modify_asset_urls,
    update_item_publish_approval,
    gen_jwt_for_approval_request,
)


logger = logging.getLogger(__name__)
sign_off_request_bp = Blueprint("sign_off_requests", __name__)


@sign_off_request_bp.route("/api/sign_off_requests/approve", methods=["GET", "OPTIONS", "POST"])
def sign_off_approval():
    def render_html_page(
        token_error: Optional[str] = None,
        form_errors: Optional[Dict[str, List[str]]] = None,
        data: Optional[Dict[str, Any]] = None,
        form: Optional[UserSignOffForm] = None,
        item: Optional[Dict[str, Any]] = None,
    ):
        return render_template(
            "sign_off_approval.html",
            token_error=token_error,
            form_errors=form_errors,
            data=data,
            form=form,
            item=item,
            css_file_path=get_css_filename(),
        )

    token = request.args.get("token")
    if not token:
        return render_html_page(token_error="no_token")

    try:
        token_data = JsonWebToken([JWT_ALGORITHM]).decode(token, app.config["SIGN_OFF_REQUESTS_SHARED_SECRET"])
        token_data.validate_exp(now=time(), leeway=0)
    except ExpiredTokenError as err:
        logger.exception(err)
        logger.error("Token expired")
        return render_html_page(token_error="expired")
    except DecodeError as err:
        logger.exception(err)
        logger.error("Failed to decode token")
        return render_html_page(token_error="invalid")
    except Exception as err:
        logger.exception(err)
        logger.error("Failed to process token")
        return render_html_page(token_error=str(err))

    form = UserSignOffForm()
    item = get_item_from_token_data(token_data)
    modify_asset_urls(item, token_data["author_id"])

    if request.method == "POST":
        if form.validate_on_submit():
            update_item_publish_approval(item, form)
            return render_template("sign_off_approval_submitted.html", css_file_path=get_css_filename())
        else:
            return render_html_page(data=token_data, form=form, item=item, form_errors=form.errors)

    return render_html_page(data=token_data, form=form, item=item)


@sign_off_request_bp.route("/api/sign_off_requests/upload-raw/<path:media_token>", methods=["GET", "OPTIONS"])
def get_upload_as_data_uri(media_token):
    if request.method == "OPTIONS":
        return handle_cors()

    token_data = JsonWebToken([JWT_ALGORITHM]).decode(media_token, app.config["SIGN_OFF_REQUESTS_SHARED_SECRET"])
    token_data.validate_exp(now=time(), leeway=0)
    media_id = token_data["item_id"]

    if not request.args.get("resource"):
        media_file = app.media.get_by_filename(media_id)
    else:
        media_file = app.media.get(media_id, request.args["resource"])
    if media_file:
        return generate_response_for_file(media_file)

    raise SuperdeskApiError.notFoundError("File not found on media storage.")


@sign_off_request_bp.route("/api/sign_off_request", methods=["POST", "OPTIONS"])
@blueprint_auth()
def send_sign_off_request_emails():
    if request.method == "OPTIONS":
        return handle_cors()

    data = request.json
    item = get_item_from_token_data(data)

    for user in get_users_from_token_data(data):
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
