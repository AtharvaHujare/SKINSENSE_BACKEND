"""
SkinSense AI - PDF Medical Report Generator Utility.

Generates professional, publication-quality medical diagnostic PDF reports using ReportLab.
"""

import os
import uuid
from datetime import datetime
from typing import Optional, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

from app.config import settings


def generate_analysis_report(
    analysis: Any,
    prediction: Any,
    doctor_review: Any,
    patient: Optional[Any] = None,
    doctor: Optional[Any] = None
) -> str:
    """
    Generates a medical PDF diagnostic report for a reviewed lesion analysis session.

    Args:
        analysis: Analysis model or dictionary containing session details.
        prediction: Prediction model or dictionary containing AI diagnostic results.
        doctor_review: DoctorReviewRequest/Response object or dict containing physician notes.
        patient: Patient ORM entity or dict (optional).
        doctor: Doctor ORM entity or dict (optional).

    Returns:
        Absolute string filepath of the generated PDF document.
    """
    # Extract IDs & Attributes cleanly
    analysis_id = str(getattr(analysis, "id", None) or (analysis.get("analysis_id") if isinstance(analysis, dict) else analysis))
    lesion_location = str(getattr(analysis, "lesion_body_location", None) or (analysis.get("lesion_body_location") if isinstance(analysis, dict) else "N/A"))
    analysis_status = str(getattr(analysis, "status", None) or (analysis.get("status") if isinstance(analysis, dict) else "COMPLETED"))
    created_at = str(getattr(analysis, "created_at", None) or (analysis.get("created_at") if isinstance(analysis, dict) else datetime.utcnow()))

    # Prediction fields
    predicted_class = str(getattr(prediction, "predicted_class", None) or (prediction.get("predicted_class") if isinstance(prediction, dict) else (prediction.get("prediction") if isinstance(prediction, dict) else "N/A")))
    
    raw_conf = getattr(prediction, "confidence_score", None) or getattr(prediction, "confidence", None) or (prediction.get("confidence") if isinstance(prediction, dict) else 0.0)
    try:
        conf_float = float(raw_conf)
        confidence_str = f"{conf_float * 100:.2f}%" if conf_float <= 1.0 else f"{conf_float:.2f}%"
    except (ValueError, TypeError):
        confidence_str = f"{raw_conf}%"

    risk_level = str(getattr(prediction, "risk_level", None) or (prediction.get("risk_level") if isinstance(prediction, dict) else "Low"))

    # Doctor Review fields
    diagnosis = str(getattr(doctor_review, "diagnosis", None) or (doctor_review.get("diagnosis") if isinstance(doctor_review, dict) else "N/A"))
    notes = str(getattr(doctor_review, "notes", None) or (doctor_review.get("notes") if isinstance(doctor_review, dict) else "N/A"))
    recommendation = str(getattr(doctor_review, "recommendation", None) or (doctor_review.get("recommendation") if isinstance(doctor_review, dict) else "N/A"))
    reviewed_at = str(getattr(doctor_review, "reviewed_at", None) or (doctor_review.get("reviewed_at") if isinstance(doctor_review, dict) else datetime.utcnow()))

    # Patient details
    patient_name = "N/A"
    patient_id = "N/A"
    if patient:
        p_first = getattr(patient, "first_name", "") or (patient.get("first_name", "") if isinstance(patient, dict) else "")
        p_last = getattr(patient, "last_name", "") or (patient.get("last_name", "") if isinstance(patient, dict) else "")
        patient_name = f"{p_first} {p_last}".strip() or "Anonymous Patient"
        patient_id = str(getattr(patient, "id", "N/A"))
    elif hasattr(analysis, "patient_id"):
        patient_id = str(analysis.patient_id)

    # Doctor details
    doctor_name = "N/A"
    license_number = "N/A"
    specialization = "Dermatology"
    hospital_affinity = "N/A"
    if doctor:
        d_first = getattr(doctor, "first_name", "") or (doctor.get("first_name", "") if isinstance(doctor, dict) else "")
        d_last = getattr(doctor, "last_name", "") or (doctor.get("last_name", "") if isinstance(doctor, dict) else "")
        doctor_name = f"Dr. {d_first} {d_last}".strip()
        license_number = str(getattr(doctor, "license_number", "N/A") or (doctor.get("license_number") if isinstance(doctor, dict) else "N/A"))
        specialization = str(getattr(doctor, "specialization", "Dermatology") or (doctor.get("specialization") if isinstance(doctor, dict) else "Dermatology"))
        hospital_affinity = str(getattr(doctor, "hospital_affinity", "N/A") or (doctor.get("hospital_affinity") if isinstance(doctor, dict) else "N/A"))

    # Ensure output directory exists
    reports_dir = os.path.abspath(settings.REPORTS_DIR)
    os.makedirs(reports_dir, exist_ok=True)

    filename = f"analysis_{analysis_id}.pdf"
    pdf_path = os.path.join(reports_dir, filename)

    # Setup ReportLab Document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY_COLOR = colors.HexColor("#1E3A8A")   # Deep Blue
    TEXT_DARK = colors.HexColor("#1E293B")       # Slate 800
    BG_LIGHT = colors.HexColor("#F8FAFC")        # Slate 50
    ACCENT_WARN = colors.HexColor("#DC2626") if risk_level.upper() == "HIGH" else colors.HexColor("#16A34A")

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=PRIMARY_COLOR,
        alignment=1,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#64748B"),
        alignment=1,
        spaceAfter=15
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=PRIMARY_COLOR,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=TEXT_DARK
    )

    bold_label = ParagraphStyle(
        "BoldLabel",
        parent=body_style,
        fontName="Helvetica-Bold"
    )

    footer_style = ParagraphStyle(
        "ReportFooter",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#94A3B8"),
        alignment=1
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("SkinSense AI Medical Report", title_style))
    story.append(Paragraph("Confidential Clinical Lesion Diagnostic & Physician Review Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_COLOR, spaceAfter=15))

    # Table Helper Function
    def build_table(data_matrix, col_widths=None):
        t = Table(data_matrix, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
            ('TEXTCOLOR', (0, 0), (-1, -1), TEXT_DARK),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9.5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
        ]))
        return t

    # 1. Patient & Doctor Information Tables (2 Columns)
    story.append(Paragraph("1. Patient & Practitioner Metadata", section_heading))
    
    info_data = [
        [Paragraph("Patient Name:", bold_label), Paragraph(patient_name, body_style),
         Paragraph("Reviewing Doctor:", bold_label), Paragraph(doctor_name, body_style)],
        [Paragraph("Patient ID:", bold_label), Paragraph(patient_id, body_style),
         Paragraph("Medical License:", bold_label), Paragraph(license_number, body_style)],
        [Paragraph("Anatomical Location:", bold_label), Paragraph(lesion_location, body_style),
         Paragraph("Specialization:", bold_label), Paragraph(specialization, body_style)],
    ]
    info_table = Table(info_data, colWidths=[120, 140, 120, 160])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('TEXTCOLOR', (0, 0), (-1, -1), TEXT_DARK),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    # 2. Analysis Summary & AI Prediction
    story.append(Paragraph("2. AI Computer Vision Diagnostic Summary", section_heading))
    ai_data = [
        [Paragraph("Analysis Session ID:", bold_label), Paragraph(analysis_id, body_style)],
        [Paragraph("Workflow Status:", bold_label), Paragraph(analysis_status, body_style)],
        [Paragraph("Predicted Diagnostic Class:", bold_label), Paragraph(predicted_class, body_style)],
        [Paragraph("Classification Confidence Score:", bold_label), Paragraph(confidence_str, body_style)],
        [Paragraph("Assessed Risk Severity Level:", bold_label),
         Paragraph(f"<font color='{ACCENT_WARN.hexval()}'><b>{risk_level.upper()}</b></font>", body_style)],
    ]
    ai_table = build_table(ai_data, col_widths=[180, 360])
    story.append(ai_table)
    story.append(Spacer(1, 12))

    # 3. Doctor Review & Clinical Assessment
    story.append(Paragraph("3. Physician Clinical Review & Treatment Plan", section_heading))
    review_data = [
        [Paragraph("Physician Diagnosis:", bold_label), Paragraph(diagnosis, body_style)],
        [Paragraph("Clinical Notes:", bold_label), Paragraph(notes, body_style)],
        [Paragraph("Recommended Action:", bold_label), Paragraph(recommendation, body_style)],
        [Paragraph("Review Completion Timestamp:", bold_label), Paragraph(str(reviewed_at), body_style)],
    ]
    review_table = build_table(review_data, col_widths=[180, 360])
    story.append(review_table)
    story.append(Spacer(1, 20))

    # Divider & Footer
    story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#CBD5E1"), spaceAfter=10))
    story.append(Paragraph("Generated by SkinSense AI Medical Platform • Confidential Patient Diagnostic Record", footer_style))

    # Build PDF
    doc.build(story)

    return pdf_path
