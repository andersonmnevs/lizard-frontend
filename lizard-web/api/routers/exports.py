import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from weasyprint import HTML
from ..db import get_db_connection

router = APIRouter(tags=["exports"])


def _build_pdf_html(op_id: str, summary, classes, hides) -> str:
    total = summary["total_hides"]
    class_rows = "".join(
        f"<tr><td>{c['class_name']}</td><td>{c['count']}</td>"
        f"<td>{round(c['count'] / total * 100, 1)}%</td></tr>"
        for c in classes
    )
    hide_rows = "".join(
        f"<tr><td>{h['hide_num']}</td><td>{h['processed_at']}</td>"
        f"<td>{h['class_name']}</td>"
        f"<td>{h['yield_pct'] if h['yield_pct'] is not None else '—'}%</td>"
        f"<td>{h['area'] if h['area'] is not None else '—'}</td></tr>"
        for h in hides
    )
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: Arial, sans-serif; font-size: 12px; margin: 2cm; color: #222; }}
    h1 {{ font-size: 18px; margin-bottom: 0.2em; }}
    h2 {{ font-size: 14px; margin-top: 1.5em; margin-bottom: 0.4em; color: #444; }}
    p {{ margin: 0.2em 0; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 0.5em; }}
    th, td {{ border: 1px solid #ccc; padding: 4px 8px; text-align: left; }}
    th {{ background: #f0f0f0; font-weight: bold; }}
    .header {{ margin-bottom: 1.2em; border-bottom: 1px solid #ccc; padding-bottom: 0.8em; }}
  </style>
</head>
<body>
  <div class="header">
    <h1>Relatório da OP {op_id}</h1>
    <p>Período: {summary['date_from']} a {summary['date_to']}</p>
    <p>Emitido por: Lizard Web — Viposa SA</p>
  </div>

  <h2>Resumo</h2>
  <table>
    <tr><th>Total de Couros</th><td>{summary['total_hides']}</td></tr>
    <tr><th>Aproveitamento Médio</th><td>{summary['avg_yield'] if summary['avg_yield'] is not None else '—'}%</td></tr>
    <tr><th>Área Média</th><td>{summary['avg_area'] if summary['avg_area'] is not None else '—'} m²</td></tr>
  </table>

  <h2>Distribuição de Classes</h2>
  <table>
    <tr><th>Classe</th><th>Couros</th><th>%</th></tr>
    {class_rows}
  </table>

  <h2>Couros</h2>
  <table>
    <tr><th>Nº Couro</th><th>Data/Hora</th><th>Classe</th><th>Aproveit.</th><th>Área (m²)</th></tr>
    {hide_rows}
  </table>
</body>
</html>"""


@router.get("/ops/{op_id}/export/pdf")
def export_op_pdf(op_id: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) as cnt FROM grading_results WHERE GrdOp = ?",
            (op_id,),
        )
        if cursor.fetchone()["cnt"] == 0:
            raise HTTPException(status_code=404, detail="OP não encontrada")

        cursor.execute(
            """
            SELECT
                COUNT(*) as total_hides,
                ROUND(AVG(GrdAre), 2) as avg_area,
                ROUND(AVG(GrdUsaPer), 2) as avg_yield,
                MIN(date(GrdDat)) as date_from,
                MAX(date(GrdDat)) as date_to
            FROM grading_results
            WHERE GrdOp = ?
            """,
            (op_id,),
        )
        summary = cursor.fetchone()

        cursor.execute(
            """
            SELECT GrdCla as class_name, COUNT(*) as count
            FROM grading_results
            WHERE GrdOp = ?
            GROUP BY GrdCla
            ORDER BY count DESC
            """,
            (op_id,),
        )
        classes = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                GrdHidNum as hide_num,
                GrdDat as processed_at,
                GrdCla as class_name,
                GrdUsaPer as yield_pct,
                GrdAre as area
            FROM grading_results
            WHERE GrdOp = ?
            ORDER BY GrdHidNum ASC
            """,
            (op_id,),
        )
        hides = cursor.fetchall()
    finally:
        conn.close()

    html_content = _build_pdf_html(op_id, summary, classes, hides)
    pdf_bytes = HTML(string=html_content).write_pdf()

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="op-{op_id}.pdf"'},
    )
