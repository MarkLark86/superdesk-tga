from datetime import datetime
from unittest.mock import patch
from bson import ObjectId

from superdesk.tests import TestCase
from tga.publish.formatters.crossref import CrossrefFormatter

USER_1_ID = ObjectId()
USER_2_ID = ObjectId()
USER_3_ID = ObjectId()
doi_batch_id = ObjectId()


class CrossrefFormatterTest(TestCase):
    def setUp(self):
        self.formatter = CrossrefFormatter()
        self.app.data.insert(
            "users",
            [
                {
                    "_id": USER_1_ID,
                    "first_name": "Joe",
                    "last_name": "Blogs",
                },
                {
                    "_id": USER_2_ID,
                    "first_name": "Ferry",
                    "last_name": "Blast",
                },
                {
                    "_id": USER_3_ID,
                    "first_name": "Perry",
                    "last_name": "Doc",
                },
            ],
        )

    @patch("tga.publish.formatters.crossref.utcnow", return_value=datetime(2022, 5, 31, 13, 0, 0))
    @patch("tga.publish.formatters.crossref.ObjectId", return_value=doi_batch_id)
    def test_xml_format(self, _object_id, _utcnow):
        article = {
            "_id": "urn:localhost.abc",
            "guid": "urn:localhost.abc",
            "source": "360info",
            "extra": {
                "doi": "10.54377/f5f3-c543",
            },
            "headline": "This is a test headline",
            "versioncreated": datetime(2022, 5, 31, 11, 45, 19, 0),
            "authors": [
                {
                    "name": "Author",
                    "parent": USER_1_ID,
                    "role": "author",
                    "sub_label": "Joe Blogs",
                    "_id": [
                        USER_1_ID,
                        "author",
                    ],
                },
                {
                    "name": "Editor",
                    "parent": USER_2_ID,
                    "role": "editor",
                    "sub_label": "Ferry Blast",
                    "_id": [
                        USER_2_ID,
                        "editor",
                    ],
                },
                {
                    "name": "Editor",
                    "parent": USER_3_ID,
                    "role": "editor",
                    "sub_label": "Perry Doc",
                    "_id": [
                        USER_3_ID,
                        "editor",
                    ],
                },
            ],
        }

        xml = self.formatter._gen_xml(article)

        self.assertEqual(xml.tag, "doi_batch")
        self.assertEqual(xml.attrib["version"], "5.3.1")

        self.assertEqual(xml.find("head/doi_batch_id").text, str(doi_batch_id))
        self.assertEqual(xml.find("head/timestamp").text, "20220531130000")

        metadata = xml.find("body/report-paper/report-paper_metadata")
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.attrib["language"], "en")
        self.assertEqual(metadata.find("titles/title").text, article["headline"])

        self.assertEqual(metadata.find("publication_date").attrib["media_type"], "online")
        self.assertEqual(metadata.find("publication_date/year").text, "2022")
        self.assertEqual(metadata.find("publication_date/month").text, "05")
        self.assertEqual(metadata.find("publication_date/day").text, "31")

        self.assertEqual(metadata.find("doi_data/doi").text, "10.54377/f5f3-c543")
        self.assertEqual(metadata.find("doi_data/resource").text, "https://360info.org/?doi=10.54377/f5f3-c543")

        contributors = {
            n.find("given_name").text + "_" + n.find("surname").text: n
            for n in metadata.find("contributors")
            if n.tag == "person_name"
        }

        self.assertIsNotNone(contributors.get("Joe_Blogs"))
        self.assertEqual(contributors["Joe_Blogs"].attrib["sequence"], "first")
        self.assertEqual(contributors["Joe_Blogs"].attrib["contributor_role"], "author")

        self.assertIsNotNone(contributors.get("Ferry_Blast"))
        self.assertEqual(contributors["Ferry_Blast"].attrib["sequence"], "additional")
        self.assertEqual(contributors["Ferry_Blast"].attrib["contributor_role"], "editor")

        self.assertIsNotNone(contributors.get("Perry_Doc"))
        self.assertEqual(contributors["Perry_Doc"].attrib["sequence"], "additional")
        self.assertEqual(contributors["Perry_Doc"].attrib["contributor_role"], "editor")
