import random
import uuid

from faker import Faker

from app.database import SessionLocal
from app.models import Document, FormulaEntry, User

fake = Faker("vi_VN")


def seed_large_data(user_count: int = 50) -> None:
    db = SessionLocal()
    try:
        print(f"Dang tao {user_count} nguoi dung gia lap...")

        for _ in range(user_count):
            email = fake.unique.email()
            user = User(
                user_id=uuid.uuid4(),
                username_email=email,
                password_hash="hashed_password_here",
                full_name=fake.name(),
                role=random.choice(["Viewer", "Editor", "Admin"]),
            )
            db.add(user)
            db.flush()

            doc_count = random.randint(2, 5)
            for _ in range(doc_count):
                file_stub = fake.file_name(extension="pdf")
                document = Document(
                    id=uuid.uuid4(),
                    user_id=user.user_id,
                    file_name=file_stub,
                    file_path_url=f"/uploads/{file_stub}",
                    status=random.choice(["Pending", "Processed", "Completed", "Error"]),
                    version=random.randint(1, 3),
                )
                db.add(document)
                db.flush()

                for idx in range(1, random.randint(2, 6)):
                    db.add(
                        FormulaEntry(
                            id=uuid.uuid4(),
                            document_id=document.id,
                            latex_content=random.choice(
                                [
                                    r"\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
                                    r"\int_0^{\pi} \sin(x)\,dx = 2",
                                    r"\sum_{i=1}^n i = \frac{n(n+1)}{2}",
                                    r"e^{i\pi} + 1 = 0",
                                ]
                            ),
                            order_index=idx,
                        )
                    )

        db.commit()
        print("Seeding bang Faker thanh cong.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_large_data()
