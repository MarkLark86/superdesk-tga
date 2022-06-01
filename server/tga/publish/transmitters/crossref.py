import logging
import requests

from flask import current_app as app

from superdesk.publish.transmitters.http_push import HTTPPushService, errors
from superdesk.publish import register_transmitter

logger = logging.getLogger(__name__)


class CrossrefPushService(HTTPPushService):
    NAME = "Crossref HTTP Post"

    def _transmit(self, queue_item, subscriber):
        item = queue_item["formatted_item"]
        destination = queue_item.get("destination", {})
        config = destination.get("config") or {}
        url = config.get("crossref_url")
        username = config.get("username")
        password = config.get("password")

        response = requests.post(
            url,
            data={
                "operation": "doMDUpload",
                "login_id": username,
                "login_passwd": password
            },
            files={"fname": item},
            timeout=app.config.get("HTTP_PUSH_TIMEOUT", (5, 30))
        )
        try:
            response.raise_for_status()
        except Exception as ex:
            logger.exception(ex)
            message = "Error pushing item %s: %s" % (response.status_code, response.text)
            super()._raise_publish_error(response.status_code, Exception(message), destination)


register_transmitter("crossref_http_post", CrossrefPushService(), errors, "crossref_http_config.html")
