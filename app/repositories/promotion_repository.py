from app.core.repository import SQLBaseRepository
from app.models.promotion_model import PromotionModel
from app.core import Result
from app import db
from app.core.exceptions import AppException, HTTPException

class PromotionRepository:

    @staticmethod
    def index():
        data = PromotionModel.query.all()
        return Result(data, 200)

    @staticmethod
    def create(obj_in):
        obj_data = dict(obj_in)
        db_obj = PromotionModel(**obj_data)
        db.session.add(db_obj)
        db.session.commit()
        return Result(db_obj, 200)

    @staticmethod
    def update_by_id(obj_id, obj_in):
        try:
            old_data = PromotionModel.query.get(obj_id)
            old_data.tittle = obj_in["tittle"]
            old_data.image = obj_in["image"]
            old_data.description = obj_in["description"]
            db.session.commit()

        except Exception as error:
            return "promotion_id does not exist", 400

        return "Data Updated"

    @staticmethod
    def delete(promotion_id):
        try:
            PromotionModel.query.filter_by(id=promotion_id).delete()
            db.session.commit()

        except Exception as error:
            return "promotion_id does not exist", 400

        return "Deleted"
