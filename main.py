from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import func
from pydantic import BaseModel

from database import engine, Vocabulary, UserProgress, User, VocabularySet

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

app = FastAPI(title="Website Learning Vocab API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# SCHEMAS
# =========================

class ProgressUpdate(BaseModel):
    user_id: int
    vocab_id: int
    is_learned: bool


class VocabCreate(BaseModel):
    set_id: int
    word: str
    phonetic: str = ""
    part_of_speech: str = ""
    meaning: str
    example: str = ""
    example_translation: str = ""


class VocabularySetCreate(BaseModel):
    title: str
    description: str = ""


# =========================
# API: VOCABULARY SETS
# =========================

@app.get("/api/sets")
def get_all_sets(db: Session = Depends(get_db)):
    sets = db.query(VocabularySet).all()
    return sets


@app.post("/api/sets")
def create_set(data: VocabularySetCreate, db: Session = Depends(get_db)):
    new_set = VocabularySet(
        title=data.title,
        description=data.description
    )

    db.add(new_set)
    db.commit()
    db.refresh(new_set)

    return {
        "message": "Đã tạo bộ từ vựng thành công!",
        "set": {
            "id": new_set.id,
            "title": new_set.title,
            "description": new_set.description
        }
    }


@app.get("/api/sets/{set_id}/flashcards")
def get_flashcards(
    set_id: int,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    vocab_set = (
        db.query(VocabularySet)
        .filter(VocabularySet.id == set_id)
        .first()
    )

    if not vocab_set:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy bộ từ vựng"
        )

    vocabularies = (
        db.query(Vocabulary)
        .filter(Vocabulary.set_id == set_id)
        .all()
    )

    return {
        "set_id": set_id,
        "set_title": vocab_set.title,
        "total_words": len(vocabularies),
        "words": vocabularies
    }


# =========================
# API: VOCABULARIES
# =========================

@app.post("/api/words")
def create_word(data: VocabCreate, db: Session = Depends(get_db)):
    vocab_set = (
        db.query(VocabularySet)
        .filter(VocabularySet.id == data.set_id)
        .first()
    )

    if not vocab_set:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy bộ từ vựng để thêm từ"
        )

    existing_word = (
        db.query(Vocabulary)
        .filter(
            Vocabulary.set_id == data.set_id,
            func.lower(Vocabulary.word) == data.word.strip().lower()
        )
        .first()
    )

    if existing_word:
        raise HTTPException(
            status_code=400,
            detail="Từ này đã tồn tại trong bộ từ vựng"
        )

    new_vocab = Vocabulary(
    set_id=data.set_id,
    word=data.word.strip(),
    phonetic=data.phonetic.strip(),
    part_of_speech=data.part_of_speech.strip(),
    meaning=data.meaning.strip(),
    example=data.example.strip(),
    example_translation=data.example_translation.strip()
    )

    db.add(new_vocab)
    db.commit()
    db.refresh(new_vocab)

    return {
        "message": "Đã thêm từ vựng thành công!",
        "word": {
            "id": new_vocab.id,
            "set_id": new_vocab.set_id,
            "word": new_vocab.word,
            "phonetic": new_vocab.phonetic,
            "part_of_speech": new_vocab.part_of_speech,
            "meaning": new_vocab.meaning,
            "example": new_vocab.example,
            "example_translation": new_vocab.example_translation
        }
    }


# =========================
# API: USER PROGRESS
# =========================

@app.post("/api/progress/update")
def update_progress(
    data: ProgressUpdate,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == data.user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy người dùng"
        )

    vocabulary = (
        db.query(Vocabulary)
        .filter(Vocabulary.id == data.vocab_id)
        .first()
    )

    if not vocabulary:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy từ vựng"
        )

    progress = (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == data.user_id,
            UserProgress.vocab_id == data.vocab_id
        )
        .first()
    )

    if progress:
        progress.is_learned = data.is_learned
    else:
        progress = UserProgress(
            user_id=data.user_id,
            vocab_id=data.vocab_id,
            is_learned=data.is_learned
        )
        db.add(progress)

    db.commit()
    db.refresh(progress)

    return {
        "status": "success",
        "message": "Đã lưu tiến độ học",
        "progress": {
            "id": progress.id,
            "user_id": progress.user_id,
            "vocab_id": progress.vocab_id,
            "is_learned": progress.is_learned,
            "last_reviewed": progress.last_reviewed
        }
    }

# =========================
# API: SỬA VÀ XÓA BỘ TỪ VỰNG
# =========================

@app.put("/api/sets/{set_id}")
def update_set(set_id: int, data: VocabularySetCreate, db: Session = Depends(get_db)):
    vocab_set = db.query(VocabularySet).filter(VocabularySet.id == set_id).first()
    if not vocab_set:
        raise HTTPException(status_code=404, detail="Không tìm thấy bộ từ vựng")
    
    vocab_set.title = data.title
    vocab_set.description = data.description
    db.commit()
    return {"message": "Đã cập nhật thành công"}

@app.delete("/api/sets/{set_id}")
def delete_set(set_id: int, db: Session = Depends(get_db)):
    vocab_set = db.query(VocabularySet).filter(VocabularySet.id == set_id).first()
    if not vocab_set:
        raise HTTPException(status_code=404, detail="Không tìm thấy bộ từ vựng")
    
    # Dọn dẹp dữ liệu con: Lấy các từ vựng thuộc bộ này
    words = db.query(Vocabulary).filter(Vocabulary.set_id == set_id).all()
    for word in words:
        # Xóa tiến độ học của từng từ
        db.query(UserProgress).filter(UserProgress.vocab_id == word.id).delete()
    
    # Xóa các từ vựng trong bộ
    db.query(Vocabulary).filter(Vocabulary.set_id == set_id).delete()
    # Cuối cùng mới xóa Bộ từ vựng
    db.delete(vocab_set)
    db.commit()
    
    return {"message": "Đã xóa bộ từ vựng thành công"}
# =========================
# API: THỐNG KÊ TIẾN ĐỘ HỌC
# =========================

@app.get("/api/progress/stats")
def get_progress_stats(user_id: int = 1, db: Session = Depends(get_db)):
    total_words = db.query(Vocabulary).count()
    learned_words = db.query(UserProgress).filter(
        UserProgress.user_id == user_id, 
        UserProgress.is_learned == True
    ).count()
    need_review = total_words - learned_words
    
    return {
        "total_words": total_words,
        "learned_words": learned_words,
        "need_review": need_review
    }

# =========================
# API: ÔN TẬP TỪ CHƯA THUỘC
# =========================

@app.get("/api/sets/{set_id}/unlearned")
def get_unlearned_flashcards(set_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    vocab_set = db.query(VocabularySet).filter(VocabularySet.id == set_id).first()
    if not vocab_set:
        raise HTTPException(status_code=404, detail="Không tìm thấy bộ từ")

    # Lấy tất cả từ trong bộ
    words = db.query(Vocabulary).filter(Vocabulary.set_id == set_id).all()
    
    # Tìm các từ người dùng ĐÃ đánh dấu là "Đã thuộc"
    learned_progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.vocab_id.in_([w.id for w in words]),
        UserProgress.is_learned == True
    ).all()
    learned_ids = [p.vocab_id for p in learned_progress]
    
    # Lọc ra những từ CHƯA THUỘC (tức là không nằm trong danh sách Đã thuộc)
    unlearned_words = [w for w in words if w.id not in learned_ids]
    
    return {
        "set_id": set_id,
        "set_title": vocab_set.title + " (Chỉ ôn từ chưa thuộc)",
        "total_words": len(unlearned_words),
        "words": unlearned_words
    }