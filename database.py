import os
import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import declarative_base, relationship

# Đọc biến môi trường từ file .env
load_dotenv(override=True)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("Thiếu DATABASE_URL trong file .env")

# Khởi tạo Engine kết nối Database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)

    progresses = relationship("UserProgress", back_populates="user")


class VocabularySet(Base):
    __tablename__ = "vocabulary_sets"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(255))

    vocabularies = relationship("Vocabulary", back_populates="vocab_set")


class Vocabulary(Base):
    __tablename__ = "vocabularies"

    id = Column(Integer, primary_key=True)
    set_id = Column(Integer, ForeignKey("vocabulary_sets.id"))

    word = Column(String(50), nullable=False)
    phonetic = Column(String(50))
    part_of_speech = Column(String(20))
    meaning = Column(String(255), nullable=False)
    example = Column(String(255))
    example_translation = Column(String(255))

    vocab_set = relationship("VocabularySet", back_populates="vocabularies")
    progresses = relationship("UserProgress", back_populates="vocabulary")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vocab_id = Column(Integer, ForeignKey("vocabularies.id"))

    is_learned = Column(Boolean, default=False)
    last_reviewed = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="progresses")
    vocabulary = relationship("Vocabulary", back_populates="progresses")


if __name__ == "__main__":
    print("Đang kết nối và thiết lập bảng trên Supabase...")
    Base.metadata.create_all(bind=engine)
    print("Hoàn tất! Hãy kiểm tra Table Editor trên Supabase.")