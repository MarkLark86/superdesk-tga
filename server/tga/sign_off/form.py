from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, HiddenField
from wtforms.validators import DataRequired


class UserSignOffForm(FlaskForm):
    item_id = HiddenField("Item Id")
    user_id = HiddenField("User Id")
    version_signed = HiddenField("Item Version Signed")

    funding_source = StringField("Funding Source", validators=[DataRequired()])
    affiliation = StringField("Affiliation", validators=[DataRequired()])

    consent_publish = BooleanField("Consent Publish", validators=[DataRequired()])
    consent_disclosure = BooleanField("Consent Disclosure", validators=[DataRequired()])
