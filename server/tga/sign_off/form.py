from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, HiddenField
from wtforms.validators import DataRequired


class UserSignOffForm(FlaskForm):
    item_id = HiddenField("Item Id")
    user_id = HiddenField("User Id")
    version_signed = HiddenField("Item Version Signed")
    sign_date = HiddenField("Signed Date")

    article_name = StringField("Article Name", validators=[DataRequired()])
    funding_source = StringField("Funding Source", validators=[DataRequired()])
    affiliation = StringField("Affiliation", validators=[DataRequired()])
    copyright_terms = StringField("Copyright Terms", validators=[DataRequired()])

    author_name = StringField("Name", validators=[DataRequired()])
    author_title = StringField("Position held / title", validators=[DataRequired()])
    author_institute = StringField("University / Institute", validators=[DataRequired()])
    author_email = StringField("Email", validators=[DataRequired()])  # This should be disabled
    author_country = StringField("Country", validators=[DataRequired()])
    author_orcid_id = StringField("ORCID ID (if known)", validators=[])

    warrants_no_copyright_infringements = BooleanField("No Copyright Infringements", validators=[DataRequired()])
    warrants_indemnify_360_against_loss = BooleanField("Indemnify 360info Against Loss", validators=[DataRequired()])
    warrants_ready_for_publishing = BooleanField("Ready For Publishing", validators=[DataRequired()])

    consent_signature = StringField("Agree To Terms", validators=[DataRequired()])
    consent_contact = BooleanField("Consent Contact", validators=[DataRequired()])
    consent_personal_information = BooleanField("Consent Personal Information", validators=[DataRequired()])
    consent_multimedia_usage = BooleanField("Consent Multimedia Usage", validators=[DataRequired()])
