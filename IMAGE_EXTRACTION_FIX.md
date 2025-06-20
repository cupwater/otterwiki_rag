# PDF/DOCX 文件图片提取功能修复

## 问题描述

在OtterWiki中，当用户上传PDF、DOCX等文档格式时，文档中的图片无法在生成的页面中正确显示。这是因为：

1. **docling库的限制**：docling库在将文档转换为Markdown时，会生成图片引用，但这些引用指向临时路径
2. **缺少图片保存机制**：图片文件没有被保存到OtterWiki的附件系统中
3. **路径引用错误**：生成的Markdown中的图片路径无法正确解析

## 解决方案

### 1. 修改文件解析器 (`otterwiki/file_parser.py`)

添加了以下功能：

- **图片提取**：从docling解析结果中提取嵌入的图片
- **图片保存**：将图片保存到页面的附件目录中
- **路径修正**：更新Markdown中的图片引用路径

#### 主要修改：

```python
def _parse_with_docling(self, file_path, filename, page_path=None):
    """解析文件并处理嵌入的图片"""
    result = self.converter.convert(file_path)
    markdown_content = result.document.export_to_markdown()
    
    # 处理图片
    if page_path and hasattr(result, 'images') and result.images:
        markdown_content = self._process_embedded_images(
            markdown_content, result.images, page_path, filename
        )
    
    return markdown_content

def _process_embedded_images(self, markdown_content, images, page_path, original_filename):
    """处理嵌入的图片并保存到页面目录"""
    # 创建页面附件目录
    page_dir = Path(page_path)
    page_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存图片并更新Markdown引用
    for i, image in enumerate(images):
        image_filename = f"{Path(original_filename).stem}_image_{i+1}{image_ext}"
        image_path = page_dir / image_filename
        
        with open(image_path, 'wb') as f:
            f.write(image.data)
        
        # 更新Markdown中的图片引用
        markdown_content = re.sub(
            rf'!\[([^\]]*)\]\(image_{i+1}\)',
            rf'![\1](./{image_filename})',
            markdown_content
        )
    
    return markdown_content
```

### 2. 修改视图处理 (`otterwiki/views.py`)

更新文件上传处理逻辑，传递页面路径给文件解析器：

```python
# 获取页面目录路径用于保存嵌入的图片
page_dir = os.path.join(storage.path, p.pagepath)

# 解析上传的文件，包含图片处理
markdown_content = parse_uploaded_file(uploaded_file, uploaded_file.filename, page_dir)
```

## 功能特性

### 支持的文档格式
- PDF (.pdf)
- Microsoft Word (.docx, .doc)
- Microsoft Excel (.xlsx, .xls)
- Microsoft PowerPoint (.pptx, .ppt)
- 其他docling支持的格式

### 图片处理
- **自动提取**：从文档中自动提取嵌入的图片
- **格式保持**：保持原始图片格式（PNG、JPEG、GIF等）
- **唯一命名**：为每个图片生成唯一的文件名
- **路径修正**：自动更新Markdown中的图片引用路径

### 文件命名规则
图片文件按照以下规则命名：
```
{原文档名}_image_{序号}.{扩展名}
```

例如：
- `document.pdf` → `document_image_1.png`, `document_image_2.jpg`
- `report.docx` → `report_image_1.png`, `report_image_2.png`

## 使用方法

1. **上传文档**：在创建新页面时上传PDF或DOCX文件
2. **自动处理**：系统会自动解析文档并提取图片
3. **查看结果**：生成的页面会包含文档内容和正确的图片显示

## 依赖要求

- **docling >= 2.37.0**：用于文档解析
- **Python >= 3.11**：运行环境要求

## 测试

运行测试脚本验证功能：

```bash
python test_image_extraction.py
```

## 注意事项

1. **存储空间**：提取的图片会占用额外的存储空间
2. **性能影响**：大文档的图片提取可能需要较长时间
3. **格式支持**：图片格式支持取决于docling库的能力
4. **错误处理**：如果图片提取失败，会记录错误日志但不会中断页面创建

## 故障排除

### 常见问题

1. **图片不显示**
   - 检查docling是否正确安装
   - 查看应用日志中的错误信息
   - 确认页面附件目录权限

2. **docling不可用**
   - 安装docling：`pip install docling`
   - 检查Python环境

3. **图片路径错误**
   - 确认页面路径正确传递
   - 检查文件权限

### 日志信息

系统会记录以下日志信息：
- 图片保存成功：`Saved embedded image: filename.png`
- 图片保存失败：`Error saving embedded image: error_message`
- 解析错误：`Error parsing with docling: error_message`

## 未来改进

1. **图片压缩**：添加图片压缩功能以减少存储空间
2. **格式转换**：支持图片格式转换
3. **批量处理**：优化大文档的处理性能
4. **预览功能**：添加图片预览功能 