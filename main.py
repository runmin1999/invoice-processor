"""
发票 PDF 批量处理工具

功能：
1. 从指定文件夹读取发票 PDF，提取发票信息（号码、日期、类型、金额、公司名、税号、车牌号）
2. 校验公司名和税号是否匹配预期值
3. 按规则重命名 PDF 并复制到输出文件夹
4. 将发票信息汇总到 Excel 表格
"""

import os
import shutil

import pdfplumber
from gooey import Gooey, GooeyParser

from config import CONFIG
from excel_writer import write_excel_batch
from ocr import is_scanned_pdf, ocr_extract
from parser import (
    check_company,
    find_duplicates,
    parse_fallback,
    parse_invoice,
    unique_filename,
)


def walk_directory(root_dir):
    """遍历目录，返回 (所有文件路径列表, 所有文件名列表, 所有文件夹路径列表)"""
    all_files, all_names, folder_paths = [], [], []
    for root, _, file_names in os.walk(root_dir):
        root = root.replace("\\", "/")
        files = [os.path.join(root, n).replace("\\", "/") for n in file_names]
        all_files.append(files)
        all_names.append(list(file_names))
        folder_paths.append(root)
    return all_files, all_names, folder_paths


def ensure_output_dir(index, root_dir, out_dir, source_dir):
    """确保输出目录存在，返回 (输出目录路径, 表格 sheet 名)"""
    target_dir = source_dir.replace(root_dir, out_dir)
    if index == 0:
        sheet_name = source_dir.split("/")[-1]
    else:
        sheet_name = source_dir.replace(root_dir + "/", "").replace("/", "_")

    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)
    return target_dir, sheet_name


def process_directory(filepaths, filenames, folder_paths, out_dir, root_dir):
    """主处理流程：遍历文件，解析 PDF，复制重命名，写入 Excel"""
    first_target_dir = None
    excel_rows_by_sheet = {}

    for i, folder_files in enumerate(filepaths):
        seen_names, seen_numbers = [], []
        target_dir, sheet_name = ensure_output_dir(i, root_dir, out_dir, folder_paths[i])
        if first_target_dir is None:
            first_target_dir = target_dir

        for j, filepath in enumerate(folder_files):
            fname = filenames[i][j]
            if not fname.lower().endswith(".pdf"):
                dest = filepath.replace(root_dir, target_dir)
                shutil.copy(filepath, dest)
                continue

            with pdfplumber.open(filepath) as pdf:
                text = pdf.pages[0].extract_text() or ""

            if CONFIG["ocr_enabled"] and is_scanned_pdf(text, CONFIG["ocr_threshold"]):
                try:
                    text = ocr_extract(filepath)
                except Exception:
                    text = ""

            company_ok, tax_ok = check_company(text)
            try:
                row = parse_invoice(text, company_ok, tax_ok, fname)
                output_name = f"{row[4]}-{row[5]}"
            except Exception:
                row = parse_fallback(fname)
                output_name = row[4]

            row = find_duplicates(row, seen_numbers)
            row = unique_filename(row, seen_names, output_name)

            shutil.copy(filepath, os.path.join(target_dir, row[7]))
            excel_rows_by_sheet.setdefault(sheet_name, []).append(row)

    write_excel_batch(first_target_dir, excel_rows_by_sheet)


def simplify_filenames(filepaths, filenames):
    """简化 PDF 文件名（去除前缀编号）"""
    for folder_files, folder_names in zip(filepaths, filenames):
        seen = []
        for filepath, fname in zip(folder_files, folder_names):
            if not fname.lower().endswith(".pdf"):
                continue
            try:
                parts = fname.split("-")
                new_name = parts[-1] if len(parts) > 1 else fname
                if "_" in new_name:
                    new_name = new_name.split("_")[0] + ".pdf"

                seen.append(new_name)
                count = seen.count(new_name)
                base = os.path.join(
                    os.path.dirname(filepath),
                    new_name.replace(".pdf", "").replace(".PDF", ""),
                )
                if count > 1:
                    new_path = f"{base}-{count}.pdf"
                else:
                    new_path = f"{base}.pdf"
                os.rename(filepath, new_path)
            except (OSError, IndexError):
                pass


@Gooey(
    program_name="发票处理工具",
    language="chinese",
    clear_before_run=True,
    encoding="utf-8",
    progress_regex=r"^progress: (\d+)%$",
    navigation="TABBED",
)
def main_gui():
    """图形界面入口"""
    description = (
        "注意：使用时不要打开目标文件夹\n"
        "1. PDF 复制后重新命名并生成 Excel 汇总\n"
        "2. 简化文件夹内 PDF 的文件名"
    )
    parser = GooeyParser(description=description)
    subs = parser.add_subparsers(help="功能", dest="command", required=False)

    tab1 = subs.add_parser("初始化 PDF 并生成 Excel")
    tab1.add_argument(
        "输入路径", help="原 PDF 文件所在的文件夹", widget="DirChooser"
    )

    tab2 = subs.add_parser("简化 PDF 文件名")
    tab2.add_argument(
        "重命名路径", help="要重命名文件所在的文件夹", widget="DirChooser"
    )

    args = parser.parse_args()
    return vars(args).get("输入路径"), vars(args).get("重命名路径")


if __name__ == "__main__":
    root_dir, rename_dir = main_gui()

    if root_dir and root_dir.strip():
        out_dir = root_dir.rstrip("\\/").rstrip(":") + "_输出"
        root_dir = root_dir.replace("\\", "/")
        out_dir = out_dir.replace("\\", "/")
        files, names, folders = walk_directory(root_dir)
        if files:
            process_directory(files, names, folders, out_dir, root_dir)
            print("1. 已复制 PDF 并重新命名")
            print("2. 已保存发票信息至 Excel")
        else:
            print("未找到文件，请选择正确的文件夹！")

    elif rename_dir and rename_dir.strip():
        rename_dir = rename_dir.replace("\\", "/")
        files, names, _ = walk_directory(rename_dir)
        if files:
            simplify_filenames(files, names)
            print("已简化 PDF 文件名")
        else:
            print("未找到文件，请选择正确的文件夹！")
