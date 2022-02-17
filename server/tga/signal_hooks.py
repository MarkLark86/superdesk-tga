from uuid import uuid4
import logging

from eve.utils import ParsedRequest, config
from flask import json

from superdesk import get_resource_service, signals

logger = logging.getLogger(__name__)
CROSSREF_DOI_PREFIX = "10.54377"


def generate_doi(_sender, item):
    """Assign a DOI to this item if one does not already exist"""

    item.setdefault("extra", {})
    if not item["extra"].get("doi"):
        item["extra"]["doi"] = _generate_short_unique_id()


def find_or_generate_doi(_sender, item):
    """Finds a DOI for this item from the ``published`` collection

    If no DOI was found, then generate a new one.
    """

    item.setdefault("extra", {})
    if item["extra"].get("doi"):
        return

    item_id = item[config.ID_FIELD]
    for published_item in _get_published_items_for_id(item_id):
        if (published_item.get("extra", {})).get("doi"):
            item["extra"]["doi"] = published_item["extra"]["doi"]
            return

    logger.warning(f"Unable to find any previous DOIs to use for this article '{item_id}'")
    item["extra"]["doi"] = _generate_short_unique_id()


def _generate_short_unique_id():
    """Generate a short, human readable and unique id in compliance with Crossref / DOI standards"""

    runs = 0
    while runs < 100:
        doi_id = str(uuid4())[:8]
        doi = CROSSREF_DOI_PREFIX + '/' + doi_id[:4] + '-' + doi_id[4:]
        if not _doi_exists(doi):
            return doi

        runs += 1
        logger.warning(f"Generation of Crossref DOI failed, doi '{doi}' already exists")

    logger.error("Failed to generate a unique Crossref DOI. Too many attempts")
    return None


def _doi_exists(doi):
    """Check if a DOI has already been used

    This should rarely happen, but just in case it does we have to check.
    """

    # Use MongoDB as searching for ``extra.doi`` in Elastic won't work
    # There will not be a huge amount of content created from this system
    # So there should be no need for an index here
    return get_resource_service('published').get_from_mongo(req=None, lookup={"extra.doi": doi}).count()


def _get_published_items_for_id(item_id):
    """Get all items in the ``published`` collection for ``item_id``"""

    service = get_resource_service("published")
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"item_id": item_id}}
                ]
            }
        },
        "sort": [{"versioncreated": "desc"}],
    }
    req = ParsedRequest()
    req.args = {"source": json.dumps(query), "repo": "published"}

    return service.get(req=req, lookup=None)


def init_app(_app):
    signals.item_publish.connect(generate_doi)
    signals.item_resend.connect(find_or_generate_doi)
