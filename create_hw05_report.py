"""Create the Homework 5 PDF from the live SPY snapshot captured 25 Oct 2026."""
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
    canvas.drawString(0.6 * inch, 0.35 * inch, "Algory QI - Homework 5")
    canvas.drawRightString(7.9 * inch, 0.35 * inch, f"Page {doc.page}")
    canvas.restoreState()


def make_table(rows, widths, styles):
    cells = [[Paragraph(str(value), styles["HeaderCell"] if row_index == 0 else styles["Cell"])
              for value in row] for row_index, row in enumerate(rows)]
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
    doc = SimpleDocTemplate("output/pdf/hw05_answers.pdf", pagesize=letter,
                            leftMargin=0.6 * inch, rightMargin=0.6 * inch,
                            topMargin=0.5 * inch, bottomMargin=0.55 * inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
                              fontSize=17, leading=21, alignment=TA_CENTER, spaceAfter=4))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold",
                              fontSize=11, leading=13, textColor=colors.HexColor("#173b60"),
                              spaceBefore=7, spaceAfter=4))
    styles.add(ParagraphStyle(name="Cell", fontName="Helvetica", fontSize=8.4, leading=9.5))
    styles.add(ParagraphStyle(name="HeaderCell", fontName="Helvetica-Bold", fontSize=8.4,
                              leading=9.5, textColor=colors.white))
    styles["BodyText"].fontSize = 9.2
    styles["BodyText"].leading = 12

    short_rows = [
        ["Strike", "Mid", "Intrinsic", "Extrinsic"],
        ["755", "17.95", "4.97", "12.98"], ["756", "17.26", "3.97", "13.29"],
        ["757", "16.57", "2.97", "13.60"], ["758", "15.90", "1.97", "13.93"],
        ["759", "15.24", "0.97", "14.27"], ["760", "14.59", "0.00", "14.59"],
        ["761", "13.96", "0.00", "13.96"], ["762", "13.34", "0.00", "13.34"],
        ["763", "12.72", "0.00", "12.72"], ["764", "12.13", "0.00", "12.13"],
    ]
    long_rows = [
        ["Strike", "Mid", "Intrinsic", "Extrinsic"],
        ["735", "69.43", "24.97", "44.46"], ["740", "65.78", "19.97", "45.81"],
        ["745", "62.20", "14.97", "47.23"], ["750", "58.77", "9.97", "48.80"],
        ["755", "55.06", "4.97", "50.10"], ["760", "51.75", "0.00", "51.75"],
        ["765", "48.80", "0.00", "48.80"], ["770", "45.55", "0.00", "45.55"],
        ["775", "42.41", "0.00", "42.41"], ["780", "39.41", "0.00", "39.41"],
    ]
    story = [
        Paragraph("Homework 5: Reading a Real Option Chain", styles["ReportTitle"]),
        Paragraph("Live-chain snapshot captured 25 October 2026 | SPY latest close: 23 October 2026", styles["BodyText"]),
        Paragraph("1. Payoffs", styles["Section"]),
        make_table([
            ["Position", "Spot $80", "Spot $100", "Spot $120"],
            ["Long call", "-$6.00", "-$6.00", "+$14.00"],
            ["Long put", "+$14.00", "-$6.00", "-$6.00"],
            ["Short call", "+$6.00", "+$6.00", "-$14.00"],
            ["Short put", "-$14.00", "+$6.00", "+$6.00"],
        ], [1.8 * inch, 1.45 * inch, 1.45 * inch, 1.45 * inch], styles),
        Paragraph("All figures are profit per share at expiry for strike $100 and premium $6. Long and short positions are exact mirrors.", styles["BodyText"]),
        Paragraph("2. Payoff diagrams", styles["Section"]),
        Image("hw05_payoffs.png", width=6.3 * inch, height=4.7 * inch, hAlign="CENTER"),
        Paragraph("The dashed vertical line is the strike; the horizontal line is zero profit.", styles["BodyText"]),
        PageBreak(),
        Paragraph("3-6. Live SPY call chain", styles["Section"]),
        Paragraph("I selected SPY for liquidity. The latest underlying close was <b>$759.97</b>. The near expiry was "
                  "<b>20 November 2026</b> (223 calls, 201 puts); the longer expiry was <b>17 June 2027</b> "
                  "(217 calls, 178 puts). Rows with a zero bid were dropped. Mid = (bid + ask) / 2; "
                  "intrinsic = max(spot - strike, 0); extrinsic = mid - intrinsic.", styles["BodyText"]),
        Spacer(1, 5),
        Table([
            [Paragraph("<b>20 Nov 2026: 10 strikes nearest spot</b>", styles["HeaderCell"]),
             Paragraph("<b>17 Jun 2027: 10 strikes nearest spot</b>", styles["HeaderCell"])]
        ], colWidths=[3.15 * inch, 3.15 * inch], style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#173b60")),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)
        ])),
        Table([[make_table(short_rows, [0.79 * inch] * 4, styles), make_table(long_rows, [0.79 * inch] * 4, styles)]],
              colWidths=[3.15 * inch, 3.15 * inch], style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")])),
        Paragraph("The largest short-expiry extrinsic value was <b>$14.59 at $760</b>; the largest long-expiry "
                  "extrinsic was <b>$51.75 at $760</b>. Both are essentially at the $759.97 spot.", styles["BodyText"]),
        Spacer(1, 4),
        Image("hw05_extrinsic_curves.png", width=6.3 * inch, height=3.55 * inch, hAlign="CENTER"),
        Paragraph("7. Interpretation", styles["Section"]),
        Paragraph("Extrinsic value is largest near the current spot price. Those at-the-money calls have little or no "
                  "exercise value today, but they have the most meaningful chance of ending on either side of the strike by expiry. "
                  "Far in-the-money calls are already mostly intrinsic value, while far out-of-the-money calls have a smaller chance "
                  "of becoming valuable, so both tend to carry less time value. In this snapshot, the peaks occur at the $760 strike, "
                  "almost exactly at SPY spot.", styles["BodyText"]),
        Paragraph("The June curve is much higher because it gives the underlying almost seven extra months to move across the strike. "
                  "Buying that time means paying for more possible price paths: a currently out-of-the-money call has more opportunity "
                  "to cross into the money, and an at-the-money call has more opportunity to make a large move. Among 97 common quoted "
                  "strikes, the long-dated call had higher extrinsic value at 96. The one deep-in-the-money $395 exception displayed "
                  "negative extrinsic value, an economically implausible artifact of a stale/wide quote rather than a violation of time value.", styles["BodyText"]),
    ]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    main()
