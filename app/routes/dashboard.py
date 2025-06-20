from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.auth import is_logged_in
from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
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