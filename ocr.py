"""OCR 模块，用于处理扫描件/图片发票"""

import tempfile
import os

import fitz  # PyMuPDF
from paddleocr import PaddleOCR

_ocr_engine = None


def get_ocr_engine():
    """懒加载 PaddleOCR 引擎"""
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
    return _ocr_engine


def pdf_to_images(pdf_path, dpi=200):
    """将 PDF 第一页转为图片"""
    doc = fitz.open(pdf_path)
    page = doc[0]
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    pix.save(tmp.name)
    doc.close()
    return tmp.name


def ocr_extract(pdf_path):
    """对 PDF 进行 OCR 识别，返回文本"""
    img_path = pdf_to_images(pdf_path)
    try:
        engine = get_ocr_engine()
        result = engine.ocr(img_path, cls=True)
        if not result or not result[0]:
            return ""
        lines = [line[1][0] for line in result[0]]
        return "\n".join(lines)
    finally:
        os.unlink(img_path)


def is_scanned_pdf(text, threshold=50):
    """判断是否为扫描件（文本过少）"""
    return len(text.strip()) < threshold
