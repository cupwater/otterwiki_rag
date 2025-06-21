# OtterWiki 文件上传功能实现

## 功能概述

在 OtterWiki 的创建页面功能中增加了文件上传功能。当用户上传文件后，系统会自动解析文件内容并转化为 markdown 格式，作为新创建页面的内容。

## 实现内容

### 1. 依赖添加
- 在 `pyproject.toml` 中添加了 `docling>=2.37.0` 依赖
- docling 是 IBM 开发的强大文档解析库，支持多种文件格式

### 2. 前端修改
- 修改了 `otterwiki/templates/create.html` 模板
- 添加了文件上传表单，支持以下文件类型：
  - 文本文件：.md, .markdown, .csv, .txt, .json
  - 文档文件：.docx, .doc, .xls, .xlsx, .ppt, .pptx, .pdf

### 3. 后端实现
#### 文件解析器 (`otterwiki/file_parser.py`)
- 创建了 `FileParser` 类，负责解析各种文件格式
- 支持的解析功能：
  - **纯文本文件**：自动检测是否为代码，适当格式化
  - **Markdown 文件**：直接读取内容
  - **CSV 文件**：转换为 markdown 表格格式
  - **JSON 文件**：格式化为代码块显示
  - **其他格式**：使用 docling 库进行高级解析

#### 视图函数修改 (`otterwiki/views.py`)
- 修改了 `create()` 函数以处理文件上传
- 添加了文件解析和页面创建逻辑
- 包含错误处理和用户反馈

## 支持的文件格式

### 文本格式
- **.txt, .text** - 纯文本文件，自动检测代码格式
- **.md, .markdown** - Markdown 文件，直接导入
- **.csv** - CSV 文件，转换为 markdown 表格
- **.json** - JSON 文件，格式化为代码块

### 文档格式 (通过 docling 解析)
- **.docx, .doc** - Microsoft Word 文档
- **.xlsx, .xls** - Microsoft Excel 电子表格
- **.pptx, .ppt** - Microsoft PowerPoint 演示文稿
- **.pdf** - PDF 文档
- **.html, .htm** - HTML 文件

## 主要特性

1. **智能解析**：根据文件类型选择最合适的解析方法
2. **格式保持**：尽可能保持原文档的结构和格式
3. **表格支持**：CSV 和 Excel 文件自动转换为 markdown 表格
4. **错误处理**：优雅的错误处理，提供有意义的错误信息
5. **性能优化**：使用临时文件处理，自动清理资源
6. **兼容性**：向后兼容，不影响现有的创建页面功能

## 使用方法

1. 访问创建页面 (`/-/create`)
2. 输入页面名称
3. 可选：选择要上传的文件
4. 点击"Create and open in editor"
5. 如果上传了文件，系统会自动解析并创建包含文件内容的页面

## 文件结构

```
otterwiki/
├── file_parser.py          # 新增：文件解析器模块
├── templates/
│   └── create.html         # 修改：添加文件上传表单
├── views.py                # 修改：添加文件上传处理逻辑
└── ...
pyproject.toml              # 修改：添加 docling 依赖
test_upload_files/          # 新增：测试文件示例
├── sample.csv
├── sample.json
└── sample.md
```

## 测试文件

项目中包含了三个测试文件：
- `test_upload_files/sample.csv` - CSV 表格示例
- `test_upload_files/sample.json` - JSON 数据示例  
- `test_upload_files/sample.md` - Markdown 文档示例

## 安装和部署

1. 确保已安装 docling 依赖：
   ```bash
   pip install docling>=2.37.0
   ```

2. 重启 OtterWiki 服务

3. 功能即可使用

## 技术细节

- **docling 库**：提供强大的文档解析能力，支持复杂文档结构
- **临时文件处理**：安全地处理上传文件，自动清理临时文件
- **错误处理**：包含完整的异常处理机制
- **性能考虑**：首次使用 docling 时会下载模型文件，后续使用会从缓存加载

## 注意事项

1. docling 库较大，首次使用时需要下载模型文件
2. 对于大型文档，解析可能需要一些时间
3. 某些复杂格式的文档可能需要手工调整解析结果
4. 建议在生产环境中测试各种文件格式的解析效果