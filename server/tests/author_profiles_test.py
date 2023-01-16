from unittest.mock import patch

from superdesk import get_resource_service
from superdesk.tests import TestCase
from tga.author_profiles import update_author_profile_content


VOCABULARIES = [
    {
        "_id": "profile_id",
        "field_type": "custom",
        "items": [],
        "type": "manageable",
        "schema": {},
        "service": {"all": 1},
        "custom_field_type": "profile-id",
        "display_name": "Author",
        "unique_field": "qcode",
    },
    {
        "_id": "profile_job_title",
        "field_type": "custom",
        "items": [],
        "type": "manageable",
        "schema": {},
        "service": {"all": 1},
        "custom_field_type": "vocabulary-typeahead-field",
        "custom_field_config": {
            "vocabulary_name": "job_titles",
            "allow_freetext": True,
        },
        "display_name": "Job Title",
        "unique_field": "qcode",
    },
    {
        "_id": "job_titles",
        "display_name": "Job Titles",
        "type": "manageable",
        "selection_type": "single selection",
        "unique_field": "qcode",
        "schema": {"qcode": {}, "name": {}},
        "items": [
            {"qcode": "ceo", "name": "CEO", "is_active": True},
            {"qcode": "director", "name": "Director", "is_active": True},
            {"qcode": "media_advisor", "name": "Media Advisor", "is_active": True},
        ],
    },
    {
        "_id": "profile_first_name",
        "field_type": "custom",
        "items": [],
        "type": "manageable",
        "schema": {},
        "service": {"all": 1},
        "custom_field_type": "profile-text",
        "display_name": "First Name",
    },
    {
        "_id": "profile_last_name",
        "field_type": "custom",
        "items": [],
        "type": "manageable",
        "schema": {},
        "service": {"all": 1},
        "custom_field_type": "profile-text",
        "display_name": "Last Name",
    },
]

CONTENT_TYPES = [
    {
        "_id": "article",
        "label": "Article",
        "enabled": True,
        "editor": {
            "slugline": {
                "order": 1,
                "sdWidth": "full",
                "enabled": True,
                "required": True,
            },
        },
        "schema": {
            "slugline": {
                "type": "string",
                "required": True,
                "maxlength": 24,
                "nullable": False,
            },
        },
    },
    {
        "_id": "author_profile",
        "label": "Author Profile",
        "enabled": True,
        "editor": {
            "profile_id": {
                "enabled": True,
                "field_name": "Author",
                "order": 1,
                "section": "header",
                "required": True,
            },
            "profile_job_title": {
                "enabled": True,
                "field_name": "Job Title",
                "order": 3,
                "section": "content",
                "required": False,
            },
            "profile_first_name": {
                "enabled": True,
                "field_name": "First Name",
                "order": 4,
                "section": "content",
                "required": True,
            },
            "profile_last_name": {
                "enabled": True,
                "field_name": "Last Name",
                "order": 4,
                "section": "content",
                "required": True,
            },
        },
        "schema": {
            "profile_id": {
                "type": "custom",
                "required": True,
                "enabled": True,
                "nullable": False,
            },
            "profile_job_title": {
                "type": "custom",
                "required": False,
                "enabled": True,
                "nullable": True,
            },
            "profile_first_name": {
                "type": "custom",
                "required": False,
                "enabled": True,
                "nullable": True,
            },
            "profile_last_name": {
                "type": "custom",
                "required": False,
                "enabled": True,
                "nullable": True,
            },
        },
    },
]


class AuthorProfilesTest(TestCase):
    def setUp(self) -> None:
        self.app.data.insert("vocabularies", VOCABULARIES)
        self.app.data.insert("content_types", CONTENT_TYPES)

    @patch("tga.author_profiles._set_article_fields")
    @patch("tga.author_profiles._add_cv_item_on_update")
    def test_only_process_author_profile_articles(self, set_fields_mock, add_cv_mock):
        update_author_profile_content(None, {}, {"profile": "article"})
        set_fields_mock.assert_not_called()
        add_cv_mock.assert_not_called()

        update_author_profile_content(None, {}, {"profile": "author_profile"})
        set_fields_mock.assert_called_once()
        add_cv_mock.assert_called_once()

    @patch("tga.author_profiles._add_cv_item_on_update")
    def test_set_article_fields(self, _add_cv_mock):
        updates = {
            "extra": {
                "profile_first_name": "Foo",
                "profile_last_name": "Bar",
            }
        }
        update_author_profile_content(None, updates, {"profile": "author_profile"})
        self.assertEqual(updates["slugline"], "Foo Bar")
        self.assertEqual(updates["headline"], "Author Profile")

    def test_add_cv_items(self):
        cv_service = get_resource_service("vocabularies")

        def get_job_titles():
            cv = cv_service.find_one(req=None, _id="job_titles")
            return cv.get("items") or []

        # 1. Test CV from setUp
        job_titles = get_job_titles()
        self.assertEqual(len(job_titles), 3)
        developer = next((item for item in job_titles if item["qcode"] == "developer"), None)
        self.assertIsNone(developer)

        # 2. Test CV is not updated when existing CV item is used
        updates = {
            "extra": {
                "profile_first_name": "Foo",
                "profile_last_name": "Bar",
                "profile_job_title": {
                    "qcode": "DIRECTOR",
                    "name": "Director",
                    "is_active": True,
                },
            }
        }
        update_author_profile_content(None, updates, {"profile": "author_profile"})
        job_titles = get_job_titles()
        self.assertEqual(len(job_titles), 3)
        developer = next((item for item in job_titles if item["qcode"] == "developer"), None)
        self.assertIsNone(developer)
        self.assertEqual(updates["extra"]["profile_job_title"]["qcode"], "director")

        # 3. Test CV is updated when a non-existing CV item is used
        updates["extra"]["profile_job_title"] = {
            "qcode": "developer",
            "name": "Developer",
            "is_active": True,
        }
        update_author_profile_content(None, updates, {"profile": "author_profile"})
        job_titles = get_job_titles()
        self.assertEqual(len(job_titles), 4)
        developer = next((item for item in job_titles if item["qcode"] == "developer"), None)
        self.assertEqual(
            developer,
            {
                "qcode": "developer",
                "name": "Developer",
                "is_active": True,
            },
        )
