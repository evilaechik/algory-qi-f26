"""Create the Homework 6 PDF from the live SPY snapshot captured 1 Nov 2026."""
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
    canvas.drawString(0.6 * inch, 0.35 * inch, "Algory QI - Homework 6")
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
    doc = SimpleDocTemplate("output/pdf/hw06_answers.pdf", pagesize=letter,
                            leftMargin=0.6 * inch, rightMargin=0.6 * inch,
                            topMargin=0.5 * inch, bottomMargin=0.55 * inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
                              fontSize=17, leading=21, alignment=TA_CENTER, spaceAfter=4))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold",
                              fontSize=11, leading=13, textColor=colors.HexColor("#173b60"),
                              spaceBefore=7, spaceAfter=4))
    styles.add(ParagraphStyle(name="Cell", fontName="Helvetica", fontSize=8.5, leading=9.8))
    styles.add(ParagraphStyle(name="HeaderCell", fontName="Helvetica-Bold", fontSize=8.5,
                              leading=9.8, textColor=colors.white))
    styles["BodyText"].fontSize = 9.2
    styles["BodyText"].leading = 12
    story = [
        Paragraph("Homework 6: Greeks, Combinations, and Implied Volatility", styles["ReportTitle"]),
        Paragraph("Live-chain snapshot captured 1 November 2026 | SPY latest close: 30 October 2026", styles["BodyText"]),
        Paragraph("1. Combination payoffs", styles["Section"]),
        Paragraph("All entries below are <b>per share</b>; one listed option contract controls 100 shares. "
                  "'Unlimited' means the payoff rises without a finite upper bound as spot rises.", styles["BodyText"]),
        make_table([
            ["Position", "Maximum profit", "Maximum loss", "Break-even price(s)"],
            ["Covered call: stock 100; short 105 call for 4", "$9.00", "-$96.00", "$96.00"],
            ["Protective put: stock 100; long 95 put for 3", "Unlimited", "-$8.00", "$103.00"],
            ["Long straddle: 100 call and put, 6 each", "Unlimited", "-$12.00", "$88.00; $112.00"],
            ["Bull call: long 95 for 8; short 105 for 4", "$6.00", "-$4.00", "$99.00"],
        ], [2.75 * inch, 1.15 * inch, 1.1 * inch, 1.3 * inch], styles),
        Spacer(1, 4),
        Image("hw06_combinations.png", width=6.15 * inch, height=4.6 * inch, hAlign="CENTER"),
        Paragraph("2. Calendar spread", styles["Section"]),
        Paragraph("A calendar spread cannot be described by one expiry payoff diagram because its two legs expire on different dates. "
                  "After the one-week short call expires, the three-month long call still has both time value and an uncertain future payoff. "
                  "The position is generally betting that near-term realised movement will be modest relative to the time value sold, while the longer-dated option retains value. "
                  "If the underlying does little for a week, the short leg normally decays faster than the long leg, but changes in implied volatility can still alter the result.", styles["BodyText"]),
        PageBreak(),
        Paragraph("3-4. Black-Scholes and inversion check", styles["Section"]),
        make_table([
            ["Input / check", "Result"],
            ["Black-Scholes call: S=100, K=100, T=1, r=4%, sigma=25%", "$11.84"],
            ["Matching Black-Scholes put", "$7.92"],
            ["Put-call parity: C - P", "$3.92 = 100 - 100e<super>-0.04</super>"],
            ["IV recovered by bisection from the call price", "0.2500"],
        ], [4.55 * inch, 1.75 * inch], styles),
        Paragraph("The bisection routine searches volatility from 0.001 to 5.0. Since a Black-Scholes option price rises monotonically with volatility, it converges to the volatility whose model price equals the observed mid price.", styles["BodyText"]),
        Paragraph("5-6. Live SPY implied and realised volatility", styles["Section"]),
        Paragraph("I used the 27 November 2026 SPY expiry, 28 calendar days after the 30 October close. "
                  "After excluding zero-bid/zero-ask quotes and option prices that violate Black-Scholes bounds, 120 calls remained. "
                  "The nearest strike was <b>$756</b> versus spot <b>$755.72</b>.", styles["BodyText"]),
        make_table([
            ["Measure", "Value"],
            ["Nearest-at-the-money call implied volatility", "16.40%"],
            ["VIX latest close", "19.42"],
            ["SPY realised volatility, prior 30 trading returns", "11.31%"],
        ], [4.55 * inch, 1.75 * inch], styles),
        Image("hw06_iv_smile.png", width=6.25 * inch, height=3.53 * inch, hAlign="CENTER"),
        Paragraph("The curve is called an <b>implied-volatility smile</b>, with a strong downside skew when read in terms of out-of-the-money puts (deep in-the-money calls mirror those puts). "
                  "A single normal distribution with constant volatility would produce a flat line, so the shape implies the market assigns extra probability to large and asymmetric moves, especially downside moves.", styles["BodyText"]),
        Paragraph("7. Why the IV-realised gap exists", styles["Section"]),
        Paragraph("Here, at-the-money implied volatility (16.40%) was higher than the trailing realised volatility (11.31%). "
                  "An option seller can reasonably demand that gap because the seller takes uncertain convex exposure and must bear jump risk, volatility spikes, hedging costs, and the possibility that future realised volatility is much higher than the recent 30-day sample. "
                  "Selling options every week can therefore make money most weeks as premiums decay, but it is a short-volatility trade: occasional large moves can generate losses far larger than many small premium collections, and naked calls in particular have theoretically unlimited upside loss. "
                  "The premium is compensation for carrying that tail risk, not a free yield.", styles["BodyText"]),
    ]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    main()
