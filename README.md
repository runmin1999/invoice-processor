# 发票处理工具 (Invoice Tool)

批量处理发票 PDF 的桌面工具，自动提取发票信息、重命名文件并生成 Excel 汇总表。

## 功能

- **提取发票信息**：从 PDF 中自动识别发票号码、日期、类型、金额、公司名、税号、车牌号
- **校验公司信息**：自动比对公司名和税号是否正确
- **智能重命名**：按 `发票类型-金额` 规则重命名 PDF，自动处理重名
- **生成 Excel 汇总**：按文件夹分 sheet，将所有发票信息写入 Excel
- **简化文件名**：一键去除 PDF 文件名中的前缀编号
- **图形界面**：基于 Gooey 的中文 GUI，支持 Tab 页切换功能

## 安装

```bash
pip install pdfplumber openpyxl gooey
```

## 使用

### 方式一：命令行

```bash
# 处理发票 PDF 并生成 Excel
python invoice_tool.py

# 运行后在 GUI 中选择功能和文件夹
```

### 方式二：直接运行

```bash
python invoice_tool.py
```

启动后会出现图形界面，选择：
1. **初始化 PDF 并生成 Excel** — 选择 PDF 文件夹，自动处理并输出到 `文件夹_输出`
2. **简化 PDF 文件名** — 选择文件夹，批量简化 PDF 文件名

## 配置

编辑 `config.json` 修改公司信息：

```json
{
    "expected_company": "你的公司名称",
    "expected_tax_id": "你的税号",
    "excel_filename": "发票汇总统计.xlsx"
}
```

| 字段 | 说明 |
|------|------|
| `expected_company` | 要校验的公司名称，留空则跳过校验 |
| `expected_tax_id` | 要校验的税号，留空则跳过校验 |
| `excel_filename` | 输出的 Excel 文件名 |

## 输出结构

```
原文件夹_输出/
├── 子文件夹1/
│   ├── 充电费-123.45.pdf
│   ├── 住宿费-200.00.pdf
│   └── 发票汇总统计.xlsx
└── 子文件夹2/
    └── ...
```

## 依赖

- Python 3.7+
- pdfplumber
- openpyxl
- gooey

## 注意事项

- 处理期间不要打开目标文件夹
- 首次使用请先编辑 `config.json` 填写公司名和税号（留空则跳过校验）
- 仅支持中国大陆发票格式
