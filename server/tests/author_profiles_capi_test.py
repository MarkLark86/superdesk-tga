from copy import deepcopy
from flask import json

from superdesk import get_resource_service
from superdesk.tests import TestCase

from content_api.app import get_app
from content_api.publish import MONGO_PREFIX

from settings import CONTENTAPI_INSTALLED_APPS
from .fixtures.vocabularies import VOCABULARIES, CONTENT_TYPES, SDGS, TEST_USER
from tga.author_profiles import AUTHOR_PROFILE_ROLE


TEST_SUBSCRIBER = {"_id": "sub1"}


class ContentAPITestCase(TestCase):
    def setUp(self):
        self.content_api = get_resource_service("content_api")
        self.db = self.app.data.mongo.pymongo(prefix=MONGO_PREFIX).db
        self.app.config["SECRET_KEY"] = "secret"
        config = deepcopy(self.app.config)
        config["AMAZON_CONTAINER_NAME"] = None  # force gridfs
        config["URL_PREFIX"] = ""
        config["MEDIA_PREFIX"] = "/assets"
        config["CONTENTAPI_INSTALLED_APPS"] = CONTENTAPI_INSTALLED_APPS
        self.capi = get_app(config)
        self.capi.testing = True
        self.subscriber = {"_id": "sub1"}

        self.app.data.insert("vocabularies", VOCABULARIES)
        self.app.data.insert("content_types", CONTENT_TYPES)
        self.app.data.insert("users", [TEST_USER])

    def _auth_headers(self, sub=None):
        if sub is None:
            sub = self.subscriber
        service = get_resource_service("subscriber_token")
        payload = {"subscriber": sub.get("_id")}
        service.create([payload])
        token = payload["_id"]
        headers = {"Authorization": "Token " + token}
        return headers

    def _publish_user_profile(self, multi_value_sdgs=False):
        item = {
            "guid": "foo",
            "type": "text",
            "authors": [
                {
                    "code": [TEST_USER["_id"], "Author Profile"],
                    "role": AUTHOR_PROFILE_ROLE,
                    "name": TEST_USER["display_name"],
                    "parent": TEST_USER["_id"],
                    "sub_label": TEST_USER["display_name"],
                }
            ],
            "extra": {
                "profile_id": TEST_USER["_id"],
                "profile_first_name": "Fooey",
                "profile_last_name": "Barey",
                "profile_job_title": {
                    "qcode": "DIRECTOR",
                    "name": "Director",
                    "is_active": True,
                },
                "profile_private_text": "This should not be included in the ContentAPI",
            },
        }
        if multi_value_sdgs:
            item["extra"].update(
                {
                    "profile_sdgs": [SDGS[0], SDGS[1]],
                    "profile_sdg_a": None,
                    "profile_sdg_b": None,
                }
            )
        else:
            item["extra"].update(
                {
                    "profile_sdg_a": SDGS[0],
                    "profile_sdg_b": SDGS[1],
                }
            )
        self.content_api.publish(item, [TEST_SUBSCRIBER])

    def _publish_content_item(self):
        item = {
            "guid": "content_bar",
            "type": "text",
            "authors": [
                {
                    "code": [TEST_USER["_id"], "Writer"],
                    "role": "writer",
                    "name": TEST_USER["display_name"],
                    "parent": TEST_USER["_id"],
                    "sub_label": TEST_USER["display_name"],
                }
            ],
            "slugline": "test-content",
            "headling": "Test Content",
            "body_html": "<p>Test Content</p>",
        }
        self.content_api.publish(item, [TEST_SUBSCRIBER])

    def test_author_profiles_endpoint(self):
        headers = self._auth_headers(TEST_SUBSCRIBER)
        self._publish_user_profile()
        self._publish_content_item()

        def assertUser(data):
            self.assertEqual(data["first_name"], "Fooey")
            self.assertEqual(data["last_name"], "Barey")
            self.assertEqual(data["job_title"], "Director")
            self.assertEqual(data["profile_id"], TEST_USER["_id"])
            self.assertEqual(data["uri"], "http://localhost:5400/author_profiles/abcd123")
            self.assertNotIn("private_text", data)

        with self.capi.test_client() as c:
            response = c.get("author_profiles", headers=headers)
            self.assertEqual(200, response.status_code)
            data = json.loads(response.data)
            self.assertEqual(1, data["_meta"]["total"])
            self.assertEqual("foo", data["_items"][0]["original_id"])
            assertUser(data["_items"][0])

            response = c.get("author_profiles/abcd123", headers=headers)
            self.assertEqual(200, response.status_code)
            data = json.loads(response.data)
            self.assertEqual("foo", data["original_id"])
            assertUser(data)

            # User Profiles not available through the Content Items endpoint
            self.assertEqual(200, c.get("items/content_bar", headers=headers).status_code)
            self.assertEqual(404, c.get("items/abcd123", headers=headers).status_code)

            response = c.get("items", headers=headers)
            self.assertEqual(200, response.status_code)
            data = json.loads(response.data)
            self.assertEqual(1, data["_meta"]["total"])
            self.assertEqual("content_bar", data["_items"][0]["original_id"])

            # Make sure the Authors metadata was enhanced using User Profiles
            author = data["_items"][0]["authors"][0]
            self.assertEqual("abcd123", author["code"])
            self.assertEqual("Fooey", author["first_name"])
            self.assertEqual("Barey", author["last_name"])
            self.assertEqual("Director", author["job_title"])
            self.assertEqual("writer", author["role"])
            self.assertEqual("urn:360info:superdesk:user:abcd123", author["uri"])
            self.assertNotIn("private_text", author)
            self.assertEqual(SDGS[0]["name"], author["sdg_a"])
            self.assertEqual(SDGS[1]["name"], author["sdg_b"])

            # Make sure if the CV defines the field as a ``multi selection``
            # then the value returned is an array
            self.app.data.update("vocabularies", "sdg", {"selection_type": "multi selection"}, {})

            # Update the ContentProfile to remove the original SDGs and add 1
            new_cv_field = deepcopy(VOCABULARIES[7])
            new_cv_field["_id"] = "profile_sdgs"
            self.app.data.insert("vocabularies", [new_cv_field])

            profile_updates = deepcopy(CONTENT_TYPES[1])
            profile_updates["editor"]["profile_sdgs"] = profile_updates["editor"].pop("profile_sdg_a")
            profile_updates["editor"].pop("profile_sdg_b")

            profile_updates["schema"]["profile_sdgs"] = profile_updates["schema"].pop("profile_sdg_a")
            profile_updates["schema"].pop("profile_sdg_b")
            self.app.data.update("content_types", "author_profile", profile_updates, {})

            # Test Author Profiles
            response = c.get("author_profiles", headers=headers)
            self.assertEqual(200, response.status_code)
            data = json.loads(response.data)["_items"][0]
            assertUser(data)

            # Update Author Profile to use multi selection SDGs
            self._publish_user_profile(True)
            response = c.get("author_profiles", headers=headers)
            self.assertEqual(200, response.status_code)
            data = json.loads(response.data)["_items"][0]
            assertUser(data)

            # Test SDGs are combined
            self.assertListEqual([SDGS[0]["name"], SDGS[1]["name"]], data["sdgs"])
            self.assertNotIn("sdg_a", data)
            self.assertNotIn("sdg_b", data)

            # Test Content
            response = c.get("items", headers=headers)
            self.assertEqual(200, response.status_code)
            data = json.loads(response.data)
            author = data["_items"][0]["authors"][0]

            # Test SDGs are combined
            self.assertListEqual([SDGS[0]["name"], SDGS[1]["name"]], author["sdgs"])
            self.assertNotIn("sdg_a", author)
            self.assertNotIn("sdg_b", author)
