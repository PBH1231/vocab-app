from database import engine, User, VocabularySet, Vocabulary
from sqlalchemy.orm import sessionmaker

# Khởi tạo kết nối tới Supabase
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed_data():
    # 1. Kiểm tra xem đã có dữ liệu chưa để tránh trùng lặp
    if db.query(User).first():
        print("Dữ liệu mẫu đã tồn tại trên Supabase, không cần bơm thêm.")
        return

    print("Đang tạo người dùng mẫu...")
    test_user = User(username="admin_huy", password_hash="hashed_password_123")
    db.add(test_user)
    db.commit() # Lưu để lấy ID

    print("Đang tạo bộ từ vựng mẫu...")
    vocab_set = VocabularySet(
        title="TOEIC Essential Words", 
        description="Bộ 600 từ vựng cốt lõi cho kỳ thi TOEIC"
    )
    db.add(vocab_set)
    db.commit() # Lưu để lấy ID
    
    print("Đang bơm danh sách từ vựng...")
    words = [
        Vocabulary(
            set_id=vocab_set.id,
            word="Incorporate",
            phonetic="/inˈkôrpəˌrāt/",
            part_of_speech="verb",
            meaning="Kết hợp, sát nhập",
            example="We will incorporate your suggestions into the master plan.",
            example_translation="Chúng tôi sẽ kết hợp các đề xuất của bạn vào bản kế hoạch tổng thể."
        ),
        Vocabulary(
            set_id=vocab_set.id,
            word="Proactive",
            phonetic="/prōˈaktiv/",
            part_of_speech="adjective",
            meaning="Chủ động",
            example="We need to be proactive in managing the database.",
            example_translation="Chúng ta cần chủ động trong việc quản trị cơ sở dữ liệu."
        ),
        Vocabulary(
            set_id=vocab_set.id,
            word="Facilitate",
            phonetic="/fəˈsiləˌtāt/",
            part_of_speech="verb",
            meaning="Tạo điều kiện, làm cho dễ dàng",
            example="The new software will facilitate the learning process.",
            example_translation="Phần mềm mới sẽ tạo điều kiện thuận lợi cho quá trình học tập."
        )
    ]
    
    db.add_all(words)
    db.commit()
    print("🎉 Bơm dữ liệu thành công! Hãy kiểm tra lại API.")

if __name__ == "__main__":
    seed_data()
    db.close()