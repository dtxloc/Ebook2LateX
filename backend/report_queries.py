from sqlalchemy import func

from app.database import SessionLocal
from app.models import Document, FormulaEntry, User


def report_users_document_count() -> None:
    db = SessionLocal()
    try:
        rows = (
            db.query(
                User.username_email,
                User.full_name,
                func.count(Document.id).label("document_count"),
            )
            .outerjoin(Document, Document.user_id == User.user_id)
            .group_by(User.username_email, User.full_name)
            .order_by(User.username_email)
            .all()
        )

        print("Danh sach user va so luong tai lieu:")
        for email, name, count in rows:
            print(f"- {name or 'N/A'} ({email}): {count}")
    finally:
        db.close()


def search_formula_by_keyword(keyword: str) -> None:
    db = SessionLocal()
    try:
        formulas = (
            db.query(FormulaEntry)
            .filter(FormulaEntry.latex_content.ilike(f"%{keyword}%"))
            .order_by(FormulaEntry.created_at.desc())
            .all()
        )

        print(f"Tim thay {len(formulas)} cong thuc cho tu khoa '{keyword}':")
        for formula in formulas:
            print(f"- {formula.id}: {formula.latex_content}")
    finally:
        db.close()


if __name__ == "__main__":
    report_users_document_count()
    search_formula_by_keyword("sqrt")
