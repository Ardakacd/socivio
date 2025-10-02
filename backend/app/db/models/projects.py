from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
import uuid
    
class ProjectModel(Base):
    __tablename__ = "projects"


    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # External account reference (Google user id, Meta id, etc.)
    external_account_id: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self):
        return f"<ProjectModel(id={self.id}, external_account_id={self.external_account_id})>"
