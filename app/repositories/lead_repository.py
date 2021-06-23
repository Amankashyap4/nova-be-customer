from app.definitions.repository import SQLBaseRepository
from app.models import Lead


class LeadRepository(SQLBaseRepository):
    model = Lead

    def find_by_otp(self, id, otp):
        result = self.model.query.filter_by(id=id, otp=otp).first()
        return result
