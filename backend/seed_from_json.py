import json
import uuid
from pathlib import Path

from app.database import SessionLocal
from app.models import Document, FormulaEntry, User


def seed_from_json() -> None:
    db = SessionLocal()
    try:
        data_path = Path(__file__).resolve().parent / "data.json"
        formulas = json.loads(data_path.read_text(encoding="utf-8"))

        user = db.query(User).filter(User.username_email == "json.seed@ebook2latex.local").first()
        if user is None:
            user = User(
                user_id=uuid.uuid4(),
                username_email="json.seed@ebook2latex.local",
                password_hash="hashed_password_here",
                full_name="JSON Seeder",
                role="Editor",
            )
            db.add(user)
            db.flush()

        doc = Document(
            id=uuid.uuid4(),
            user_id=user.user_id,
            file_name="json_formulas.pdf",
            file_path_url="/uploads/json_formulas.pdf",
            status="Completed",
        )
        db.add(doc)
        db.flush()

        for idx, latex in enumerate(formulas, start=1):
            db.add(
                FormulaEntry(
                    id=uuid.uuid4(),
                    document_id=doc.id,
                    latex_content=latex,
                    order_index=idx,
                )
            )

        db.commit()
        print(f"Da nap {len(formulas)} cong thuc tu data.json")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_from_json()
