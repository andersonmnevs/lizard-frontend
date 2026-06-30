import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from ..db import get_db_connection
from ..config import RESULTS_DIR
from ..models.hide import HideDetail

router = APIRouter(prefix="/hides", tags=["hides"])


def _check_image_available(result_path: str, processed_at: str, op: str, hide_num: str, area) -> bool:
    try:
        if not result_path or area is None:
            return False
        dt = datetime.fromisoformat(processed_at.replace(" ", "T"))
        date_str = dt.strftime("%d.%m.%Y")
        time_str = dt.strftime("%H.%M.%S")
        filename = f"{date_str}-{time_str}-{op}-{hide_num}-{area}.jpg"
        full_path = os.path.join(result_path, filename)
        return os.path.isfile(full_path)
    except Exception:
        return False


@router.get("/{hide_id}", response_model=HideDetail)
def get_hide_detail(hide_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                rowid as id,
                GrdHidNum as hide_num,
                GrdOp as op,
                GrdDat as processed_at,
                GrdCla as class_name,
                GrdUsaPer as yield_pct,
                GrdAre as area,
                GrdResPat as result_path
            FROM grading_results
            WHERE rowid = ?
            """,
            (hide_id,),
        )
        row = cursor.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Couro não encontrado")

        image_available = _check_image_available(
            result_path=row["result_path"] or RESULTS_DIR,
            processed_at=row["processed_at"],
            op=row["op"],
            hide_num=row["hide_num"],
            area=row["area"],
        )

        cursor.execute(
            """
            SELECT rowid as id
            FROM grading_results
            WHERE GrdOp = ? AND GrdHidNum < ?
            ORDER BY GrdHidNum DESC
            LIMIT 1
            """,
            (row["op"], row["hide_num"]),
        )
        prev_row = cursor.fetchone()
        prev_hide_id = prev_row["id"] if prev_row else None

        cursor.execute(
            """
            SELECT rowid as id
            FROM grading_results
            WHERE GrdOp = ? AND GrdHidNum > ?
            ORDER BY GrdHidNum ASC
            LIMIT 1
            """,
            (row["op"], row["hide_num"]),
        )
        next_row = cursor.fetchone()
        next_hide_id = next_row["id"] if next_row else None

        return HideDetail(
            id=row["id"],
            hide_num=row["hide_num"],
            op=row["op"],
            processed_at=row["processed_at"],
            class_name=row["class_name"],
            yield_pct=row["yield_pct"],
            area=row["area"],
            image_available=image_available,
            prev_hide_id=prev_hide_id,
            next_hide_id=next_hide_id,
        )
    finally:
        conn.close()
