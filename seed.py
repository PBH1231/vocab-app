from database import engine, User, VocabularySet, Vocabulary
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def seed_data():
    db = SessionLocal()

    try:
        # Tạo user mẫu nếu chưa có
        user = (
            db.query(User)
            .filter(User.username == "admin_huy")
            .first()
        )

        if not user:
            print("Đang tạo người dùng mẫu...")

            user = User(
                username="admin_huy",
                password_hash="hashed_password_123"
            )

            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            print("Người dùng mẫu đã tồn tại.")

        # Tạo bộ từ vựng mẫu nếu chưa có
        vocab_set = (
            db.query(VocabularySet)
            .filter(VocabularySet.title == "TOEIC Essential Words")
            .first()
        )

        if not vocab_set:
            print("Đang tạo bộ từ vựng mẫu...")

            vocab_set = VocabularySet(
                title="TOEIC Essential Words",
                description="Bộ 600 từ vựng cốt lõi cho kỳ thi TOEIC"
            )

            db.add(vocab_set)
            db.commit()
            db.refresh(vocab_set)
        else:
            print("Bộ từ vựng mẫu đã tồn tại.")

        # Kiểm tra xem bộ này đã có từ chưa
        existing_words_count = (
            db.query(Vocabulary)
            .filter(Vocabulary.set_id == vocab_set.id)
            .count()
        )

        if existing_words_count > 0:
            print("Bộ từ này đã có dữ liệu, không cần bơm thêm.")
            return

        print("Đang bơm danh sách từ vựng...")

        words = [
            Vocabulary(
                set_id=vocab_set.id,
                word="Incorporate",
                phonetic="/ɪnˈkɔːr.pə.reɪt/",
                part_of_speech="verb",
                meaning="Kết hợp, sáp nhập",
                example="We will incorporate your suggestions into the master plan.",
                example_translation="Chúng tôi sẽ kết hợp các đề xuất của bạn vào bản kế hoạch tổng thể."
            ),
            Vocabulary(
                set_id=vocab_set.id,
                word="Proactive",
                phonetic="/ˌproʊˈæk.tɪv/",
                part_of_speech="adjective",
                meaning="Chủ động",
                example="We need to be proactive in managing the database.",
                example_translation="Chúng ta cần chủ động trong việc quản trị cơ sở dữ liệu."
            ),
            Vocabulary(
                set_id=vocab_set.id,
                word="Facilitate",
                phonetic="/fəˈsɪl.ə.teɪt/",
                part_of_speech="verb",
                meaning="Tạo điều kiện, làm cho dễ dàng",
                example="The new software will facilitate the learning process.",
                example_translation="Phần mềm mới sẽ tạo điều kiện thuận lợi cho quá trình học tập."
            ),
            Vocabulary(
                set_id=vocab_set.id,
                word="Serendipity",
                phonetic="/ˌser.ənˈdɪp.ə.ti/",
                part_of_speech="noun",
                meaning="Sự tình cờ may mắn",
                example="Finding my dream job was pure serendipity.",
                example_translation="Việc tìm được công việc mơ ước hoàn toàn là một sự tình cờ may mắn."
            )
        ]

        db.add_all(words)
        db.commit()

        print("Bơm dữ liệu thành công!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()