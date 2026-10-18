"""Create the PDF report for the locked Homework 4 snapshot."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(0.6 * inch, 0.35 * inch, "Algory QI - Homework 4")
    canvas.drawRightString(7.9 * inch, 0.35 * inch, f"Page {doc.page}")
    canvas.restoreState()


def make_table(rows, widths, styles):
    cells = [[Paragraph(str(value), styles["HeaderCell"] if row_number == 0 else styles["Cell"])
              for value in row] for row_number, row in enumerate(rows)]
    table = Table(cells, colWidths=widths, hAlign="LEFT", repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173b60")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#b5c4d0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3f7")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def main():
    doc = SimpleDocTemplate("output/pdf/hw04_answers.pdf", pagesize=letter,
                            leftMargin=0.6 * inch, rightMargin=0.6 * inch,
                            topMargin=0.5 * inch, bottomMargin=0.55 * inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
                              fontSize=17, leading=21, alignment=TA_CENTER, spaceAfter=5))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold",
                              fontSize=11, leading=13, textColor=colors.HexColor("#173b60"),
                              spaceBefore=7, spaceAfter=4))
    styles.add(ParagraphStyle(name="Cell", fontName="Helvetica", fontSize=8.5, leading=10))
    styles.add(ParagraphStyle(name="HeaderCell", fontName="Helvetica-Bold", fontSize=8.5,
                              leading=10, textColor=colors.white))
    styles["BodyText"].fontSize = 9
    styles["BodyText"].leading = 12
    story = [
        Paragraph("Homework 4: Build and Honestly Test a Strategy", styles["ReportTitle"]),
        Paragraph("Data snapshot: 18 October 2026 | Index: ^SP500TR (total return)", styles["BodyText"]),
        Paragraph("1. Data and split", styles["Section"]),
        Paragraph("The requested 10 September 2011 was a Saturday, so the split uses the preceding trading close, "
                  "9 September. Training has <b>5,469 closes</b> with mean price <b>1,358.78</b>. "
                  "The test input has <b>3,857 closes</b> including the 60 training closes used only for warmup; "
                  "its mean is <b>6,875.45</b>. Its first earned return is 9 to 12 September 2011.", styles["BodyText"]),
        Paragraph("2-5. Backtester and controls (training)", styles["Section"]),
        Paragraph("The 60-close window ends at today's close; the decision applies only to the return to the next close. "
                  "The index and strategy both start at 1 over the same traded dates. The random rule uses seed 0.", styles["BodyText"]),
        make_table([
            ["Rule", "Total return", "Annualised return"],
            ["Always hold / index", "+432.27%", "+8.10%"],
            ["Always cash", "+0.00%", "+0.00%"],
            ["Random hold, 70%", "+361.36%", "+7.38%"],
            ["Class: hold unless 5-day return positive", "+206.70%", "+5.36%"],
        ], [3.5 * inch, 1.25 * inch, 1.55 * inch], styles),
        Spacer(1, 4),
        Image("hw04_train_control.png", width=5.2 * inch, height=2.6 * inch, hAlign="CENTER"),
        Paragraph("The always-hold and index curves overlap exactly; always cash returns exactly zero.", styles["BodyText"]),
        Paragraph("6-7. All variants tried and final rule", styles["Section"]),
        make_table([
            ["Training rule", "Annualised"],
            ["Close above 60-day moving average", "+5.72%"],
            ["Close above 30-day moving average", "+3.84%"],
            ["Positive 30-day return", "+3.28%"],
            ["Nonpositive 15-day return", "+3.43%"],
            ["Above 60-day average AND nonpositive 5-day return", "+2.52%"],
        ], [4.9 * inch, 1.4 * inch], styles),
        Paragraph("I selected the first rule on training data: hold when the latest close is above its 60-day average; "
                  "otherwise hold cash. A trend filter could work beyond this sample if sustained declines tend to persist, "
                  "though whipsaws can make the rule miss recoveries and generate trading costs.", styles["BodyText"]),
        PageBreak(),
        Paragraph("8. One holdout evaluation", styles["Section"]),
        Paragraph("The rule was locked before evaluating the holdout and was not changed afterward. "
                  "The 60 warmup closes generate no test returns; results cover 3,797 subsequent trading returns.", styles["BodyText"]),
        make_table([
            ["Holdout metric", "60-day strategy", "Buy-and-hold index"],
            ["Total return", "+189.81%", "+773.51%"],
            ["Annualised return", "+7.32%", "+15.47%"],
            ["Maximum drawdown", "-21.40%", "-33.79%"],
            ["Fraction invested", "76.32%", "100.00%"],
        ], [2.5 * inch, 1.8 * inch, 2.0 * inch], styles),
        Spacer(1, 4),
        Image("hw04_test_strategy.png", width=6.0 * inch, height=3.0 * inch, hAlign="CENTER"),
        Paragraph("9. Latest signal", styles["Section"]),
        Paragraph("Using the latest 60 closes through <b>16 October 2026</b>, the rule says <b>CASH</b>.", styles["BodyText"]),
        Paragraph("10. What the test means", styles["Section"]),
        Paragraph("The strategy earned 7.32% annualised in the holdout versus 5.72% in training, but lost plainly "
                  "to buy-and-hold's 15.47% in the holdout; its lower drawdown is a real historical tradeoff, not evidence "
                  "of superior overall performance. I am not surprised that a trend rule missed part of a strong bull market, "
                  "although the size of the return gap is striking. I would not invest my own money based on this result: five "
                  "rules were tried, and the public historical holdout is only one market path, not a genuinely new prospective sample. "
                  "To trust it, I would want a pre-registered rule tested prospectively and across independent markets and regimes, "
                  "with realistic costs, taxes, cash yield, and executable timing. The backtest assumes a trade at the same close "
                  "used to compute the signal, which is optimistic, and it ignores slippage and trading costs; a total-return index "
                  "also cannot itself be traded. The lesson is that a smoother ride can come with substantial opportunity cost, "
                  "and a favorable training comparison among several variants is not proof of a durable edge.", styles["BodyText"]),
    ]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    main()
