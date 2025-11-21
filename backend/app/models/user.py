"""
User and UserSettings SQLAlchemy models
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import json


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(50))
    role = Column(String(100))
    is_active = Column(Integer, default=1)
    
    # Profile fields
    qualification = Column(String(255))
    occupation = Column(String(255))
    professional_summary = Column(Text)
    skills = Column(Text)  # JSON stored as text
    experience = Column(Text)  # JSON stored as text
    publications = Column(Text)  # JSON stored as text
    awards = Column(Text)  # JSON stored as text
    social_links = Column(Text)  # JSON stored as text
    avatar_url = Column(Text)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    tokens = relationship("AuthToken", back_populates="user", cascade="all, delete-orphan")
    
    def get_skills(self):
        """Parse skills JSON"""
        if self.skills:
            try:
                return json.loads(self.skills)
            except:
                return []
        return []
    
    def set_skills(self, skills_list):
        """Set skills as JSON"""
        self.skills = json.dumps(skills_list) if skills_list else None


class UserSettings(Base):
    """User settings model"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    email_notifications = Column(Integer, default=1)
    analysis_complete_alerts = Column(Integer, default=1)
    research_updates = Column(Integer, default=0)
    theme = Column(String(50), default="light")
    language = Column(String(10), default="en")
    data_sharing = Column(Integer, default=0)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="settings")

