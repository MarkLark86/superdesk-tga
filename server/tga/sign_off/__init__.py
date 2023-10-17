from superdesk.factory.app import SuperdeskEve

from .sign_off_requests import sign_off_request_bp
from .template_globals import (
    render_text_input,
    render_content_text,
    render_html_content,
    render_tag_list,
    render_cv_items,
    render_featuremedia_image,
)
from .utils import (
    fix_item_publish_sign_off_format,
    fix_resource_publish_sign_off_formats,
    fix_archive_lock_sign_off_formats,
    fix_item_on_archive_update,
)


def init_app(app: SuperdeskEve):
    app.register_blueprint(sign_off_request_bp)
    app.add_template_global(render_text_input)
    app.add_template_global(render_content_text)
    app.add_template_global(render_html_content)
    app.add_template_global(render_tag_list)
    app.add_template_global(render_cv_items)
    app.add_template_global(render_featuremedia_image)

    # Make sure publish sign off format is correct
    # This makes the sign_off extension backwards compatible, so the format coming from
    # the server is the newer format, so the front-end shouldn't need backwards compatability
    app.on_fetched_item_archive += fix_item_publish_sign_off_format
    app.on_fetched_item_published += fix_item_publish_sign_off_format

    app.on_fetched_resource_archive += fix_resource_publish_sign_off_formats
    app.on_fetched_resource_published += fix_resource_publish_sign_off_formats

    app.on_inserted_archive_lock += fix_archive_lock_sign_off_formats

    # Make sure ``extra.publish_sign_off`` use ``ObjectId`` for User IDs
    app.on_update_archive += fix_item_on_archive_update
