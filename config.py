import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


class Config:
    """Set Flask configuration vars from .env file."""

    APP_NAME = "nova-be-customer"
    FLASK_ENV = os.getenv("FLASK_ENV")

    DB_ENGINE = os.getenv("DB_ENGINE", default="POSTGRES")

    # SQL database
    SQL_DB_USER = os.getenv("DB_USER")
    SQL_DB_HOST = ""
    SQL_DB_NAME = os.getenv("DB_NAME")
    SQL_DB_PASSWORD = os.getenv("DB_PASSWORD")
    SQL_DB_PORT = os.getenv("DB_PORT", default=5432)

    # MONGO database
    MONGODB_DB = os.getenv("DB_NAME")
    MONGODB_PORT = int(os.getenv("DB_PORT", default=27017))
    MONGODB_USERNAME = os.getenv("DB_USER")
    MONGODB_PASSWORD = os.getenv("DB_PASSWORD")
    MONGODB_CONNECT = False

    # REDIS
    REDIS_SERVER = os.getenv("REDIS_SERVER")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

    # KAFKA
    KAFKA_BOOTSTRAP_SERVERS = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS", default="localhost:9092"
    )
    # General
    DEBUG = False
    DEVELOPMENT = False
    SECRET_KEY = os.getenv("SECRET_KEY", default="SECRET")
    FLASK_RUN_PORT = 6000
    TESTING = False
    LOGFILE = "log.log"
    LOG_MAIL_SUBJECT = f"error_log[{APP_NAME}]"

    # KEYCLOAK
    KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", default="").split("|")
    KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")
    KEYCLOAK_URI = os.getenv("KEYCLOAK_URI")
    KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
    KEYCLOAK_ADMIN_USER = os.getenv("KEYCLOAK_ADMIN_USER")
    KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD")
    JWT_ALGORITHMS = ["HS256", "RS256"]
    JWT_ISSUER = f"{os.getenv('KEYCLOAK_URI')}/auth/realms/{os.getenv('KEYCLOAK_REALM')}"

    # MAIL CONFIGURATION
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_SERVER_PORT = int(os.getenv("MAIL_SERVER_PORT", default=587))
    DEFAULT_MAIL_SENDER_ADDRESS = os.getenv("DEFAULT_MAIL_SENDER_ADDRESS")
    DEFAULT_MAIL_SENDER_PASSWORD = os.getenv("DEFAULT_MAIL_SENDER_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    ADMIN_MAIL_ADDRESSES = os.getenv("ADMIN_MAIL_ADDRESSES", default="").split("|")

    # OBJECT STORAGE (CEPH)
    CEPH_SERVER_URL = os.getenv("CEPH_SERVER_URL", default="http://localhost")
    CEPH_ACCESS_KEY = os.getenv("CEPH_ACCESS_KEY", default="")
    CEPH_SECRET_KEY = os.getenv("CEPH_SECRET_KEY", default="")
    CEPH_BUCKET = os.getenv("CEPH_BUCKET", default="nova-bucket")

    @property
    def SQLALCHEMY_DATABASE_URI(self):  # noqa
        return "postgresql+psycopg2://{db_user}:{password}@{host}:{port}/{db_name}".format(  # noqa
            db_user=self.SQL_DB_USER,
            host=self.SQL_DB_HOST,
            password=self.SQL_DB_PASSWORD,
            port=self.SQL_DB_PORT,
            db_name=self.SQL_DB_NAME,
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SQL_DB_HOST = os.getenv("DEV_DB_HOST", default="localhost")
    MONGODB_HOST = os.getenv("DEV_DB_HOST", default="localhost")
    LOG_BACKTRACE = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False
    SQL_DB_HOST = os.getenv("DB_HOST")
    MONGODB_HOST = os.getenv("DB_HOST")
    LOG_BACKTRACE = False
    LOG_LEVEL = "INFO"


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    DEVELOPMENT = True
    LOG_BACKTRACE = True
    LOG_LEVEL = "DEBUG"

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return (
            f"sqlite:///{os.path.join('..', self.SQL_DB_NAME)}"
            f".sqlite3?check_same_thread=False"
        )
