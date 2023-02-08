from app.core.repository import SQLBaseRepository
from app.models.contact_us_model import ContactUsModel


class ContactUsRepository(SQLBaseRepository):

    model = ContactUsModel
