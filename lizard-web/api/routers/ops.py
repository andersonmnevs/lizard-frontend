import math
from typing import Optional
from fastapi import APIRouter, Query
from ..db import get_db_connection
from ..models.op import (
    DashboardResponse,
    DashboardPeriod,
    ClassDistribution,
    RecentOp,
    OpSummary,
    OpListResponse,
)

router = APIRouter(tags=["ops"])


@router.get("/ops", response_model=OpListResponse)
def list_ops(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    class_filter: Optional[str] = Query(default=None, alias="class"),
    search: Optional[str] = Query(default=None),
):
    conditions = ["1=1"]
    params: list = []

    if date_from:
        conditions.append("date(GrdDat) >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date(GrdDat) <= ?")
        params.append(date_to)
    if class_filter:
        conditions.append("UPPER(GrdCla) = UPPER(?)")
        params.append(class_filter)
    if search:
        conditions.append("GrdOp LIKE ?")
        params.append(f"%{search}%")

    where_clause = " AND ".join(conditions)

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT COUNT(DISTINCT GrdOp) as total FROM grading_results WHERE {where_clause}",
            params,
        )
        total = cursor.fetchone()["total"] or 0

        offset = (page - 1) * limit
        pages = math.ceil(total / limit) if total > 0 else 0

        cursor.execute(
            f"""
            SELECT GrdOp as op,
                   MAX(GrdDat) as last_updated,
                   COUNT(*) as total_hides,
                   ROUND(AVG(GrdUsaPer), 2) as avg_yield,
                   (
                       SELECT GrdCla FROM grading_results g2
                       WHERE g2.GrdOp = g1.GrdOp
                       GROUP BY GrdCla
                       ORDER BY COUNT(*) DESC
                       LIMIT 1
                   ) as predominant_class
            FROM grading_results g1
            WHERE {where_clause}
            GROUP BY GrdOp
            ORDER BY last_updated DESC
            LIMIT ? OFFSET ?
            """,
            params + [limit, offset],
        )
        items = [
            OpSummary(
                op=r["op"],
                last_updated=r["last_updated"],
                total_hides=r["total_hides"],
                avg_yield=r["avg_yield"],
                predominant_class=r["predominant_class"],
            )
            for r in cursor.fetchall()
        ]

        return OpListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )
    finally:
        conn.close()


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) as total, AVG(GrdUsaPer) as avg_yield
            FROM grading_results
            WHERE date(GrdDat) = date('now', 'localtime')
        """)
        row = cursor.fetchone()
        today = DashboardPeriod(
            total_hides=row["total"] or 0,
            avg_yield=round(row["avg_yield"], 2) if row["avg_yield"] is not None else None,
        )

        cursor.execute("""
            SELECT COUNT(*) as total, AVG(GrdUsaPer) as avg_yield
            FROM grading_results
            WHERE date(GrdDat) >= date('now', '-6 days', 'localtime')
        """)
        row = cursor.fetchone()
        week = DashboardPeriod(
            total_hides=row["total"] or 0,
            avg_yield=round(row["avg_yield"], 2) if row["avg_yield"] is not None else None,
        )

        cursor.execute("""
            SELECT GrdCla as class_name,
                   COUNT(*) as count,
                   ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as pct
            FROM grading_results
            WHERE date(GrdDat) = date('now', 'localtime')
            GROUP BY GrdCla
            ORDER BY count DESC
        """)
        today_class_distribution = [
            ClassDistribution(class_name=r["class_name"], count=r["count"], pct=r["pct"])
            for r in cursor.fetchall()
        ]

        cursor.execute("""
            SELECT GrdOp as op,
                   date(MAX(GrdDat)) as date,
                   COUNT(*) as total_hides
            FROM grading_results
            GROUP BY GrdOp
            ORDER BY MAX(GrdDat) DESC
            LIMIT 5
        """)
        recent_ops = [
            RecentOp(op=r["op"], date=r["date"], total_hides=r["total_hides"])
            for r in cursor.fetchall()
        ]

        return DashboardResponse(
            today=today,
            week=week,
            today_class_distribution=today_class_distribution,
            recent_ops=recent_ops,
        )
    finally:
        conn.close()
