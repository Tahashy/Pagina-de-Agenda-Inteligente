# utils/report_pdf.py
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
from reportlab.platypus import Image as RLImage
import tempfile
import os
from reportlab.lib.units import mm

def exportar_pdf(nombre_archivo, titulo, df: pd.DataFrame):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(nombre_archivo, pagesize=A4)

    elementos = []

    # Título
    elementos.append(Paragraph(f"<b>{titulo}</b>", styles["Title"]))
    elementos.append(Spacer(1, 20))

    # Convertir df a tabla
    data = [df.columns.tolist()] + df.values.tolist()

    tabla = Table(data)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#003566")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 10),
        ("BOTTOMPADDING", (0,0), (-1,0), 6)
    ]))

    elementos.append(tabla)

    elementos.append(Spacer(1, 30))
    elementos.append(
        Paragraph(
            "<i>Este informe fue generado automáticamente mediante el Sistema SST – "
            "Conforme a los lineamientos del Módulo de Reportes del Laboratorio 13 y la Adenda.</i>",
            styles["Normal"]
        )
    )

    doc.build(elementos)
    return nombre_archivo


def generar_reporte_mensual_pdf(nombre_archivo, resumen: dict, df_inc: pd.DataFrame, df_epp: pd.DataFrame, df_cap: pd.DataFrame, by_area: pd.DataFrame = None):
    """Genera un PDF consolidado mensual con métricas y tablas principales.

    - `resumen` es un dict con claves como 'total_inc', 'total_cap', 'total_epp'.
    - `df_inc`, `df_epp`, `df_cap` son DataFrame (pueden estar vacíos).
    - `by_area` es un DataFrame opcional con conteos por área.
    """
    styles = getSampleStyleSheet()
    left_margin = 25
    right_margin = 25
    top_margin = 25
    bottom_margin = 25
    doc = SimpleDocTemplate(nombre_archivo, pagesize=A4, leftMargin=left_margin, rightMargin=right_margin, topMargin=top_margin, bottomMargin=bottom_margin)
    elementos = []

    # helper: create table with reasonable column widths and left alignment
    def make_table_from_df(df_table, max_rows=100):
        cols = df_table.columns.tolist()
        data = [cols]
        for _, row in df_table.head(max_rows).iterrows():
            data.append([str(row.get(c, "")) for c in cols])

        # compute approximate column widths
        page_width = A4[0] - left_margin - right_margin
        col_count = max(1, len(cols))
        col_width = page_width / col_count
        col_widths = [col_width] * col_count

        tabla = Table(data, colWidths=col_widths, repeatRows=1)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#003566")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("ALIGN", (0,0), (-1,-1), "LEFT"),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ("FONTSIZE", (0,0), (-1, -1), 8),
            ("BOTTOMPADDING", (0,0), (-1, -1), 4),
        ]))
        return tabla

    # Título
    elementos.append(Paragraph("<b>Reporte Mensual SST</b>", styles["Title"]))
    elementos.append(Spacer(1, 6))

    # Resumen de métricas
    elementos.append(Paragraph("<b>Resumen</b>", styles["Heading2"]))
    for k, v in resumen.items():
        elementos.append(Paragraph(f"<b>{k}:</b> {v}", styles["Normal"]))
    elementos.append(Spacer(1, 12))

    # Insertar gráficas si existen imágenes en /tmp (previamente generadas)
    tmpdir = tempfile.gettempdir()
    # look for files named report_chart_*.png in temp dir created by caller
    chart_files = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.startswith("report_chart_") and f.endswith(".png")]
    for cf in sorted(chart_files):
        try:
            elementos.append(RLImage(cf, width=170*mm))
            elementos.append(Spacer(1, 6))
        except (OSError, IOError):
            pass

    elementos.append(Spacer(1, 8))

    # Incidentes (tabla resumida)
    elementos.append(Paragraph("<b>Incidentes (resumen)</b>", styles["Heading3"]))
    if df_inc is None or df_inc.empty:
        elementos.append(Paragraph("No hay incidentes registrados.", styles["Normal"]))
    else:
        elementos.append(make_table_from_df(df_inc, max_rows=100))
    elementos.append(Spacer(1, 12))

    # EPP por vencer (resumido)
    elementos.append(Paragraph("<b>EPP por vencer (resumen)</b>", styles["Heading3"]))
    if df_epp is None or df_epp.empty:
        elementos.append(Paragraph("No hay registros de EPP.", styles["Normal"]))
    else:
        elementos.append(make_table_from_df(df_epp, max_rows=50))
    elementos.append(Spacer(1, 12))

    # Capacitaciones del mes
    elementos.append(Paragraph("<b>Capacitaciones (resumen)</b>", styles["Heading3"]))
    if df_cap is None or df_cap.empty:
        elementos.append(Paragraph("No hay capacitaciones registradas.", styles["Normal"]))
    else:
        elementos.append(make_table_from_df(df_cap, max_rows=50))
    elementos.append(Spacer(1, 12))

    # Incidentes por área
    elementos.append(Paragraph("<b>Incidentes por área</b>", styles["Heading3"]))
    if by_area is None or by_area.empty:
        elementos.append(Paragraph("No hay datos por área.", styles["Normal"]))
    else:
        elementos.append(make_table_from_df(by_area, max_rows=200))

    # build and cleanup temporary chart files
    doc.build(elementos)

    # try to remove temp chart files created earlier
    for cf in chart_files:
        try:
            os.remove(cf)
        except OSError:
            pass

    return nombre_archivo
