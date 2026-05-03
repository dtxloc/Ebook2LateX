from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Document, FormulaEntry, Log, User, UserFavorite
from app.schemas import (
	DocumentCreate,
	DocumentRead,
	DocumentUpdate,
	FavoriteCreate,
	FavoriteRead,
	FormulaEntryCreate,
	FormulaEntryRead,
	FormulaEntryUpdate,
	LogCreate,
	LogRead,
	UserCreate,
	UserDocumentCountRead,
	UserRead,
	UserUpdate,
)

app = FastAPI(
	title="Ebook2LateX Web Services",
	version="0.1.0",
	description="REST API minh hoa mo hinh client-server cho Ebook2LateX.",
)


def _escape_text(value):
	if value is None:
		return ""
	return (
		str(value)
		.replace("&", "&amp;")
		.replace("<", "&lt;")
		.replace(">", "&gt;")
		.replace('"', "&quot;")
	)


def _layout(title: str, body: str) -> HTMLResponse:
	page = f"""<!doctype html>
<html lang="vi">
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>{_escape_text(title)}</title>
	<style>
		:root {{
			--bg: #08111f;
			--panel: rgba(10, 18, 32, 0.84);
			--panel-2: rgba(16, 27, 46, 0.96);
			--border: rgba(148, 163, 184, 0.18);
			--text: #e5eefb;
			--muted: #9bb0cb;
			--accent: #7dd3fc;
			--accent-2: #38bdf8;
			--good: #34d399;
			--shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
			font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
		}}
		* {{ box-sizing: border-box; }}
		body {{
			margin: 0;
			color: var(--text);
			background:
				radial-gradient(circle at top left, rgba(56, 189, 248, 0.25), transparent 28%),
				radial-gradient(circle at right top, rgba(125, 211, 252, 0.12), transparent 25%),
				linear-gradient(180deg, #060b16 0%, var(--bg) 100%);
			min-height: 100vh;
		}}
		.wrap {{ max-width: 1180px; margin: 0 auto; padding: 32px 20px 56px; }}
		.hero {{
			padding: 28px;
			border: 1px solid var(--border);
			border-radius: 24px;
			background: linear-gradient(180deg, rgba(12, 20, 36, 0.96), rgba(9, 15, 28, 0.92));
			box-shadow: var(--shadow);
			overflow: hidden;
			position: relative;
		}}
		.hero::after {{
			content: "";
			position: absolute;
			inset: auto -80px -120px auto;
			width: 280px;
			height: 280px;
			border-radius: 50%;
			background: radial-gradient(circle, rgba(56, 189, 248, 0.18), transparent 70%);
			filter: blur(10px);
			pointer-events: none;
		}}
		.eyebrow {{
			display: inline-flex;
			padding: 6px 12px;
			border-radius: 999px;
			border: 1px solid rgba(125, 211, 252, 0.25);
			color: var(--accent);
			background: rgba(8, 17, 31, 0.75);
			font-size: 12px;
			letter-spacing: 0.08em;
			text-transform: uppercase;
		}}
		h1 {{ margin: 16px 0 10px; font-size: clamp(32px, 5vw, 56px); line-height: 1.03; }}
		.lede {{ color: var(--muted); max-width: 780px; font-size: 16px; line-height: 1.7; margin: 0; }}
		.grid {{ display: grid; gap: 18px; margin-top: 22px; grid-template-columns: repeat(12, minmax(0, 1fr)); }}
		.card {{
			border: 1px solid var(--border);
			border-radius: 20px;
			background: var(--panel);
			backdrop-filter: blur(18px);
			box-shadow: var(--shadow);
		}}
		.card.pad {{ padding: 20px; }}
		.card h2, .card h3 {{ margin: 0 0 12px; }}
		.muted {{ color: var(--muted); }}
		.stats {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-top: 18px; }}
		.stat {{ padding: 18px; border-radius: 18px; background: rgba(10, 18, 32, 0.72); border: 1px solid var(--border); }}
		.stat strong {{ display: block; font-size: 26px; margin-bottom: 6px; }}
		.controls {{ display: grid; gap: 12px; grid-template-columns: 1fr auto; }}
		input[type="text"], input[type="email"], input[type="url"], input[type="number"], textarea, select {{
			width: 100%;
			color: var(--text);
			background: rgba(3, 8, 20, 0.72);
			border: 1px solid var(--border);
			border-radius: 14px;
			padding: 12px 14px;
			outline: none;
		}}
		textarea {{ min-height: 96px; resize: vertical; }}
		button, .btn {{
			appearance: none;
			border: 0;
			border-radius: 14px;
			padding: 12px 16px;
			background: linear-gradient(135deg, var(--accent-2), #0ea5e9);
			color: #04111f;
			font-weight: 700;
			cursor: pointer;
			text-decoration: none;
			display: inline-flex;
			align-items: center;
			justify-content: center;
			gap: 8px;
		}}
		.btn.secondary {{ background: rgba(15, 23, 42, 0.92); color: var(--text); border: 1px solid var(--border); }}
		.sections {{ display: grid; gap: 18px; margin-top: 18px; grid-template-columns: repeat(12, minmax(0, 1fr)); }}
		.span-8 {{ grid-column: span 8; }}
		.span-4 {{ grid-column: span 4; }}
		.span-12 {{ grid-column: span 12; }}
		.table-wrap {{ overflow: auto; border-radius: 16px; border: 1px solid var(--border); }}
		table {{ width: 100%; border-collapse: collapse; min-width: 760px; background: rgba(6, 11, 20, 0.45); }}
		th, td {{ padding: 12px 14px; border-bottom: 1px solid rgba(148, 163, 184, 0.12); text-align: left; vertical-align: top; }}
		th {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); background: rgba(15, 23, 42, 0.72); }}
		code, pre {{ font-family: Consolas, "SFMono-Regular", ui-monospace, monospace; }}
		.pill {{ display: inline-flex; padding: 5px 10px; border-radius: 999px; background: rgba(52, 211, 153, 0.14); color: #a7f3d0; font-size: 12px; }}
		.formula {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; white-space: pre-wrap; word-break: break-word; }}
		.stack {{ display: grid; gap: 12px; }}
		.stack > * {{ margin: 0; }}
		.links {{ display: flex; gap: 12px; flex-wrap: wrap; margin-top: 18px; }}
		.section-title {{ display: flex; align-items: baseline; justify-content: space-between; gap: 12px; margin-bottom: 14px; }}
		@media (max-width: 920px) {{
			.stats, .sections {{ grid-template-columns: 1fr; }}
			.span-4, .span-8, .span-12 {{ grid-column: span 1; }}
			.controls {{ grid-template-columns: 1fr; }}
		}}
	</style>
</head>
<body>
	<main class="wrap">
		{body}
	</main>
</body>
</html>"""
	return HTMLResponse(page)


def _landing_body(user_count: int, document_count: int, formula_count: int, log_count: int, favorite_count: int, latest_formulas):
	rows = "".join(
		f"<tr><td>{_escape_text(item.id)}</td><td class='formula'>{_escape_text(item.latex_content or '')}</td><td>{_escape_text(item.order_index)}</td><td>{_escape_text(item.document_id)}</td></tr>"
		for item in latest_formulas
	)
	if not rows:
		rows = "<tr><td colspan='4' class='muted'>Chua co du lieu cong thuc.</td></tr>"

	return f"""
		<section class="hero">
			<span class="eyebrow">Ebook2LateX Web Services</span>
			<h1>Giao dien web thay cho JSON, van giu nguyen REST API phia sau.</h1>
			<p class="lede">Trang nay minh hoa mo hinh client-server: trinh duyet gui request toi FastAPI, server truy van PostgreSQL va tra ve giao dien HTML de nguoi dung xem du lieu de hieu hon.</p>
			<div class="links">
				<a class="btn" href="/formula-entries/search">Tim cong thuc</a>
				<a class="btn secondary" href="/baitap/10a/7">Bai tap 10a</a>
				<a class="btn secondary" href="/baitap/10b/Nike/42">Bai tap 10b</a>
				<a class="btn secondary" href="/docs">Mo Swagger UI</a>
				<a class="btn secondary" href="/demo/client-server">Xem demo JSON</a>
			</div>
			<div class="stats">
				<div class="stat"><strong>{user_count}</strong><span>Users</span></div>
				<div class="stat"><strong>{document_count}</strong><span>Documents</span></div>
				<div class="stat"><strong>{formula_count}</strong><span>Formula entries</span></div>
				<div class="stat"><strong>{log_count}</strong><span>Logs</span></div>
				<div class="stat"><strong>{favorite_count}</strong><span>Favorites</span></div>
			</div>
		</section>

		<section class="sections">
			<article class="card pad span-8">
				<div class="section-title">
					<h2>Cong thuc moi nhat</h2>
					<span class="pill">UI rendering</span>
				</div>
				<div class="table-wrap">
					<table>
						<thead>
							<tr><th>ID</th><th>LaTeX</th><th>Order</th><th>Document</th></tr>
						</thead>
						<tbody>{rows}</tbody>
					</table>
				</div>
			</article>

			<aside class="card pad span-4">
				<h3>Menu nhanh</h3>
				<div class="stack muted">
					<p>- <a href="/formula-entries/search">Trang tim kiem cong thuc</a></p>
					<p>- <a href="/baitap/10a/7">Bai tap 10a</a></p>
					<p>- <a href="/baitap/10b/Nike/42">Bai tap 10b</a></p>
					<p>- <a href="/reports/users-document-count">API bao cao users/documents</a></p>
					<p>- <a href="/openapi.json">OpenAPI schema</a></p>
					<p>- <a href="/health">Health check</a></p>
				</div>
				<p class="muted" style="margin-top: 16px;">Cac API JSON van nam o duong dan <code>/api</code> va cac route hien co.</p>
			</aside>
		</section>
"""


def _exercise_body(title: str, subtitle: str, value_rows: str, answer: str):
	return f"""
		<section class="hero">
			<span class="eyebrow">Bai tap web services</span>
			<h1>{_escape_text(title)}</h1>
			<p class="lede">{_escape_text(subtitle)}</p>
		</section>

		<section class="sections">
			<article class="card pad span-8">
				<div class="section-title">
					<h2>Du lieu nhan tu URL</h2>
					<span class="pill">Request path</span>
				</div>
				<div class="table-wrap">
					<table>
						<thead><tr><th>Thong tin</th><th>Gia tri</th></tr></thead>
						<tbody>{value_rows}</tbody>
					</table>
				</div>
			</article>

			<aside class="card pad span-4">
				<h3>Ket qua</h3>
				<p class="lede">{_escape_text(answer)}</p>
				<div class="links">
					<a class="btn secondary" href="/">Ve trang chu</a>
					<a class="btn secondary" href="/formula-entries/search?keyword=sqrt">Thu tim cong thuc</a>
				</div>
			</aside>
		</section>
	"""


def _search_body(keyword: str, results):
	result_rows = "".join(
		f"""
				<tr>
					<td>{_escape_text(item.id)}</td>
					<td class="formula">{_escape_text(item.latex_content or '')}</td>
					<td>{_escape_text(item.order_index)}</td>
					<td>{_escape_text(item.document_id)}</td>
					<td>{_escape_text(item.created_at)}</td>
				</tr>
				"""
		for item in results
	)
	if not result_rows:
		result_rows = "<tr><td colspan='5' class='muted'>Khong tim thay cong thuc phu hop.</td></tr>"

	return f"""
		<section class="hero">
			<span class="eyebrow">Tim kiem cong thuc</span>
			<h1>Giao dien tim kiem thay cho JSON raw.</h1>
			<p class="lede">Nhap tu khoa, server se truy van PostgreSQL va tra ve danh sach cong thuc trong bang HTML de quan sat truc quan hon.</p>
			<form method="get" action="/formula-entries/search" class="controls" style="margin-top: 20px;">
				<input type="text" name="keyword" value="{_escape_text(keyword)}" placeholder="Vi du: sqrt, integral, sum, bayes">
				<button type="submit">Tim kiem</button>
			</form>
		</section>

		<section class="sections">
			<article class="card pad span-12">
				<div class="section-title">
					<h2>Ket qua cho: {_escape_text(keyword or '...')}</h2>
					<span class="pill">{len(results)} records</span>
				</div>
				<div class="table-wrap">
					<table>
						<thead>
							<tr><th>ID</th><th>LaTeX</th><th>Order</th><th>Document</th><th>Created</th></tr>
						</thead>
						<tbody>{result_rows}</tbody>
					</table>
				</div>
			</article>

			<aside class="card pad span-12">
				<h3>Goi y</h3>
				<p class="muted">Muốn xem JSON gốc, hãy dùng API riêng như <code>/api/formula-entries/search?keyword=sqrt</code> hoặc mở Swagger UI ở <a href="/docs">/docs</a>.</p>
			</aside>
		</section>
"""


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def _get_or_404(db: Session, model, object_id: UUID):
	instance = db.get(model, object_id)
	if instance is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"{model.__name__} not found",
		)
	return instance


@app.get("/", response_class=HTMLResponse)
def read_root(db: Session = Depends(get_db)):
	latest_formulas = (
		db.query(FormulaEntry)
		.order_by(FormulaEntry.created_at.desc())
		.limit(8)
		.all()
	)
	user_count = db.query(func.count(User.user_id)).scalar() or 0
	document_count = db.query(func.count(Document.id)).scalar() or 0
	formula_count = db.query(func.count(FormulaEntry.id)).scalar() or 0
	log_count = db.query(func.count(Log.log_id)).scalar() or 0
	favorite_count = db.query(func.count(UserFavorite.favorite_id)).scalar() or 0
	body = _landing_body(
		user_count=user_count,
		document_count=document_count,
		formula_count=formula_count,
		log_count=log_count,
		favorite_count=favorite_count,
		latest_formulas=latest_formulas,
	)
	return _layout("Ebook2LateX", body)


@app.get("/health")
def health_check():
	return {"status": "ok"}


@app.get("/demo/client-server")
def client_server_demo():
	return {
		"client": "trinh duyet hoac ung dung HTTP",
		"server": "FastAPI/Uvicorn",
		"protocol": "HTTP",
		"flow": [
			"Client gui request",
			"Server xu ly request",
			"Server tra response",
			"Client hien thi ket qua",
		],
	}


@app.get("/baitap/10a/{number}", response_class=HTMLResponse)
def bai_tap_10a(number: float):
	result = number * 10
	value_rows = f"""
		<tr><td>So nhan vao</td><td>{_escape_text(number)}</td></tr>
		<tr><td>Phep tinh</td><td>{_escape_text(number)} x 10</td></tr>
		<tr><td>Ket qua</td><td><strong>{_escape_text(result)}</strong></td></tr>
	"""
	answer = f"Ket qua la {result}"
	return _layout(
		"Bai tap 10a",
		_exercise_body(
			"Bai tap 10a: Nhan so voi 10",
			"Nhap mot so tren thanh dia chi, FastAPI se nhan so do voi 10 va tra ket qua ve trinh duyet.",
			value_rows,
			answer,
		),
	)


@app.get("/baitap/10b/{brand}/{size}", response_class=HTMLResponse)
def bai_tap_10b(brand: str, size: int):
	answer = f"Ban muon mua giay {brand} kich thuoc {size} dung khong?"
	value_rows = f"""
		<tr><td>Brand</td><td>{_escape_text(brand)}</td></tr>
		<tr><td>Size</td><td>{_escape_text(size)}</td></tr>
		<tr><td>Cau tra loi</td><td><strong>{_escape_text(answer)}</strong></td></tr>
	"""
	return _layout(
		"Bai tap 10b",
		_exercise_body(
			"Bai tap 10b: Nhan brand va size giay",
			"Nhap brand va size tren thanh dia chi, FastAPI se tra ve cau xac nhan dung theo de bai.",
			value_rows,
			answer,
		),
	)


@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
	existing_user = db.query(User).filter(User.username_email == payload.username_email).first()
	if existing_user:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

	user = User(**payload.model_dump())
	db.add(user)
	db.commit()
	db.refresh(user)
	return user


@app.get("/users", response_model=list[UserRead])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	return (
		db.query(User)
		.order_by(User.created_at.desc())
		.offset(skip)
		.limit(limit)
		.all()
	)


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
	return _get_or_404(db, User, user_id)


@app.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: UUID, payload: UserUpdate, db: Session = Depends(get_db)):
	user = _get_or_404(db, User, user_id)
	updates = payload.model_dump(exclude_unset=True)
	for field, value in updates.items():
		setattr(user, field, value)
	db.commit()
	db.refresh(user)
	return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
	user = _get_or_404(db, User, user_id)
	db.delete(user)
	db.commit()
	return None


@app.get("/users/{user_id}/documents", response_model=list[DocumentRead])
def list_documents_by_user(user_id: UUID, db: Session = Depends(get_db)):
	_get_or_404(db, User, user_id)
	return (
		db.query(Document)
		.filter(Document.user_id == user_id)
		.order_by(Document.upload_date.desc())
		.all()
	)


@app.post("/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
def create_document(payload: DocumentCreate, db: Session = Depends(get_db)):
	if payload.user_id is not None:
		_get_or_404(db, User, payload.user_id)

	document = Document(**payload.model_dump())
	db.add(document)
	db.commit()
	db.refresh(document)
	return document


@app.get("/documents", response_model=list[DocumentRead])
def list_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	return (
		db.query(Document)
		.order_by(Document.upload_date.desc())
		.offset(skip)
		.limit(limit)
		.all()
	)


@app.get("/documents/{document_id}", response_model=DocumentRead)
def get_document(document_id: UUID, db: Session = Depends(get_db)):
	return _get_or_404(db, Document, document_id)


@app.put("/documents/{document_id}", response_model=DocumentRead)
def update_document(document_id: UUID, payload: DocumentUpdate, db: Session = Depends(get_db)):
	document = _get_or_404(db, Document, document_id)
	updates = payload.model_dump(exclude_unset=True)
	if "user_id" in updates and updates["user_id"] is not None:
		_get_or_404(db, User, updates["user_id"])
	for field, value in updates.items():
		setattr(document, field, value)
	db.commit()
	db.refresh(document)
	return document


@app.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: UUID, db: Session = Depends(get_db)):
	document = _get_or_404(db, Document, document_id)
	db.delete(document)
	db.commit()
	return None


@app.get("/documents/{document_id}/formulas", response_model=list[FormulaEntryRead])
def list_formulas_by_document(document_id: UUID, db: Session = Depends(get_db)):
	_get_or_404(db, Document, document_id)
	return (
		db.query(FormulaEntry)
		.filter(FormulaEntry.document_id == document_id)
		.order_by(FormulaEntry.order_index.asc())
		.all()
	)


@app.post("/formula-entries", response_model=FormulaEntryRead, status_code=status.HTTP_201_CREATED)
def create_formula_entry(payload: FormulaEntryCreate, db: Session = Depends(get_db)):
	_get_or_404(db, Document, payload.document_id)
	formula = FormulaEntry(**payload.model_dump())
	db.add(formula)
	db.commit()
	db.refresh(formula)
	return formula

@app.get("/formula-entries", response_model=list[FormulaEntryRead])
def list_formula_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	return (
		db.query(FormulaEntry)
		.order_by(FormulaEntry.created_at.desc())
		.offset(skip)
		.limit(limit)
		.all()
	)


@app.get("/formula-entries/search", response_class=HTMLResponse)
def search_formulas_page(
	keyword: str = Query("", description="Search text for latex_content"),
	db: Session = Depends(get_db),
):
	results = []
	if keyword:
		results = (
			db.query(FormulaEntry)
			.filter(FormulaEntry.latex_content.ilike(f"%{keyword}%"))
			.order_by(FormulaEntry.created_at.desc())
			.all()
		)
	body = _search_body(keyword, results)
	return _layout("Tim kiem cong thuc", body)


@app.get("/api/formula-entries/search", response_model=list[FormulaEntryRead])
def search_formulas_api(
	keyword: str = Query(..., min_length=1, description="Search text for latex_content"),
	db: Session = Depends(get_db),
):
	return (
		db.query(FormulaEntry)
		.filter(FormulaEntry.latex_content.ilike(f"%{keyword}%"))
		.order_by(FormulaEntry.created_at.desc())
		.all()
	)


@app.get("/formula-entries/{formula_id}", response_model=FormulaEntryRead)
def get_formula_entry(formula_id: UUID, db: Session = Depends(get_db)):
	return _get_or_404(db, FormulaEntry, formula_id)


@app.put("/formula-entries/{formula_id}", response_model=FormulaEntryRead)
def update_formula_entry(formula_id: UUID, payload: FormulaEntryUpdate, db: Session = Depends(get_db)):
	formula = _get_or_404(db, FormulaEntry, formula_id)
	updates = payload.model_dump(exclude_unset=True)
	if "document_id" in updates and updates["document_id"] is not None:
		_get_or_404(db, Document, updates["document_id"])
	for field, value in updates.items():
		setattr(formula, field, value)
	db.commit()
	db.refresh(formula)
	return formula


@app.delete("/formula-entries/{formula_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_formula_entry(formula_id: UUID, db: Session = Depends(get_db)):
	formula = _get_or_404(db, FormulaEntry, formula_id)
	db.delete(formula)
	db.commit()
	return None


@app.post("/logs", response_model=LogRead, status_code=status.HTTP_201_CREATED)
def create_log(payload: LogCreate, db: Session = Depends(get_db)):
	if payload.formula_id is not None:
		_get_or_404(db, FormulaEntry, payload.formula_id)
	log = Log(**payload.model_dump())
	db.add(log)
	db.commit()
	db.refresh(log)
	return log


@app.get("/formula-entries/{formula_id}/logs", response_model=list[LogRead])
def list_logs_by_formula(formula_id: UUID, db: Session = Depends(get_db)):
	_get_or_404(db, FormulaEntry, formula_id)
	return (
		db.query(Log)
		.filter(Log.formula_id == formula_id)
		.order_by(Log.timestamp.desc())
		.all()
	)


@app.post("/favorites", response_model=FavoriteRead, status_code=status.HTTP_201_CREATED)
def add_favorite(payload: FavoriteCreate, db: Session = Depends(get_db)):
	_get_or_404(db, User, payload.user_id)
	_get_or_404(db, FormulaEntry, payload.formula_id)

	existing = (
		db.query(UserFavorite)
		.filter(
			UserFavorite.user_id == payload.user_id,
			UserFavorite.formula_id == payload.formula_id,
		)
		.first()
	)
	if existing:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Favorite already exists")

	favorite = UserFavorite(**payload.model_dump())
	db.add(favorite)
	db.commit()
	db.refresh(favorite)
	return favorite


@app.get("/users/{user_id}/favorites", response_model=list[FavoriteRead])
def list_favorites_by_user(user_id: UUID, db: Session = Depends(get_db)):
	_get_or_404(db, User, user_id)
	return (
		db.query(UserFavorite)
		.filter(UserFavorite.user_id == user_id)
		.order_by(UserFavorite.created_at.desc())
		.all()
	)


@app.delete("/favorites/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite(favorite_id: UUID, db: Session = Depends(get_db)):
	favorite = _get_or_404(db, UserFavorite, favorite_id)
	db.delete(favorite)
	db.commit()
	return None


@app.get("/reports/users-document-count", response_model=list[UserDocumentCountRead])
def report_users_document_count(db: Session = Depends(get_db)):
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
	return [
		UserDocumentCountRead(
			username_email=email,
			full_name=name,
			document_count=count,
		)
		for email, name, count in rows
	]
