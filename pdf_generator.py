from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from io import BytesIO


def generate_pdf(itinerary):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    # Title Style (Centered, Bold, Size 22)
    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=22,
        alignment=TA_CENTER,
        spaceAfter=20
    )

    # Heading Style (Day headings)
    heading_style = ParagraphStyle(
        name="HeadingStyle",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=22,
        spaceAfter=10
    )

    # Normal Content Style
    normal_style = ParagraphStyle(
        name="NormalStyle",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=14,
        spaceAfter=6
    )

    # ---------- TITLE ----------
    destination = itinerary["trip_summary"]["destination"]
    title = f"{destination} Trip Daywise Plan"
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.3 * inch))

    # ---------- DAYWISE CONTENT ------------
    for day in itinerary["days"]:
        # Day Header
        day_header = f"Day {day['day']}"
        elements.append(Paragraph(day_header, heading_style))
        elements.append(Spacer(1, 0.2 * inch))

        # Activities
        for activity in day["activities"]:
            elements.append(Paragraph(
                f"<b>{activity['time']}</b> : {activity['activity']}",
                normal_style
            ))

            elements.append(Paragraph(
                f"Location : {activity['location']}",
                normal_style
            ))

            elements.append(Paragraph(
                f"Estimated Cost : INR {activity['estimated_cost']}",
                normal_style
            ))

            elements.append(Paragraph(
                f"Travel Suggestions : {activity['transport_suggestion']}",
                normal_style
            ))

            elements.append(Spacer(1, 0.15 * inch))

        # Daily Expense at End of Day
        elements.append(Paragraph(
            f"<b>Daily Expense : INR {day['daily_estimated_total']}</b>",
            normal_style
        ))

        elements.append(Spacer(1, 0.4 * inch))

    # ---------- ADDITIONAL TIPS ----------
    elements.append(Paragraph(
        "Additional Tips to enhance your experience",
        heading_style
    ))

    elements.append(Spacer(1, 0.2 * inch))

    for tip in itinerary["travel_tips"]:
        elements.append(Paragraph(f"- {tip}", normal_style))
        elements.append(Spacer(1, 0.1 * inch))

    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    return pdf