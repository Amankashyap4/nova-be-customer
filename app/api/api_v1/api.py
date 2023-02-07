from .endpoints import customer, file_manager,faq,safety,promotion,contact_us

def init_app(app):
    """
    Register app blueprints over here
    eg: # app.register_blueprint(user, url_prefix="/api/users")
    :param app:
    :return:
    """
    app.register_blueprint(customer, url_prefix="/api/v1/customers")
    app.register_blueprint(faq, url_prefix="/api/v1/faqs")
    app.register_blueprint(promotion, url_prefix="/api/v1/promotions")
    app.register_blueprint(safety, url_prefix="/api/v1/safetys")
    app.register_blueprint(contact_us, url_prefix="/api/v1/contactus")
    app.register_blueprint(file_manager, url_prefix="/api/v1/customer/filemanager/files")
