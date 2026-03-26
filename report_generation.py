import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

def generate_report():

    # ---------------- LOAD DATA ----------------
    conn = sqlite3.connect("database.db")

    query = """
    SELECT date, open, high, low, close, volume, price_diff, daily_return, Trend
    FROM stock_data
    ORDER BY date DESC
    LIMIT 7
    """

    df = pd.read_sql(query, conn)
    conn.close()

    df = df.sort_values("date")

    # Format date for readability
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

    # Round numbers (makes table cleaner)
    df = df.round(2)

    # ---------------- CREATE SIMPLE CHARTS ----------------

    # Chart 1: Closing Price (simple line)
    plt.figure()
    plt.plot(df["date"], df["close"], marker='o')
    plt.title("Closing Price (Last 7 Days)")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("price_chart.png")
    plt.close()

    # Chart 2: Trend count (very simple)
    trend_counts = df["Trend"].value_counts()

    plt.figure()
    plt.bar(trend_counts.index, trend_counts.values)
    plt.title("Trend Distribution")
    plt.tight_layout()
    plt.savefig("trend_chart.png")
    plt.close()

    # ---------------- CREATE PDF ----------------

    doc = SimpleDocTemplate("report.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("Stock Analytics Report", styles["Title"]))
    elements.append(Spacer(1, 10))

    # Log summary
    elements.append(Paragraph("Monitoring Summary:", styles["Heading2"]))
    elements.append(Paragraph("Monitoring/insert completed. 0 new rows added.", styles["Normal"]))
    elements.append(Spacer(1, 10))

    # ---------------- TABLE FIX ----------------
    elements.append(Paragraph("Last 7 Days Data:", styles["Heading2"]))

    table_data = [df.columns.tolist()] + df.values.tolist()

    # Dynamically set column widths to fit page
    page_width = 500  # usable width
    num_cols = len(df.columns)
    col_widths = [page_width / num_cols] * num_cols

    table = Table(table_data, colWidths=col_widths)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 7),  # smaller font
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # ---------------- ADD CHARTS ----------------
    elements.append(Paragraph("Closing Price Trend:", styles["Heading2"]))
    elements.append(Image("price_chart.png", width=400, height=200))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Trend Distribution:", styles["Heading2"]))
    elements.append(Image("trend_chart.png", width=400, height=200))

    # Build PDF
    doc.build(elements)

    print("✅ Fixed PDF report generated: report.pdf")

if __name__ == "__main__":
    generate_report()