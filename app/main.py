from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
from pathlib import Path
import pandas as pd
import zipfile
import patoolib
import shutil
import sqlite3
import tempfile
import os
import datetime

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="secret-key")
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fake_user = {"username": "admin", "password_hash": pwd_context.hash("123456")}

def is_logged_in(request: Request):
    return request.session.get("user")

def get_db():
    return sqlite3.connect("local.db")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if not is_logged_in(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == fake_user["username"] and pwd_context.verify(password, fake_user["password_hash"]):
        request.session["user"] = username
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)

@app.post("/upload/")
def upload_file(request: Request, file: UploadFile = File(...)):
    if not is_logged_in(request):
        return RedirectResponse("/login")
    temp_dir = tempfile.mkdtemp()
    file_path = Path(temp_dir) / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    extracted_dir = Path(temp_dir) / "extracted"
    extracted_dir.mkdir()
    try:
        if file.filename.endswith(".zip"):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extracted_dir)
        elif file.filename.endswith(".rar"):
            patoolib.extract_archive(str(file_path), outdir=str(extracted_dir))
        else:
            return HTMLResponse("ไฟล์ไม่รองรับ")

        summary = []
        for excel in extracted_dir.rglob("*.xlsx"):
            result = process_excel(excel)
            for _, row in result["data_table"].iterrows():
                enforcement_id = str(row["เลขที่ติดตามทวงถาม"]).replace("DIP", "EFM")
                gov_result = row["ผลพิจารณา ทล."]
                gov_name = result["cell_b1"]
                status, error = update_dispute(enforcement_id, gov_name, gov_result)
                summary.append((enforcement_id, gov_result, status, error))

        table_html = "<table border='1'><tr><th>ID</th><th>RESULT</th><th>STATUS</th><th>ERROR</th></tr>"
        for row in summary:
            table_html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>"
        table_html += "</table>"
        return HTMLResponse(content=table_html)

    finally:
        shutil.rmtree(temp_dir)

def process_excel(file_path):
    data = pd.read_excel(file_path, sheet_name='Worksheet', header=1).fillna("")
    raw = pd.read_excel(file_path, sheet_name='Worksheet', header=None)
    cell_a1 = raw.iloc[0, 0] if pd.notna(raw.iloc[0, 0]) else ""
    cell_b1 = raw.iloc[0, 1] if pd.notna(raw.iloc[0, 1]) else ""
    return {"cell_a1": cell_a1, "cell_b1": cell_b1, "data_table": data}

def update_dispute(enf_id, gov_name, gov_result):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE DISPUTE SET GOV_NAME=?, GOV_RESULT=?, GOV_UPDATE_DATE=CURRENT_TIMESTAMP
            WHERE ENFORCEMENT_ID=?
        """, (gov_name, gov_result, enf_id))
        status = "SUCCESS" if cursor.rowcount > 0 else "NOT FOUND"
        error = "" if status == "SUCCESS" else "ไม่พบ ENFORCEMENT_ID"
        conn.commit()
    except Exception as e:
        status = "FAIL"
        error = str(e)
    finally:
        cursor.execute("""
            INSERT INTO UPDATE_LOG (ENFORCEMENT_ID, GOV_NAME, GOV_RESULT, STATUS, ERROR_MESSAGE)
            VALUES (?, ?, ?, ?, ?)
        """, (enf_id, gov_name, gov_result, status, error))
        conn.commit()
        conn.close()
    return status, error

@app.get("/history", response_class=HTMLResponse)
def history(request: Request):
    if not is_logged_in(request):
        return RedirectResponse("/login")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT ENFORCEMENT_ID, GOV_NAME, GOV_RESULT, STATUS, ERROR_MESSAGE, UPDATED_AT FROM UPDATE_LOG ORDER BY UPDATED_AT DESC LIMIT 100")
    logs = cursor.fetchall()
    total_success = sum(1 for l in logs if l[3] == "SUCCESS")
    total_failed = sum(1 for l in logs if l[3] == "FAIL")
    return templates.TemplateResponse("history.html", {"request": request, "logs": logs, "total_success": total_success, "total_failed": total_failed})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    if not is_logged_in(request):
        return RedirectResponse("/login")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DATE(UPDATED_AT), STATUS, COUNT(*) FROM UPDATE_LOG GROUP BY DATE(UPDATED_AT), STATUS")
    rows = cursor.fetchall()
    stats = {}
    for day, status, count in rows:
        stats.setdefault(day, {"SUCCESS": 0, "FAIL": 0})
        stats[day][status] = count
    labels = [str(k) for k in stats.keys()]
    success_data = [v["SUCCESS"] for v in stats.values()]
    failed_data = [v["FAIL"] for v in stats.values()]
    total_all = sum(success_data) + sum(failed_data)
    return templates.TemplateResponse("dashboard.html", {"request": request, "labels": labels, "success_data": success_data, "failed_data": failed_data, "total_success": sum(success_data), "total_failed": sum(failed_data), "total_all": total_all})
