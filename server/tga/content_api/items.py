from typing import List, Any

from flask import json

import superdesk
from content_api.items.resource import ItemsResource
from content_api.items.service import ItemsService as _ItemsService

from tga.author_profiles import AUTHOR_PROFILE_ROLE


class ItemsService(_ItemsService):
    def _set_request_filters(self, req, filters: List[Any]):
        req_filter = {"bool": {"must_not": [{"term": {"authors.role": AUTHOR_PROFILE_ROLE}}]}}

        if filters:
            req_filter["bool"]["must"] = filters

        req.args["filter"] = json.dumps(req_filter)

    def _is_internal_api(self):
        """Override this check, to remove filtering by subscribers used when the item was published"""

        return False


def init_app(app):
    endpoint_name = "items"
    service = ItemsService(endpoint_name, backend=superdesk.get_backend())
    ItemsResource(endpoint_name, app=app, service=service)
