from app.core.repository import SQLBaseRepository
from app.models import OwnedOtherBrandCylindersModel


class OwnedOtherBrandCylinderRepository(SQLBaseRepository):

    model = OwnedOtherBrandCylindersModel
