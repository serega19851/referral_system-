from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base
from settings import EXPIRES_AT


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    referrer_id = Column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    referrer = relationship("User", remote_side=[id], backref="referrals")

    referral_code = relationship("ReferralCode", back_populates="owner")


class ReferralCode(Base):
    __tablename__ = "referral_codes"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    expires_at = Column(
        DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=int(EXPIRES_AT))
    )
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="referral_code")
