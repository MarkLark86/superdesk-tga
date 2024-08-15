from unittest.mock import patch

from superdesk import get_resource_service
from superdesk.tests import TestCase
from tga.author_profiles import update_author_profile_content

from .fixtures.vocabularies import VOCABULARIES, CONTENT_TYPES


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
