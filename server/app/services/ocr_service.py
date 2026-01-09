import fitz
from google.generativeai import GenerativeModel
from pathlib import Path
from typing import Dict, Any
import logging
import base64

logger = logging.getLogger(__name__)

model = GenerativeModel("gemini-2.5-flash")


class OCRService:
    async def extract_text_from_document(self, file_path: str) -> Dict[str, Any]:
        try:
            logger.info(f"Starting OCR extraction for: {file_path}")

            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            doc = fitz.open(file_path)
            markdown_lines = []

            for page in doc:
                pix = page.get_pixmap(dpi=200)
                png_bytes = pix.tobytes("png")

                encoded = base64.b64encode(png_bytes).decode()

                # Send to Gemini Vision
                result = model.generate_content(
                    [
                        {
                            "mime_type": "image/png",
                            "data": png_bytes
                        },
                        "Extract ALL text from this page."
                    ]
                )

                text = result.text or ""
                markdown_lines.append(text)

            markdown_text = "\n\n".join(markdown_lines)

            # same logic
            page_count = len(doc)
            quality_score = self._calculate_quality_score(markdown_text)

            return {
                "success": True,
                "raw_text": markdown_text,
                "page_count": page_count,
                "confidence": quality_score,
                "file_path": file_path
            }

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "raw_text": "",
                "confidence": 0.0,
                "file_path": file_path
            }

    def _calculate_quality_score(self, text: str) -> float:
        length = len(text)
        if length > 100:
            return 0.9
        elif length > 50:
            return 0.7
        return 0.5


ocr_service = OCRService()
