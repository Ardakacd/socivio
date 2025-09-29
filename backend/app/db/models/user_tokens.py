from sqlalchemy import DateTime, Text, Enum, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from .base import Base
import enum
from typing import Optional

class PlatformType(enum.Enum):
    youtube = "youtube"
    facebook = "facebook"
    tiktok = "tiktok"

class UserTokenModel(Base):
    __tablename__ = "user_tokens"

    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    platform: Mapped[PlatformType] = mapped_column(Enum(PlatformType), nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return (f"<UserTokenModel(id={self.id}, user_id='{self.user_id}', "
                f"platform='{self.platform.name}', expires_at='{self.expires_at}')>")
