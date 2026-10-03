"""Create the Homework 3 PDF submission from the results in hw03_starter.py."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak


OUTPUT = "output/pdf/hw03_answers.pdf"


def footer(canvas, document):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(0.65 * inch, 0.40 * inch, "Algory QI - Homework 3")
    canvas.drawRightString(7.85 * inch, 0.40 * inch, f"Page {document.page}")
    canvas.restoreState()


def styled_table(rows, widths):
    table = Table(rows, colWidths=widths, hAlign="LEFT", repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12355b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#9aa8b6")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#edf3f8")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


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
    story = [
        Paragraph("Homework 3: Probability and Testing Independence", styles["ReportTitle"]),
        Paragraph("Algory QI Education | Data downloaded 3 October 2026", styles["BodyText"]),
        Spacer(1, 8),
        Paragraph("1. Two-dice simulation", styles["Section"]),
        Paragraph(
            "I used NumPy's random generator with fixed seed <b>42</b> and ran 100,000 trials. "
            "The estimate of <b>P(4-sided | rolled a 1)</b> was <b>0.6050</b>, compared with the exact answer "
            "<b>0.6000</b>, for a difference of <b>+0.0050</b>.", styles["BodyText"]
        ),
        Paragraph("2. Three-coin payout", styles["Section"]),
        Paragraph(
            "With 100,000 trials and seed 42, the simulated expected payout was <b>1.5013</b>. "
            "The exact expected payout is <b>1.5000</b>.", styles["BodyText"]
        ),
        Paragraph("3. Simulation convergence", styles["Section"]),
        styled_table([
            ["Trials", "Estimated payout", "Exact payout"],
            ["100", "1.5800", "1.5000"],
            ["1,000", "1.4860", "1.5000"],
            ["10,000", "1.4946", "1.5000"],
            ["100,000", "1.5013", "1.5000"],
        ], [1.35 * inch, 1.65 * inch, 1.45 * inch]),
        Spacer(1, 8),
        Image("hw03_coin_convergence.png", width=5.6 * inch, height=3.6 * inch, hAlign="CENTER"),
        Paragraph(
            "The estimate becomes much more stable as trials increase. This is the practical reason simulation and backtest results need enough observations before they are trusted.",
            styles["BodyText"]
        ),
        PageBreak(),
        Paragraph("4-6. Are daily SPY returns independent?", styles["Section"]),
        Paragraph(
            "I downloaded 10 years of unadjusted daily SPY closes (3 October 2016 through 2 October 2026), yielding "
            "<b>2,514 trading days</b> and 2,513 daily returns. The mean daily return was <b>0.0571%</b>.",
            styles["BodyText"]
        ),
        Spacer(1, 7),
        styled_table([
            ["Quantity", "Estimate", "Count supporting estimate"],
            ["P(tomorrow is down)", "0.4481", "1,126 down days / 2,513 returns"],
            ["P(tomorrow down | today down)", "0.4414", "1,126 qualifying down days"],
            ["P(tomorrow down | today down more than 2%)", "0.4023", "87 qualifying big-drop days"],
        ], [2.75 * inch, 1.0 * inch, 2.35 * inch]),
        Paragraph("7. Expected present value", styles["Section"]),
        Paragraph(
            "<b>expected_present_value([10, 10, 10], 0.10, 0.5) = 15.10.</b> "
            "Year 1 is certain, Year 2 is weighted by 0.5, and Year 3 by 0.25 before each cash flow is discounted.",
            styles["BodyText"]
        ),
        Paragraph("8. Interpretation", styles["Section"]),
        Paragraph(
            "These data do not provide strong evidence of a useful one-day dependence in the direction tested: the unconditional probability of a down day is 44.81%, while the probability after a down day is 44.14%. "
            "After a drop greater than 2%, the estimate is lower at 40.23%, but it is based on only 87 days, so that difference is much less precise. "
            "Thus, independence is a reasonable rough approximation for this simple next-day test, but it is not proven by it; returns can still have changing volatility, tail risk, or patterns at other horizons. "
            "A strategy that assumes independent daily returns should therefore test its signal out of sample and stress its results rather than treating small conditional-probability differences as a reliable trading edge.",
            styles["BodyText"]
        ),
    ]
    document.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    main()
