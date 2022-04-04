from .endpoints import customer, file_manager


def init_app(app):
    """
    Register app blueprints over here
    eg: # app.register_blueprint(user, url_prefix="/api/users")
    :param app:
    :return:
    """
    app.register_blueprint(customer, url_prefix="/api/v1/customers")
    app.register_blueprint(file_manager, url_prefix="/api/v1/filemanager/files")
