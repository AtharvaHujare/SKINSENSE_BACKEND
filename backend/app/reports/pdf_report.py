import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)

DISEASE_NAMES = {
    "nv": "Melanocytic Nevus",
    "mel": "Melanoma",
    "bcc": "Basal Cell Carcinoma",
    "akiec": "Actinic Keratosis / Intraepithelial Carcinoma",
    "bkl": "Benign Keratosis",
    "df": "Dermatofibroma",
    "vasc": "Vascular Lesion",
}

def get_styles():
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0D47A1"),
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Heading2"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1565C0"),
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        textColor=colors.white,
        backColor=colors.HexColor("#1565C0"),
        leftIndent=5,
        spaceBefore=10,
        spaceAfter=8,
    )

    normal_style = styles["BodyText"]

    small_style = ParagraphStyle(
        "SmallStyle",
        parent=styles["BodyText"],
        fontSize=9,
        textColor=colors.grey,
    )


    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "heading": heading_style,
        "normal": normal_style,
        "small": small_style,
    }
def add_header(story, styles):

    report_id = f"SSR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    case_id = f"CASE-{datetime.now().strftime('%H%M%S')}"

    story.append(
        Paragraph(
            "SkinSense AI",
            styles["title"]
        )
    )

    story.append(
        Paragraph(
            "AI-Powered Skin Screening Report",
            styles["subtitle"]
        )
    )

    story.append(Spacer(1, 12))

    info = [
    [
        "Report ID",
        "Case ID",
        "Generated On"
    ],
        [
            report_id,
            case_id,
            datetime.now().strftime("%d %b %Y | %I:%M %p")
        ]
    ]

    table = Table(
        info,
        colWidths=[160, 160, 170]
    )

    table.setStyle(
        TableStyle(
            [

                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565C0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F5F9FF")),

                ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#B0BEC5")),

                ("ALIGN", (0, 0), (-1, -1), "CENTER"),

                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),

                ("TOPPADDING", (0, 0), (-1, -1), 10),

            ]
        )
    )

    story.append(table)

    story.append(Spacer(1, 18))

def add_patient_information(
    story,
    styles,
    patient_name,
):

    story.append(
        Paragraph(
            "Patient Information",
            styles["heading"]
        )
    )

    patient_table = Table(
        [
    ["Patient Name", patient_name],
    ["Patient ID", patient_name],
    ["Report Date", datetime.now().strftime("%d %b %Y")],
],
        colWidths=[160, 320],
    )

    patient_table.setStyle(
        TableStyle(
            [

                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF4FC")),

                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),

                ("TOPPADDING", (0, 0), (-1, -1), 8),

            ]
        )
    )

    story.append(patient_table)

    story.append(Spacer(1, 15))
def add_ai_findings(
    story,
    styles,
    prediction,
    confidence,
    risk_level,
):

    story.append(
        Paragraph(
            "AI Findings",
            styles["heading"]
        )
    )

    disease = DISEASE_NAMES.get(
        prediction.lower(),
        prediction
    )

    risk_color = (
        colors.red
        if risk_level == "High"
        else colors.green
    )

    findings_table = Table(
        [
            ["Prediction", disease],
            ["Confidence", f"{confidence:.2f}%"],
            ["Risk Level", risk_level],
        ],
        colWidths=[160, 320],
    )

    findings_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF4FC")),

                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),

                ("TEXTCOLOR", (1, 2), (1, 2), risk_color),

                ("FONTNAME", (1, 2), (1, 2), "Helvetica-Bold"),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),

                ("TOPPADDING", (0, 0), (-1, -1), 8),

                ("ALIGN", (0, 0), (-1, -1), "LEFT"),

                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    story.append(findings_table)

    story.append(Spacer(1, 15))
def add_images(
    story,
    styles,
    original_image_path,
    heatmap_path,
):

    story.append(
        Paragraph(
            "Image Analysis",
            styles["heading"]
        )
    )

    images = []

    # Original Image
    if os.path.exists(original_image_path):
        original = Image(
            original_image_path,
            width=180,
            height=180,
        )
    else:
        original = Paragraph(
            "Original Image Not Found",
            styles["normal"]
        )

    # Grad-CAM Image
    if os.path.exists(heatmap_path):
        heatmap = Image(
            heatmap_path,
            width=180,
            height=180,
        )
    else:
        heatmap = Paragraph(
            "Grad-CAM Not Found",
            styles["normal"]
        )

    images.append(
        [
            Paragraph("<b>Original Image</b>", styles["normal"]),
            Paragraph("<b>Grad-CAM Heatmap</b>", styles["normal"]),
        ]
    )

    images.append(
        [
            original,
            heatmap,
        ]
    )

    table = Table(
        images,
        colWidths=[240, 240]
    )

    table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )

    story.append(table)

    story.append(Spacer(1, 20))
def add_assessment(
    story,
    styles,
    prediction,
    risk_level,
):

    story.append(
        Paragraph(
            "AI Assessment",
            styles["heading"]
        )
    )

    disease_names = {
        "nv": "Melanocytic Nevus",
        "mel": "Melanoma",
        "bcc": "Basal Cell Carcinoma",
        "akiec": "Actinic Keratosis",
        "bkl": "Benign Keratosis",
        "df": "Dermatofibroma",
        "vasc": "Vascular Lesion",
    }

    disease = disease_names.get(
        prediction.lower(),
        prediction
    )

    if risk_level == "High":
        text = f"""
        The uploaded lesion was classified as
        <b>{disease}</b>.

        This lesion falls under the
        <font color='red'><b>High Risk</b></font>
        category based on the trained AI model.

        Immediate consultation with a dermatologist
        is strongly recommended.
        """
    else:
        text = f"""
        The uploaded lesion was classified as
        <b>{disease}</b>.

        This lesion falls under the
        <font color='green'><b>Low Risk</b></font>
        category based on the trained AI model.

        Continue routine monitoring and seek
        medical advice if the lesion changes.
        """

    story.append(
        Paragraph(
            text,
            styles["normal"]
        )
    )

    story.append(Spacer(1, 15))
def add_disclaimer(
    story,
    styles,
):

    story.append(
        Paragraph(
            "Disclaimer",
            styles["heading"]
        )
    )

    text = """
    This report has been generated using the
    SkinSense AI deep learning model.

    It is intended for preliminary screening
    purposes only and should not replace
    professional medical diagnosis.

    Always consult a qualified dermatologist
    before making healthcare decisions.
    """

    story.append(
        Paragraph(
            text,
            styles["normal"]
        )
    )

    story.append(Spacer(1,15))
def add_doctor_review(
    story,
    styles,
):

    story.append(
        Paragraph(
            "Doctor Review",
            styles["heading"]
        )
    )

    table = Table(
        [
            ["Doctor Name", ""],
            ["Remarks", ""],
            ["Signature", ""],
        ],
        colWidths=[120,360],
        rowHeights=[30,70,30]
    )

    table.setStyle(
        TableStyle(
            [

                ("GRID",(0,0),(-1,-1),0.5,colors.grey),

                ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#EAF4FC")),

                ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),

                ("BOTTOMPADDING",(0,0),(-1,-1),8),

            ]
        )
    )

    story.append(table)

    story.append(Spacer(1,20))
def add_footer(
    story,
    styles,
):

    story.append(
        Paragraph(
            "<font color='grey'>Generated by SkinSense AI v1.0 | AI-Assisted Healthcare Screening</font>",
            styles["small"]
        )
    )
def add_recommendations(
    story,
    styles,
    risk_level,
):

    story.append(
        Paragraph(
            "Recommendations",
            styles["heading"]
        )
    )

    if risk_level == "High":
        recommendation = """
        <b>Recommended Actions</b><br/><br/>
        • Consult a dermatologist as soon as possible.<br/>
        • Do not rely solely on this AI report for diagnosis.<br/>
        • Additional clinical examination or biopsy may be required.<br/>
        • Monitor the lesion for any rapid changes in size, color, or shape.
        """
    else:
        recommendation = """
        <b>Recommended Actions</b><br/><br/>
        • Continue regular skin self-examinations.<br/>
        • Protect your skin from excessive sun exposure.<br/>
        • Use sunscreen (SPF 30+) when outdoors.<br/>
        • Consult a dermatologist if the lesion changes in appearance.
        """

    story.append(
        Paragraph(
            recommendation,
            styles["normal"]
        )
    )

    story.append(Spacer(1, 15))
def generate_skin_report(
    patient_name,
    prediction,
    confidence,
    risk_level,
    output_path,
    original_image_path,
    heatmap_path,
):

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=25,
        rightMargin=25,
        topMargin=20,
        bottomMargin=20,
    )

    styles = get_styles()

    story = []

    add_header(
        story,
        styles
    )

    add_patient_information(
        story,
        styles,
        patient_name
    )

    add_ai_findings(
        story,
        styles,
        prediction,
        confidence,
        risk_level,
    )

    add_images(
        story,
        styles,
        original_image_path,
        heatmap_path,
    )

    add_recommendations(
        story,
        styles,
        risk_level,
    )

    add_disclaimer(
        story,
        styles,
    )

    add_doctor_review(
        story,
        styles,
    )

    add_footer(
        story,
        styles,
    )

    doc.build(story)

    return output_path