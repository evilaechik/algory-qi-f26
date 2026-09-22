"""Create the PDF submission from the results printed by hw02_starter.py."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)


OUTPUT = "output/pdf/hw02_answers.pdf"


def footer(canvas, document):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(0.65 * inch, 0.40 * inch, "Algory QI - Homework 2")
    canvas.drawRightString(7.85 * inch, 0.40 * inch, f"Page {document.page}")
    canvas.restoreState()


def main():
    document = SimpleDocTemplate(
        OUTPUT, pagesize=letter, rightMargin=0.65 * inch, leftMargin=0.65 * inch,
        topMargin=0.60 * inch, bottomMargin=0.62 * inch
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=19, leading=23, alignment=TA_CENTER, spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=12, leading=15, textColor=colors.HexColor("#12355b"),
        spaceBefore=11, spaceAfter=5
    ))
    styles["BodyText"].fontSize = 10
    styles["BodyText"].leading = 14
    story = []

    story += [
        Paragraph("Homework 2: Rates, Ratios, and Discounting", styles["ReportTitle"]),
        Paragraph("Algory QI Education | Data downloaded 22 September 2026", styles["BodyText"]),
        Spacer(1, 8),
        Paragraph("1. Present value", styles["Section"]),
        Paragraph(
            "<b>present_value([10, 15, 20], 0.10) = 36.51.</b> "
            "Each cash flow is discounted by (1 + rate) raised to its year number.",
            styles["BodyText"]
        ),
        Paragraph("2. Bond priced at its coupon rate", styles["Section"]),
        Paragraph(
            "<b>bond_price(1000, 0.04, 10, 0.04) = $1,000.00.</b> "
            "The final cash flow includes both the $40 coupon and the $1,000 face value.",
            styles["BodyText"]
        ),
        Paragraph("3. Bond price and market rate", styles["Section"]),
    ]
    bond_table = Table([
        ["Market rate", "Bond price"],
        ["2.00%", "$1,179.65"],
        ["4.00%", "$1,000.00"],
        ["4.96%", "$925.73"],
    ], colWidths=[1.7 * inch, 1.7 * inch], hAlign="LEFT")
    bond_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12355b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9aa8b6")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#edf3f8")]),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [
        bond_table, Spacer(1, 8),
        Image("hw02_bond_price_curve.png", width=5.6 * inch, height=3.6 * inch, hAlign="CENTER"),
        Paragraph(
            "The curve slopes downward and is convex: a given fall in rates increases the price more than an equal rise in rates decreases it.",
            styles["BodyText"]
        ),
        PageBreak(),
        Paragraph("4-6. Beta from five years of daily closing prices", styles["Section"]),
        Paragraph(
            "Selected sectors: AAPL (technology), JPM (financials), and XOM (energy). "
            "Each series, including SPY, contains 1,254 trading days. Annualised return uses compounded daily growth; "
            "volatility is the standard deviation of daily returns multiplied by the square root of 252; beta is calculated from daily returns against SPY.",
            styles["BodyText"]
        ), Spacer(1, 8),
    ]
    data_table = Table([
        ["Ticker", "Annualised return", "Annualised volatility", "Beta vs SPY"],
        ["AAPL", "18.38%", "28.05%", "1.16"],
        ["JPM", "16.20%", "24.45%", "0.87"],
        ["XOM", "22.83%", "26.68%", "0.39"],
    ], colWidths=[0.8 * inch, 1.6 * inch, 1.75 * inch, 1.15 * inch], repeatRows=1)
    data_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12355b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9aa8b6")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#edf3f8")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [
        data_table,
        Paragraph("Ranked by beta: <b>AAPL &gt; JPM &gt; XOM</b>.", styles["BodyText"]),
        Paragraph("Ranked by volatility: <b>AAPL &gt; XOM &gt; JPM</b>.", styles["BodyText"]),
        Paragraph("7. Interpretation", styles["Section"]),
        Paragraph(
            "The rankings do not fully agree: JPM ranks above XOM on beta, while XOM ranks above JPM on volatility. "
            "XOM is the clearest example: its annualised volatility is 26.68%, yet its beta is only 0.39. "
            "That combination means much of XOM's movement over this period was company- or energy-sector-specific rather than movement shared with the broad equity market. "
            "In other words, XOM was relatively jumpy, but its jumps were not especially sensitive to SPY, so diversification can reduce more of its risk than it can for a high-beta stock.",
            styles["BodyText"]
        ),
    ]
    document.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    main()
