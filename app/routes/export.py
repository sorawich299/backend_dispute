from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, RedirectResponse
import pandas as pd
from app.auth import is_logged_in
from app.database import get_db
import io

router = APIRouter()

@router.get("/export")
def export_data(request: Request):
    if not is_logged_in(request):
        return RedirectResponse("/login")
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM UPDATE_LOG ORDER BY UPDATED_AT DESC", conn)
    conn.close()
    stream = io.BytesIO()
    df.to_excel(stream, index=False, engine='openpyxl')
    stream.seek(0)
    return StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=export_log.xlsx"})