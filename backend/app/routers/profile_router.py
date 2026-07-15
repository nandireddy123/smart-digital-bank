from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user_orm import UserORM
from app.repositories.user_repository import UserRepository
from app.repositories.misc_repository import NotificationRepository, SupportRepository
from app.services.misc_services import NotificationService, SupportService
from app.schemas.misc_schemas import UpdateProfileRequest, SupportTicketRequest

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("/me")
def get_profile(current_user: UserORM = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone": current_user.phone,
        "role": current_user.role,
    }


@router.put("/me")
def update_profile(payload: UpdateProfileRequest,
                    current_user: UserORM = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.update_profile(current_user, payload.full_name, payload.phone)
    return {"message": "Profile updated", "full_name": user.full_name, "phone": user.phone}


@router.get("/notifications")
def my_notifications(current_user: UserORM = Depends(get_current_user), db: Session = Depends(get_db)):
    service = NotificationService(NotificationRepository(db))
    return service.my_notifications(current_user.user_id)


@router.post("/support")
def contact_support(payload: SupportTicketRequest,
                     current_user: UserORM = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    service = SupportService(SupportRepository(db))
    ticket = service.create_ticket(current_user.user_id, payload.subject, payload.message)
    return {"message": "Support ticket submitted", "ticket_id": ticket.ticket_id}
