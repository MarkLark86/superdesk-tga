from flask import json

from superdesk.tests import TestCase
from superdesk.utc import utcnow


class SignOffRequestTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.app.config["SIGN_OFF_REQUESTS_SHARED_SECRET"] = "secret123"

    def test_sign_off_request_email_workflow(self):
        user_ids = self.app.data.insert(
            "users",
            [
                {"username": "foo", "user_type": "administrator", "email": "foo@foobar.org"},
                {"username": "bar", "user_type": "user", "email": "bar@foobar.org"},
            ],
        )
        self.app.data.insert(
            "auth",
            [
                {
                    "user": user_ids[0],
                    "_updated": utcnow(),
                    "token": "foo",
                }
            ],
        )
        item_id = self.app.data.insert(
            "archive",
            [
                {
                    "_id": "tag:example.com,0000:newsml_BRE9A605",
                    "guid": "tag:example.com,0000:newsml_BRE9A605",
                    "slugline": "slugger-info",
                    "headline": "Header Of The Informational Article",
                    "body_html": "<p>The story so far.</p>",
                    "genre": [{"name": "Article", "qcode": "Article"}],
                    "anpa_category": [{"qcode": "i", "name": "International News"}],
                    "subject": [{"qcode": "17004000", "name": "Statistics"}, {"qcode": "04001002", "name": "Weather"}],
                }
            ],
        )[0]

        data = json.dumps(
            {
                "item_id": item_id,
                "authors": [user_ids[0], user_ids[1]],
            }
        )

        # Construct test client, so we have a user logged in
        client = self.app.test_client()
        with client.session_transaction() as sess:
            sess["session_token"] = "foo"

        # Post the request, which in tern sends the emails to authors
        with self.app.mail.record_messages() as outbox:
            response = client.post("/api/sign_off_request", content_type="application/json", data=data)
            assert response.status_code == 201
            assert len(outbox) == 2

        # Pop the session_token, effectively logging us out of Superdesk
        with client.session_transaction() as sess:
            sess.pop("session_token", None)

        # Iterate over the emails that were sent, extract the link, and test the HTML response from that link
        for email_sent in outbox:
            assert "'Header Of The Informational Article'" in email_sent.subject

            approval_url = "https://localhost/api/sign_off_requests/approve?token="
            assert approval_url in email_sent.body
            assert "link expires after 24 hours" in email_sent.body

            # Extract the URL from the email
            url_index = email_sent.body.index(approval_url) + len(approval_url)
            token = email_sent.body[url_index:].split(" ", 1)[0]

            # Get the HTML page from the link in the email
            response = client.get(f"/api/sign_off_requests/approve?token={token}")
            assert response.status_code == 200
            response_text = response.get_data(as_text=True)

            assert "Header Of The Informational Article" in response_text
            current_user_id = 0 if "foo@foobar.org" in email_sent.recipients else 1
            assert str(user_ids[current_user_id]) in response_text

    def test_validate_sign_off_request_approval(self):
        client = self.app.test_client()

        response = client.get("/api/sign_off_requests/approve")
        assert "Token not provided, invalid URL" in response.get_data(as_text=True)

        response = client.get("/api/sign_off_requests/approve?token=some_invalid_token")
        assert "Invalid token" in response.get_data(as_text=True)
