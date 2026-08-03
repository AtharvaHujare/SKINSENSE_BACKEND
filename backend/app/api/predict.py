"""
Prediction API Endpoints.
"""

import os
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from app.ai.predict import predict
from app.reports.pdf_report import generate_skin_report


router = APIRouter(tags=["Prediction"])


@router.post("/predict", summary="Predict skin disease")
async def predict_skin(
    request: Request,
    file: UploadFile = File(...)
):
    """
    Upload a skin lesion image and return the AI prediction.
    """

    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed."
        )

    suffix = Path(file.filename).suffix

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        shutil.copyfileobj(file.file, temp)
        temp_path = temp.name

    try:
        result = predict(temp_path)

        # Generate PDF report
        patient_name = Path(file.filename).stem

        report_path = (
            f"reports/{patient_name}_skin_report.pdf"
        )

        generate_skin_report(
            patient_name,
            result["prediction"],
            result["confidence"],
            result["risk_level"],
            report_path,
            temp_path,
            result["heatmap_path"],
        )

        # Add report path to response
        result["report_path"] = report_path

        # Convert Grad-CAM path to public URL
        filename = Path(result["heatmap_path"]).name

        result["heatmap_url"] = (
            f"{request.base_url}outputs/{filename}"
        )

        # Remove local heatmap path
        result.pop("heatmap_path")

        return result

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/report/{filename}", summary="Download PDF report")
async def download_report(filename: str):
    """
    Download generated skin screening PDF report.
    """

    report_path = Path("reports") / filename

    if not report_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return FileResponse(
        path=report_path,
        media_type="application/pdf",
        filename=filename
    )