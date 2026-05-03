import uuid

from app.database import SessionLocal
from app.models import Document, FormulaEntry, User


def seed_data() -> None:
    db = SessionLocal()
    try:
        print("Dang tao du lieu...")

        existing_user = (
            db.query(User)
            .filter(User.username_email == "teo@dalat.edu.vn")
            .first()
        )
        if existing_user:
            print("Du lieu mau da ton tai, bo qua viec tao moi.")
            return

        test_user = User(
            user_id=uuid.uuid4(),
            username_email="teo@dalat.edu.vn",
            password_hash="hashed_password_here",
            full_name="Le Van Teo",
            role="Admin",
        )
        db.add(test_user)
        db.flush()

        test_doc = Document(
            id=uuid.uuid4(),
            user_id=test_user.user_id,
            file_name="Giao_trinh_Toan_12.pdf",
            file_path_url="/uploads/toan12.pdf",
            status="Completed",
        )
        db.add(test_doc)
        db.flush()

        formula = FormulaEntry(
            id=uuid.uuid4(),
            document_id=test_doc.id,
            latex_content=r"\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
            order_index=1,
        )
        db.add(formula)

        db.commit()
        print("Tao du lieu thanh cong! Hay kiem tra database.")
    except Exception as exc:
        print(f"Co loi xay ra: {exc}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
