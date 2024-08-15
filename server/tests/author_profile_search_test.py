from eve.utils import ParsedRequest

from superdesk.metadata.item import CONTENT_STATE, ITEM_STATE
from superdesk.tests import TestCase, json
from apps.search import init_app

from tga.author_profiles import AUTHOR_PROFILE_ROLE
from .fixtures.vocabularies import VOCABULARIES, CONTENT_TYPES, TEST_USER


class AuthorProfileSearchTest(TestCase):
    def setUp(self) -> None:
        init_app(self.app)
        self.app.data.insert("vocabularies", VOCABULARIES)
        self.app.data.insert("content_types", CONTENT_TYPES)
        self.app.data.insert("users", [TEST_USER])

    def test_search_author_profile(self):
        self.app.data.insert(
            "archive",
            [
                {
                    "_id": "ap_1",
                    "task": {"desk": 1},
                    ITEM_STATE: CONTENT_STATE.PROGRESS,
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
                            "name": "Director of Photography",
                            "is_active": True,
                        },
                    },
                },
            ],
        )

        def _perform_search(query_string):
            req = ParsedRequest()
            req.args = {
                "repo": "archive",
                "source": json.dumps(
                    {
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "query_string": {
                                            "query": query_string,
                                            "lenient": True,
                                            "default_operator": "AND",
                                        },
                                    },
                                ],
                            },
                        },
                        "from": 0,
                        "size": 25,
                    }
                ),
            }

            return self.app.data.find("search", req, None)[0]

        self.assertEqual(_perform_search("Fooey").count(), 1)
        self.assertEqual(_perform_search("Barey").count(), 1)
        self.assertEqual(_perform_search("Fooey AND Barey").count(), 1)
        self.assertEqual(_perform_search("Director").count(), 1)
        self.assertEqual(_perform_search("Director AND Photography").count(), 1)
        self.assertEqual(_perform_search("Director AND NOT Development").count(), 1)
        self.assertEqual(_perform_search(TEST_USER["_id"]).count(), 1)

        self.assertEqual(_perform_search("Director AND Development").count(), 0)
        self.assertEqual(_perform_search("NOT Director").count(), 0)
