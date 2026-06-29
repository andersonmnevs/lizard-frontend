from fastapi import APIRouter
from ..db import get_db_connection
from ..models.op import (
    DashboardResponse,
    DashboardPeriod,
    ClassDistribution,
    RecentOp,
)

router = APIRouter(tags=["ops"])


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
