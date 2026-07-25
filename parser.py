import re

from config import CONFIG

LICENSE_PLATE_PATTERN = re.compile(
    r"[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁台琼使领军北南成广沈济空海]{1}"
    r"[A-HJ-NP-Z]{1}"
    r"[A-HJ-NP-Z0-9]{4}"
    r"[A-HJ-NP-Z0-9挂领学警港澳]{1}"
)


def clean_text(text):
    """去除多余空格和标点"""
    for ch in (" ", "\u3000", "）", ")", "："):
        text = text.replace(ch, "")
    return text


def regex_extract(pattern, text, sep=":", group=-1):
    """用正则从文本中提取字段，失败返回空字符串"""
    match = re.search(pattern, text)
    if match is None:
        return ""
    return clean_text(match[0]).split(sep, 1)[group]


def check_company(pdf_text):
    """校验 PDF 中的公司名和税号是否与预期一致"""
    tax_ok = CONFIG["expected_tax_id"] in pdf_text.replace(" ", "") if CONFIG["expected_tax_id"] else None
    company_ok = CONFIG["expected_company"] in pdf_text if CONFIG["expected_company"] else None
    return company_ok, tax_ok


def _check_label(ok):
    """将校验结果转换为显示文本"""
    if ok is None:
        return "未配置"
    return "通过" if ok else "不通过"


def parse_invoice(pdf_text, company_ok, tax_ok, filename):
    """从 PDF 文本中解析发票信息，返回 list"""
    invoice_number = regex_extract(r"发票号码(.*\d+)", pdf_text)
    invoice_date = regex_extract(r"开票日期(.*)", pdf_text)

    amount_text = regex_extract(r"小写.*(.*[0-9.]+)", pdf_text)
    if not amount_text:
        m = re.search(r"[￥¥]([0-9.]+)", pdf_text)
        amount_text = m.group(1) if m else "0"

    inv_type = regex_extract(r"[/\*]+[\u4e00-\u9fa5]+[ ]", pdf_text)
    if not inv_type:
        inv_type = regex_extract(r"[/（]+[\u4e00-\u9fa5]+[/）]", pdf_text)
        inv_type = inv_type.split("（", 1)[-1] if inv_type else ""
    inv_type = inv_type.split("*", 1)[-1] if inv_type else ""

    if "服务费" in pdf_text and "电费" in pdf_text and "住宿" not in pdf_text:
        inv_type = "充电费"
    elif "服务费" in pdf_text and "住宿" in pdf_text:
        inv_type = "住宿费"

    plate_match = LICENSE_PLATE_PATTERN.search(pdf_text)
    license_plate = plate_match.group(0) if plate_match else ""

    return [
        _check_label(company_ok),
        _check_label(tax_ok),
        int(invoice_number) if invoice_number else 0,
        "无重复",
        inv_type,
        float(amount_text) if amount_text else 0,
        invoice_date,
        "",
        filename,
        license_plate,
    ]


def parse_fallback(filename):
    """解析失败时的兜底数据"""
    return ["", "", "", "", "其他单或读不出来", "", "", "", filename, ""]


def find_duplicates(excel_row, seen_numbers):
    """检测发票号码重复"""
    seen_numbers.append(excel_row[2])
    if seen_numbers.count(excel_row[2]) > 1:
        excel_row[3] = "重复"
    return excel_row


def unique_filename(excel_row, seen_names, output_name):
    """处理重名文件，返回唯一文件名"""
    seen_names.append(output_name)
    count = seen_names.count(output_name)
    if count > 1:
        if excel_row[3] == "重复":
            output_name += "(重复)"
        else:
            output_name += f"_{count}"

    result = output_name + ".pdf"
    result = result.replace(".0.", ".00.").replace(".0_", ".00_").replace(".0(", ".00(")
    excel_row[7] = result
    return excel_row
