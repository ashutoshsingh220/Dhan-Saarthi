import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

class ScamOCRService:
    @classmethod
    def extract_text(cls, image_bytes: bytes) -> str:
        """
        Preferred processing pipeline:
        Image Decode -> OpenCV Preprocessing -> Grayscale -> Noise Reduction
        -> Contrast Enhancement -> Thresholding -> Tesseract OCR -> Text Cleanup
        """
        try:
            # Image Decode
            np_arr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if img is None:
                raise ValueError("Could not decode image")

            # OpenCV Preprocessing
            # Grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Noise Reduction
            denoised = cv2.fastNlMeansDenoising(gray, h=30)
            
            # Contrast Enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            contrast = clahe.apply(denoised)
            
            # Thresholding
            # Using Otsu's thresholding
            _, thresh = cv2.threshold(contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Tesseract OCR
            # Converting back to PIL Image for pytesseract
            pil_img = Image.fromarray(thresh)
            
            # Use English and Hindi if available, otherwise just English
            try:
                extracted_text = pytesseract.image_to_string(pil_img, lang='eng+hin')
            except pytesseract.TesseractError:
                extracted_text = pytesseract.image_to_string(pil_img, lang='eng')
                
            # Text Cleanup
            cleaned_text = " ".join(extracted_text.split())
            
            return cleaned_text
        except Exception as e:
            logger.error(f"OCR Extraction failed: {e}")
            raise e

ocr_service = ScamOCRService()
