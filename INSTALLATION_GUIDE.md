# OtterWiki 文件上传功能安装指南

## 前提条件

- OtterWiki 已正常运行
- Python 3.11 或更高版本
- 管理员权限来安装新的依赖

## 安装步骤

### 1. 安装 docling 依赖

```bash
# 方法1：直接安装
pip install docling>=2.37.0

# 方法2：如果使用项目的pyproject.toml
pip install -e .
```

### 2. 验证安装

```bash
python3 -c "import docling; print('docling installed successfully')"
```

### 3. 重启 OtterWiki 服务

```bash
# 根据你的部署方式重启服务
# 例如：
systemctl restart otterwiki

# 或者如果是开发环境：
# 重新启动 Flask 应用
```

## 功能测试

1. 访问 OtterWiki 的创建页面：`http://your-domain/-/create`
2. 输入页面名称
3. 选择测试文件（可以使用 `test_upload_files/` 目录下的示例文件）
4. 点击"Create and open in editor"
5. 验证文件内容是否正确解析为 markdown

## 故障排除

### docling 安装失败
```bash
# 如果是 Intel Mac，可能需要特定版本
pip install "docling[mac_intel]"

# 如果遇到 PyTorch 相关问题
pip install docling --extra-index-url https://download.pytorch.org/whl/cpu
```

### 首次使用缓慢
- docling 首次使用时会下载模型文件（约2.5分钟）
- 这是一次性过程，后续使用会很快

### 文件解析失败
- 检查文件格式是否受支持
- 查看 OtterWiki 日志中的错误信息
- 确保上传的文件没有损坏

## 支持的文件类型

- **文本文件**：.txt, .md, .csv, .json
- **Office 文档**：.docx, .doc, .xlsx, .xls, .pptx, .ppt
- **其他格式**：.pdf, .html

## 注意事项

1. 大文件解析可能需要较长时间
2. 复杂文档的解析结果可能需要手动调整
3. 确保有足够的磁盘空间存储模型文件
4. 建议在测试环境先验证功能