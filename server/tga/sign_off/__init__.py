from superdesk.factory.app import SuperdeskEve
from .sign_off_requests import sign_off_request_bp


def init_app(app: SuperdeskEve):
    app.register_blueprint(sign_off_request_bp)
