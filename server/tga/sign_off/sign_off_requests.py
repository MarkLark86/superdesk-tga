from typing import Dict, Any, Optional, List
from time import time
import logging

from authlib.jose import JsonWebToken
from authlib.jose.errors import ExpiredTokenError, DecodeError
from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, request, render_template, current_app as app, url_for, jsonify, make_response

from superdesk.errors import SuperdeskApiError
from superdesk.auth.decorator import blueprint_auth
from superdesk.emails import send_email
from superdesk.upload import generate_response_for_file

from apps.auth import get_user_id

from .form import UserSignOffForm
from .utils import (
    get_css_filename,
    JWT_ALGORITHM,
    get_item_from_token_data,
    get_users_from_token_data,
    modify_asset_urls,
    remove_sign_off_from_item,
    update_item_publish_approval,
    update_item_with_request_details,
    gen_jwt_for_approval_request,
    get_author_profiles_by_user_id,
    get_publish_sign_off_data,
)


logger = logging.getLogger(__name__)
sign_off_request_bp = Blueprint("sign_off_requests", __name__)


def make_cors_response(methods, *args):
    response = make_response(*args)
    response.headers.add("Access-Control-Allow-Origin", app.config["CLIENT_URL"])
    response.headers.add("Access-Control-Allow-Headers", ",".join(app.config["X_HEADERS"]))
    response.headers.add("Access-Control-Allow-Methods", methods)
    response.headers.set("Access-Control-Allow-Credentials", "true")
    return response


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
            readonly=False,
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

    item = get_item_from_token_data(token_data)
    modify_asset_urls(item, token_data["author_id"])
    user_id = ObjectId(token_data["author_id"])
    author_profiles = get_author_profiles_by_user_id([user_id])
    profile = (author_profiles.get(user_id) or {}).get("extra") or {}
    form = UserSignOffForm(author_email=profile.get("profile_email"))

    if request.method == "POST":
        if form.validate_on_submit():
            update_item_publish_approval(item, form)
            return render_template("sign_off_approval_submitted.html", css_file_path=get_css_filename())
        else:
            return render_html_page(data=token_data, form=form, item=item, form_errors=form.errors)

    return render_html_page(data=token_data, form=form, item=item)


@sign_off_request_bp.route("/api/sign_off_requests/<item_id>/<user_id_str>/view", methods=["GET", "OPTIONS"])
@blueprint_auth()
def view_sign_off_request(item_id, user_id_str):
    if request.method == "OPTIONS":
        return make_cors_response("GET")

    try:
        user_id = ObjectId(user_id_str)
    except InvalidId:
        raise SuperdeskApiError.badRequestError("Invalid User ID provided")

    item = get_item_from_token_data({"item_id": item_id})
    publish_sign_off = get_publish_sign_off_data(item)

    if not publish_sign_off:
        raise SuperdeskApiError.badRequestError("Item doesnt contain any publish sign off")

    author_sign_off = next(
        (sign_off for sign_off in publish_sign_off["sign_offs"] if sign_off["user_id"] == user_id), None
    )

    if not author_sign_off:
        raise SuperdeskApiError.badRequestError("Item doesnt contain sign off for user")

    form = UserSignOffForm(
        item_id=item_id,
        user_id=user_id_str,
        version_signed=author_sign_off["version_signed"],
        sign_date=author_sign_off["sign_date"],
        article_name=author_sign_off["article_name"],
        funding_source=author_sign_off["funding_source"],
        affiliation=author_sign_off["affiliation"],
        copyright_terms=author_sign_off["copyright_terms"],
        author_name=author_sign_off["author"]["name"],
        author_title=author_sign_off["author"]["title"],
        author_institute=author_sign_off["author"]["institute"],
        author_email=author_sign_off["author"]["email"],
        author_country=author_sign_off["author"]["country"],
        author_orcid_id=author_sign_off["author"]["orcid_id"],
        warrants_no_copyright_infringements=author_sign_off["warrants"]["no_copyright_infringements"],
        warrants_indemnify_360_against_loss=author_sign_off["warrants"]["indemnify_360_against_loss"],
        warrants_ready_for_publishing=author_sign_off["warrants"]["ready_for_publishing"],
        consent_signature=author_sign_off["consent"]["signature"],
        consent_contact=author_sign_off["consent"]["contact"],
        consent_personal_information=author_sign_off["consent"]["personal_information"],
        consent_multimedia_usage=author_sign_off["consent"]["multimedia_usage"],
    )

    return render_template(
        "sign_off_approval_view_form.html",
        css_file_path=get_css_filename(),
        form=form,
        readonly=True,
    )


@sign_off_request_bp.route("/api/sign_off_requests/upload-raw/<path:media_token>", methods=["GET", "OPTIONS"])
def get_upload_as_data_uri(media_token):
    if request.method == "OPTIONS":
        return make_cors_response("GET")

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


@sign_off_request_bp.route("/api/sign_off_request/<item_id>/<user_id_str>", methods=["DELETE", "OPTIONS"])
@blueprint_auth()
def remove_author_sign_off(item_id, user_id_str):
    if request.method == "OPTIONS":
        return make_cors_response("DELETE")

    try:
        user_id = ObjectId(user_id_str)
    except InvalidId:
        raise SuperdeskApiError.badRequestError("Invalid User ID provided")

    item = get_item_from_token_data({"item_id": item_id})
    remove_sign_off_from_item(item, user_id)

    return make_cors_response("DELETE", "", 204)


@sign_off_request_bp.route("/api/sign_off_request", methods=["POST", "OPTIONS"])
@blueprint_auth()
def send_sign_off_request_emails():
    if request.method == "OPTIONS":
        return make_cors_response("POST")

    data = request.json
    item = get_item_from_token_data(data)
    user_ids: List[ObjectId] = []

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
        user_ids.append(ObjectId(user["_id"]))

    update_item_with_request_details(item, get_user_id(True), user_ids)

    return make_cors_response("POST", jsonify({"_status": "OK"}), 201)
