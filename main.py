from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from pydantic import BaseModel
# Import các bảng và engine từ file database.py của bạn
from database import engine, Vocabulary, UserProgress, User, VocabularySet

# Khởi tạo phiên làm việc với Database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="Website Learning Vocab API")

# Cấu hình CORS để Frontend (HTML/JS) có thể gọi được API mà không bị chặn
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hàm Dependency để mở và đóng kết nối DB tự động cho mỗi request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- SCHEMA (Định nghĩa cấu trúc dữ liệu gửi lên) ---
class ProgressUpdate(BaseModel):
    user_id: int
    vocab_id: int
    is_learned: bool

# --- API ENDPOINTS ---

@app.get("/api/sets/{set_id}/flashcards")
def get_flashcards(set_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """API lấy danh sách từ vựng của một bộ từ (Vocabulary Set)"""
    # Lấy các từ vựng thuộc set_id
    vocabularies = db.query(Vocabulary).filter(Vocabulary.set_id == set_id).all()
    
    # Do database đang trống, mình trả về danh sách rỗng để test connection trước
    return {
        "set_id": set_id,
        "total_words": len(vocabularies),
        "words": vocabularies
    }

@app.post("/api/progress/update")
def update_progress(data: ProgressUpdate, db: Session = Depends(get_db)):
    """API lưu tiến độ học của người dùng"""
    # MVP Nhóm 1: Nhận request và báo thành công
    return {
        "status": "success", 
        "message": f"Đã lưu trạng thái (Thuộc: {data.is_learned}) cho từ vựng ID {data.vocab_id}"
    }
# --- Khai báo cấu trúc dữ liệu từ vựng gửi lên ---
class VocabCreate(BaseModel):
    set_id: int
    word: str
    phonetic: str = ""
    part_of_speech: str = ""
    meaning: str
    example: str = ""
    example_translation: str = ""

# --- API thêm từ vựng mới ---
@app.post("/api/words")
def create_word(data: VocabCreate, db: Session = Depends(get_db)):
    """API lưu từ vựng mới vào Supabase"""
    new_vocab = Vocabulary(
        set_id=data.set_id,
        word=data.word,
        phonetic=data.phonetic,
        part_of_speech=data.part_of_speech,
        meaning=data.meaning,
        example=data.example,
        example_translation=data.example_translation
    )
    db.add(new_vocab)
    db.commit()
    return {"message": "Đã thêm từ vựng thành công!"}