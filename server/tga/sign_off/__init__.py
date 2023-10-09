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


def init_app(app: SuperdeskEve):
    app.register_blueprint(sign_off_request_bp)
    app.add_template_global(render_text_input)
    app.add_template_global(render_content_text)
    app.add_template_global(render_html_content)
    app.add_template_global(render_tag_list)
    app.add_template_global(render_cv_items)
    app.add_template_global(render_featuremedia_image)
