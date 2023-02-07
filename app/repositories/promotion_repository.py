from app.core.repository import SQLBaseRepository
from app.models.promotion_model import PromotionModel


class PromotionRepository(SQLBaseRepository):

    model = PromotionModel
