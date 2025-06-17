import pytest
import httpx
import zipfile
import os
import io
import pandas as pd

@pytest.fixture
def sample_zip(tmp_path):
    excel_path = tmp_path / "test.xlsx"
    df = pd.DataFrame({
        "เลขที่ติดตามทวงถาม": ["DIP0001", "DIP0002"],
        "ผลพิจารณา ทล.": ["ผ่าน", "ไม่ผ่าน"]
    })
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, startrow=1, sheet_name="Worksheet")
        sheet = writer.book["Worksheet"]
        sheet["A1"] = "รหัสเจ้าหน้าที่"
        sheet["B1"] = "คุณสมศักดิ์"

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.write(excel_path, arcname="test.xlsx")
    zip_buffer.seek(0)
    return zip_buffer

@pytest.mark.asyncio
async def test_upload(sample_zip):
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        files = {"file": ("test.zip", sample_zip, "application/zip")}
        response = await client.post("/upload/", files=files)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_history():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.get("/history")
    assert response.status_code == 200
