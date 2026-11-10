"""Create the Homework 7 PDF from the fixed SPY snapshot run on 6 Nov 2026."""
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
    canvas.drawString(0.6 * inch, 0.35 * inch, "Algory QI - Homework 7")
    canvas.drawRightString(7.9 * inch, 0.35 * inch, f"Page {doc.page}")
    canvas.restoreState()


def make_table(rows, widths, styles):
    cells = [[Paragraph(str(value), styles["HeaderCell"] if row_number == 0 else styles["Cell"])
              for value in row] for row_number, row in enumerate(rows)]
    table = Table(cells, colWidths=widths, hAlign="LEFT", repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173b60")),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#b5c4d0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3f7")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table


def main():
    doc = SimpleDocTemplate("output/pdf/hw07_answers.pdf", pagesize=letter,
                            leftMargin=0.6 * inch, rightMargin=0.6 * inch,
                            topMargin=0.5 * inch, bottomMargin=0.55 * inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
                              fontSize=17, leading=21, alignment=TA_CENTER, spaceAfter=4))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold",
                              fontSize=11, leading=13, textColor=colors.HexColor("#173b60"),
                              spaceBefore=7, spaceAfter=4))
    styles.add(ParagraphStyle(name="Cell", fontName="Helvetica", fontSize=8.2, leading=9.5))
    styles.add(ParagraphStyle(name="HeaderCell", fontName="Helvetica-Bold", fontSize=8.2,
                              leading=9.5, textColor=colors.white))
    styles["BodyText"].fontSize = 9.15
    styles["BodyText"].leading = 12
    story = [
        Paragraph("Homework 7: Machine Learning on a Real Prediction Problem", styles["ReportTitle"]),
        Paragraph("SPY daily-data snapshot run 6 November 2026 | Latest close in sample: 5 November 2026", styles["BodyText"]),
        Paragraph("1. Dataset", styles["Section"]),
        Paragraph("The feature table has <b>3,711 rows and 8 columns</b>. Each row at date t uses only data through the close at t; "
                  "the label is the return from t to t+1. I used returns over 1, 5, 20, and 60 days, 20-day realised volatility, "
                  "price relative to a 50-day average, and volume relative to its 20-day average.", styles["BodyText"]),
        Paragraph("Columns: return_1, return_5, return_20, return_60, realised_vol_20, price_to_ma50, volume_to_avg20, next_day_return.", styles["BodyText"]),
        make_table([
            ["Date", "r1", "r5", "r20", "r60", "vol20", "MA50 rel.", "vol. rel.", "next return"],
            ["2012-02-03", "0.0140", "0.0206", "0.0508", "0.0656", "0.0055", "0.0623", "0.1354", "-0.0007"],
            ["2012-02-06", "-0.0007", "0.0234", "0.0528", "0.0514", "0.0054", "0.0590", "-0.2276", "0.0025"],
            ["2012-02-07", "0.0025", "0.0264", "0.0529", "0.0944", "0.0054", "0.0587", "-0.0404", "0.0030"],
        ], [0.87 * inch] + [0.67 * inch] * 8, styles),
        Paragraph("Manual check: the first row's features end on 3 February 2012; only its label uses the next close.", styles["BodyText"]),
        Paragraph("2. Time split", styles["Section"]),
        make_table([
            ["Set", "Date range", "Rows"],
            ["Training", "2012-02-03 to 2020-12-07", "2,226"],
            ["Validation", "2020-12-08 to 2023-11-17", "742"],
            ["Test", "2023-11-20 to 2026-11-05", "743"],
        ], [1.2 * inch, 3.7 * inch, 1.1 * inch], styles),
        Paragraph("The ranges are consecutive, time ordered, and non-overlapping; no rows were shuffled.", styles["BodyText"]),
        Paragraph("3. Initial model fit", styles["Section"]),
        make_table([
            ["Model", "Training R-squared", "Validation R-squared"],
            ["Linear regression", "+0.0299", "-0.0293"],
            ["Ridge (alpha=1)", "+0.0299", "-0.0293"],
            ["Random forest (unrestricted)", "+0.8438", "-0.0562"],
            ["Gradient boosting (depth=3)", "+0.5797", "-0.1102"],
        ], [3.3 * inch, 1.45 * inch, 1.55 * inch], styles),
        Paragraph("The large train-validation gaps for the tree models are overfitting, not predictive power.", styles["BodyText"]),
        Paragraph("4. Validation-only tuning", styles["Section"]),
        make_table([
            ["Model / hyperparameter", "Chosen value", "Validation R-squared"],
            ["Ridge alpha", "100", "-0.0256"],
            ["Random forest max_depth", "2", "-0.0079"],
            ["Gradient boosting max_depth", "1", "-0.0055"],
        ], [3.2 * inch, 1.35 * inch, 1.75 * inch], styles),
        Image("hw07_validation_tuning.png", width=6.1 * inch, height=1.85 * inch, hAlign="CENTER"),
        PageBreak(),
        Paragraph("5. One held-out test", styles["Section"]),
        Paragraph("The shallow gradient booster had the highest validation score, even though it was still negative. It was selected before evaluating the test set.", styles["BodyText"]),
        make_table([
            ["Test metric", "Result"],
            ["Test R-squared", "+0.0239"],
            ["Correlation: prediction vs. actual next-day return", "+0.1627"],
        ], [4.55 * inch, 1.75 * inch], styles),
        Paragraph("6. Test-set sign strategy", styles["Section"]),
        Paragraph("The rule holds SPY when the prediction is positive and otherwise holds cash. It uses the same close-to-next-close convention as Homework 4.", styles["BodyText"]),
        make_table([
            ["Metric", "Sign strategy", "Buy-and-hold"],
            ["Annualised return", "+18.45%", "+17.84%"],
            ["Maximum drawdown", "-19.00%", "-19.00%"],
            ["Fraction invested", "99.46%", "100.00%"],
        ], [2.5 * inch, 1.85 * inch, 1.95 * inch], styles),
        Paragraph("7. Gradient-boosting feature importances", styles["Section"]),
        make_table([
            ["Feature", "Importance"],
            ["return_1", "0.541396"], ["return_60", "0.225347"], ["price_to_ma50", "0.112016"],
            ["return_5", "0.100778"], ["realised_vol_20", "0.016551"], ["return_20", "0.003912"],
            ["volume_to_avg20", "0.000000"],
        ], [4.55 * inch, 1.75 * inch], styles),
        Paragraph("8. Interpretation", styles["Section"]),
        Paragraph("Near-zero validation R-squared is the expected outcome here, not evidence of a coding bug. Daily SPY returns "
                  "are extremely noisy, the simple price and volume features are public, and many sophisticated investors already test "
                  "the same momentum, moving-average, volatility, and volume signals. Competition should eliminate an obvious, scalable "
                  "next-day forecast; flexible trees can nevertheless fit noise in the training period, which is exactly what their large "
                  "training-validation gaps show. The positive test R-squared is one holdout outcome after a negative validation result, "
                  "so it is not enough evidence to claim an edge.\n\nA near-zero R-squared can still coexist with a profitable trading rule. "
                  "R-squared measures squared-error accuracy for the size of every daily return, whereas a sign rule only needs a small, "
                  "persistent advantage in conditional expected return or direction, potentially concentrated on a subset of days. But this "
                  "particular strategy was invested 99.46% of the time and its small return advantage is consistent with being almost buy-and-hold; "
                  "it does not establish a predictive edge, especially before transaction costs, turnover, and a genuinely prospective test.", styles["BodyText"]),
    ]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    main()
