from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Image,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


def generate_pdf(last7_df, summary):
    doc = SimpleDocTemplate("reports/stock_report.pdf", pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Stock Market Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Summary", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    for key, value in summary.items():
        elements.append(Paragraph(f"{key}: {value}", styles["Normal"]))

    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Last 7 Days Data", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    data = [list(last7_df.columns)] + last7_df.values.tolist()
    table = Table(data)

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 20))

    charts = [
        ("Price Trend", "reports/price_trend.png"),
        ("Volume", "reports/volume.png"),
        ("Returns Distribution", "reports/returns.png"),
        ("Trend Distribution", "reports/trend.png"),
    ]

    for title, path in charts:
        try:
            elements.append(Paragraph(title, styles["Heading2"]))
            elements.append(Spacer(1, 10))
            elements.append(Image(path, width=400, height=250))
            elements.append(Spacer(1, 20))
        except:
            elements.append(Paragraph(f"{title} image not found.", styles["Normal"]))

    doc.build(elements)
    print("PDF report generated: reports/stock_report.pdf")
