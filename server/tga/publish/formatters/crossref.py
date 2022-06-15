from lxml import etree
import logging
from bson import ObjectId

from superdesk import get_resource_service
from superdesk.publish.formatters import Formatter
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE
from superdesk.text_utils import get_text
from superdesk.utc import utcnow
from superdesk.errors import FormatterError

logger = logging.getLogger(__name__)

DEPOSITOR_INFO = dict(
    name="360info",
    email="charis.palmer@360info.org",
    registrant="Monash University"
)
PUBLIC_DOI_URL_PREFIX = "https://360info.org/?doi="
author_to_contributor_role_map = dict(
    adviser="author",
    author="author",
    contributor="author",
    editor="editor",
)

FormatterError._codes.update({
    25000: "Failed to generate article metadata for Crossref"
})


class CrossrefFormatter(Formatter):
    FORMAT_TYPE = "crossref"
    ENCODING = "UTF-8"
    XML_ROOT = '<?xml version="1.0" encoding="{}"?>'.format(ENCODING)
    message_nsmap = {
        None: "http://www.crossref.org/schema/5.3.1",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "jats": "http://www.ncbi.nlm.nih.gov/JATS1",
        "fr": "http://www.crossref.org/fundref.xsd",
        "mml": "http://www.w3.org/1998/Math/MathML",
    }

    debug_message_extra = {
        "{{{}}}schemaLocation".format(
            message_nsmap["xsi"]
        ): "http://www.crossref.org/schema/5.3.1 https://www.crossref.org/schemas/crossref5.3.1.xsd",
        "version": "5.3.1",
    }

    def __init__(self):
        super().__init__()
        self.can_export = True

    def can_format(self, format_type, article):
        return format_type == self.FORMAT_TYPE and article[ITEM_TYPE] == CONTENT_TYPE.TEXT

    def format(self, article, subscriber, codes=None):
        try:
            self.subscriber = subscriber
            pub_seq_num = get_resource_service("subscribers").generate_sequence_number(subscriber)
            cr_xml = self._gen_xml(article)

            return [
                (
                    pub_seq_num,
                    self.XML_ROOT
                    + etree.tostring(
                        cr_xml,
                        pretty_print=True,
                        encoding="unicode",
                        inclusive_ns_prefixes=["jats"],
                        exclusive=True
                    )
                )
            ]
        except Exception as ex:
            raise FormatterError(25000, ex, subscriber)

    def _gen_xml(self, article):
        cr_xml = etree.Element(
            "doi_batch",
            attrib=CrossrefFormatter.debug_message_extra,
            nsmap=CrossrefFormatter.message_nsmap
        )
        self._format_header(cr_xml, article)

        body_xml = etree.SubElement(cr_xml, "body")

        report_paper = etree.SubElement(body_xml, "report-paper")
        report_paper_metadata = etree.SubElement(
            report_paper,
            "report-paper_metadata",
            attrib={"language": article.get("language", "en")}
        )

        self._format_contributors(report_paper_metadata, article)
        self._format_titles(report_paper_metadata, article)
        self._format_dates(report_paper_metadata, article)
        self._format_doi_data(report_paper_metadata, article)

        return cr_xml

    def _format_header(self, cr_xml, article):
        now = utcnow()
        head = etree.SubElement(cr_xml, "head")
        etree.SubElement(head, "doi_batch_id").text = str(ObjectId())
        etree.SubElement(head, "timestamp").text = now.strftime("%Y%m%d%H%M%S")
        depositor = etree.SubElement(head, "depositor")
        etree.SubElement(depositor, "depositor_name").text = DEPOSITOR_INFO["name"]
        etree.SubElement(depositor, "email_address").text = DEPOSITOR_INFO["email"]
        etree.SubElement(head, "registrant").text = DEPOSITOR_INFO["registrant"]

    def _format_titles(self, xml_node, article):
        titles = etree.SubElement(xml_node, "titles")
        etree.SubElement(titles, "title").text = get_text(article.get("headline"))

    def _format_dates(self, xml_node, article):
        publish_date = (article.get("schedule_settings") or {}).get("utc_embargo") or article["versioncreated"]
        posted_date = etree.SubElement(xml_node, "publication_date", attrib={"media_type": "online"})
        etree.SubElement(posted_date, "month").text = publish_date.strftime("%m")
        etree.SubElement(posted_date, "day").text = publish_date.strftime("%d")
        etree.SubElement(posted_date, "year").text = publish_date.strftime("%Y")

    def _format_doi_data(self, xml_node, article):
        doi_data = etree.SubElement(xml_node, "doi_data")
        doi = (article.get("extra") or {}).get("doi")
        etree.SubElement(doi_data, "doi").text = doi
        etree.SubElement(doi_data, "resource").text = PUBLIC_DOI_URL_PREFIX + doi

    def _format_contributors(self, xml_node, article):
        if not article.get("authors"):
            return

        users_service = get_resource_service("users")
        contributors = etree.SubElement(xml_node, "contributors")
        is_first = True
        for author in article["authors"]:
            try:
                user_id = author["parent"]
            except KeyError:
                # XXX: in some older items, parent may be missing, we try to find user with name in this case
                try:
                    user = next(users_service.find({"display_name": author["name"]}))
                except (StopIteration, KeyError):
                    logger.warning("Unknown user")
                    user = {}
            else:
                try:
                    user = next(users_service.find({"_id": user_id}))
                except StopIteration:
                    logger.warning(f"Unknown user: {user_id}")
                    user = {}

            attributes = {
                "sequence": "first" if is_first else "additional",
                "contributor_role": (
                    author_to_contributor_role_map.get(author.get("role", "author")) or
                    author_to_contributor_role_map["author"]
                )
            }
            is_first = False
            person = etree.SubElement(contributors, "person_name", attrib=attributes)
            etree.SubElement(person, "given_name").text = user["first_name"]
            etree.SubElement(person, "surname").text = user["last_name"]

    def export(self, article):
        if self.can_format(self.FORMAT_TYPE, article):
            sequence, formatted_doc = self.format(article, {"_id": "0"}, None)[0]
            return formatted_doc.replace("''", "'")
        else:
            raise Exception()
