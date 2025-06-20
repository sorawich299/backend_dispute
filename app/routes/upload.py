from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
import zipfile, shutil, tempfile
from pathlib import Path
import patoolib
from app.auth import is_logged_in
from app.services.file_processor import process_excel
from app.services.updater import update_dispute

router = APIRouter()

@router.post("/upload/", response_class=HTMLResponse)
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
                enf_id = str(row["เลขที่ติดตามทวงถาม"]).replace("DIP", "EFM")
                gov_result = row["ผลพิจารณา ทล."]
                gov_name = result["cell_b1"]
                status, error = update_dispute(enf_id, gov_name, gov_result)
                summary.append((enf_id, gov_result, status, error))
        return HTMLResponse(f"<pre>{summary}</pre>")
    finally:
        shutil.rmtree(temp_dir)