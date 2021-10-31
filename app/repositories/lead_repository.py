from core.repository import SQLBaseRepository
from app.models import Lead


class LeadRepository(SQLBaseRepository):
    model = Lead
