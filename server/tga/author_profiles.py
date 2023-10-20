from typing import List, Dict, Any, Optional

from bson import ObjectId
from flask import current_app as app

from superdesk import get_resource_service


AUTHOR_PROFILE_ROLE = "author_profile"


def update_author_profile_content(_sender: Any, updates: Dict[str, Any], original: Dict[str, Any]):
    """Process the ``AuthorProfile`` content on update"""

    custom_fields = _get_content_profile_custom_fields(original)
    if not _content_profile_contains_custom_profile_id(custom_fields):
        # We use the presence of the custom field ProfileID to determine an AuthorProfile article
        # If ProfileID doesn't exist, no need to continue
        return

    _set_article_fields(updates)
    _add_cv_item_on_update(updates, original, custom_fields)


def _get_content_profile_custom_fields(original: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get the list of ``CustomFields`` from the ``ContentProfile`` for the content provided"""

    if original.get("profile") is None:
        return []

    content_profile = get_resource_service("content_types").find_one(req=None, _id=original["profile"])
    return [
        field
        for field in get_resource_service("vocabularies").get_extra_fields()
        if field["_id"] in content_profile["schema"].keys()
    ]


def _content_profile_contains_custom_profile_id(custom_fields: List[Dict[str, Any]]) -> bool:
    """Determines if the Content Profile contains the custom field ProfileID"""

    return (
        next(
            (
                field
                for field in custom_fields
                if field.get("field_type") == "custom" and field.get("custom_field_type") == "profile-id"
            ),
            None,
        )
        is not None
    )


def _set_article_fields(updates: Dict[str, Any]):
    extra = updates.get("extra") or {}
    updates["slugline"] = extra.get("profile_first_name", "") + " " + extra.get("profile_last_name", "")

    if not updates.get("headline"):
        updates["headline"] = "Author Profile"

    if extra.get("profile_id"):
        user_id = updates["extra"]["profile_id"]
        updates["authors"] = [
            {
                "_id": [user_id, "Author Profile"],
                "role": AUTHOR_PROFILE_ROLE,
                "name": "Author Profile",
                "parent": user_id,
                "sub_label": updates["slugline"],
            }
        ]


def _add_cv_item_on_update(updates: Dict[str, Any], original: Dict[str, Any], custom_fields: List[Dict[str, Any]]):
    """Iterates over ``vocabulary-typeahead-field`` values and adds missing items to the CV"""

    cv_fields = [
        field
        for field in custom_fields
        if (
            (field.get("custom_field_config") or {}).get("vocabulary_name")
            and (field.get("custom_field_config") or {}).get("allow_freetext")
        )
    ]

    original_extra = original.get("extra") or {}
    updates_extra = updates.get("extra") or {}
    cv_service = get_resource_service("vocabularies")

    for field_config in cv_fields:
        field_name = field_config["_id"]
        original_qcode = (original_extra.get(field_name) or {}).get("qcode")
        updated_qcode = (updates_extra.get(field_name) or {}).get("qcode")

        if not updated_qcode or updated_qcode == original_qcode:
            # No need to add CV items if the qcode has not changed or updated doesn't contain one
            continue

        # Determine if the ``updated_qcode`` exists in the CV
        cv_id = field_config["custom_field_config"]["vocabulary_name"]
        cv = cv_service.find_one(req=None, _id=cv_id)
        existing_item = next(
            (item for item in cv.get("items") or [] if item["qcode"].lower() == updated_qcode.lower()), None
        )

        if existing_item:
            # Make sure the qcode/name match exactly what's in the CV (case-sensitive)
            updates_extra[field_name].update(
                {
                    "qcode": existing_item["qcode"],
                    "name": existing_item["name"],
                }
            )
        if not existing_item:
            # Item doesn't exist in the CV, add it now
            cv_updates = {"items": cv.get("items") or []}
            cv_updates["items"].append(
                {
                    "name": updates_extra[field_name]["name"],
                    "qcode": updates_extra[field_name]["qcode"],
                    "is_active": True,
                }
            )
            cv_service.patch(cv_id, cv_updates)


def get_author_profiles_by_user_id(user_ids: List[ObjectId]) -> Dict[ObjectId, Dict[str, Any]]:
    urn_domain = app.config["URN_DOMAIN"]
    query = {
        "query": {
            "bool": {
                "must": [
                    {"terms": {"authors.uri": [f"urn:{urn_domain}:user:{user_id}" for user_id in user_ids]}},
                    {"term": {"authors.role": AUTHOR_PROFILE_ROLE}},
                ],
            },
        },
    }

    try:
        response = get_resource_service("author_profiles").search(query)
    except KeyError:
        response = get_resource_service("items").search(query)

    if response.count():
        return {ObjectId(user["extra"]["profile_id"]): user for user in response}

    return {}
