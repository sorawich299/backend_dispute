from app.database import get_db

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