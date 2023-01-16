from typing import List, Dict, Any

from urllib.parse import urljoin, quote
from flask import current_app as app

import superdesk
from superdesk.vocabularies import VocabulariesService, VocabulariesResource

from content_api.items.resource import ItemsResource
from content_api.items.service import ItemsService
from tga.author_profiles import AUTHOR_PROFILE_ROLE


class AuthorProfileResource(ItemsResource):
    datasource = {
        "source": "items",
        "search_backend": "elastic",
        "default_sort": [("versioncreated", -1)]
    }
    item_methods = ["GET"]
    resource_methods = ["GET"]


def _get_content_profile_public_field_ids():
    return [
        field["_id"]
        for field in superdesk.get_resource_service("vocabularies").get_extra_fields()
        if not (field.get("custom_field_config") or {}).get("exclude_from_content_api")
    ]


class AuthoringProfileService(ItemsService):
    def _set_request_filters(self, req, filters: List[Any]):
        filters.append({"term": {"authors.role": AUTHOR_PROFILE_ROLE}})
        super()._set_request_filters(req, filters)

    def _is_internal_api(self):
        return False

    def _get_uri(self, document):
        resource_url = "{api_url}/{endpoint}/".format(
            api_url=app.config["CONTENTAPI_URL"], endpoint=app.config["URLS"]["author_profiles"]
        )
        try:
            user_id = document["authors"][0]["code"]
        except (IndexError, KeyError):
            user_id = (document.get("extra") or {}).get("profile_id")
        return urljoin(resource_url, quote(user_id))

    def find_one(self, req, **lookup):
        if (req is None or not req.args) and len(lookup) == 1 and lookup["_id"]:
            # Attempting to get a single item by ID, return based on authors.uri field
            user_profiles = self.get_author_profiles_by_user_ids([lookup["_id"]])
            return user_profiles[0] if user_profiles.count() else None

        return super().find_one(req=req, **lookup)

    def _process_fetched_object(self, profile: Dict[str, Any]):
        super()._process_fetched_object(profile)
        KEYS_TO_KEEP = ["firstcreated", "versioncreated", "original_id", "firstpublished", "_type", "_links", "uri",
                        "extra", "guid"]
        for key in list(profile.keys()):
            if key not in KEYS_TO_KEEP:
                profile.pop(key)

        profile_value = self.get_profile_value_enhanced(profile["extra"])
        profile.update(profile_value)
        profile.pop("extra")

    def get_profile_value_enhanced(self, item):
        field_names = _get_content_profile_public_field_ids()
        profile = {}
        for key, val in item.items():
            if key not in field_names:
                continue
            elif key == "profile_id":
                profile["profile_id"] = val
            else:
                profile_key = key.replace("profile_", "")
                if isinstance(val, dict):
                    profile[profile_key] = val.get("name") or val.get("qcode")
                    if profile == "country" and val.get("region"):
                        profile["region"] = val["region"]
                else:
                    profile[profile_key] = val

        return profile

    def get_author_profiles_by_user_ids(self, user_ids) -> List[Dict[str, Any]]:
        return self.search({
            "query": {
                "bool": {
                    "must": [
                        {"terms": {"authors.uri": [f"domain:user:{user_id}" for user_id in user_ids]}},
                        {"term": {"authors.role": AUTHOR_PROFILE_ROLE}},
                    ],
                },
            },
        })

    def ehance_embedded_item_authors(self, document):
        if not document.get("authors") or document["authors"][0].get("role") == AUTHOR_PROFILE_ROLE:
            return

        author_profiles = {
            profile["extra"]["profile_id"]: self.get_profile_value_enhanced(profile["extra"])
            for profile in self.get_author_profiles_by_user_ids([author["code"] for author in document["authors"]])
        }
        field_names = _get_content_profile_public_field_ids()
        for author in document.get("authors"):
            author_id = author.get("code")

            author_profile = author_profiles.get(author_id)
            if not author_profile:
                # Profile not found for this Author
                continue

            for field in field_names:
                profile_field = field.replace("profile_", "")
                if author_profile.get(profile_field):
                    author[profile_field] = author_profile[profile_field]

    def on_item_fetched(self, document):
        self.ehance_embedded_item_authors(document)

    def on_items_fetched(self, result):
        for document in result["_items"]:
            self.ehance_embedded_item_authors(document)


def init_app(app):
    endpoint_name = "vocabularies"
    VocabulariesResource.internal_resource = True
    service = VocabulariesService(endpoint_name, backend=superdesk.get_backend())
    VocabulariesResource(endpoint_name, app=app, service=service)

    endpoint_name = "author_profiles"
    service = AuthoringProfileService(endpoint_name, backend=superdesk.get_backend())
    AuthorProfileResource(endpoint_name, app=app, service=service)

    app.on_fetched_item_items += service.on_item_fetched
    app.on_fetched_resource_items += service.on_items_fetched
