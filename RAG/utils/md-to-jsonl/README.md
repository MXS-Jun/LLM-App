# md-to-jsonl

一个将 Markdown 文件转换为带摘要信息的 JSONL 格式文件的工具，支持文本、表格、图片等内容类型的解析与摘要生成。

## 功能说明

该工具可批量处理指定目录下的 Markdown 文件，主要功能包括：

- 解析 Markdown 中的标题层级结构（支持 1-8 级标题）。
- 按段落（`\n\n`）拆分内容并生成唯一 `chunk_id`。
- 自动识别内容类型（文本、表格、图片）。
- 基于 Ollama 模型生成各类型内容的摘要。
- 生成文件级别的整体摘要。
- 将处理结果保存为 JSONL 格式（每行一个 JSON 对象）。

## 依赖环境

- Python 3.12+。
- Ollama 服务（用于运行大语言模型）。
- 所需 Python 库：`httpx`、`ollama`、`pyyaml`。

## 安装步骤

1. 克隆或下载本项目。
2. 安装依赖库：

```bash
pip install httpx
pip install ollama
pip install pyyaml
```

3. 确保 Ollama 服务已启动并拉取配置中指定的模型（默认：`gemma3:12b`）：

```bash
ollama pull gemma3:12b
```

> 需要拉取支持多模态输入的模型（除 `gemma3` 外，还有 `qwen2.5vl`、`minicpm 系列` 等）。

## 配置说明

配置文件为 `config.yaml`，主要参数说明：

```yaml
host: http://localhost:11434  # Ollama 服务地址
model: gemma3:12b             # 使用的模型名称
options:
  num_ctx: 8192               # 上下文窗口大小
  temperature: 0.7            # 生成温度（0-1，值越高越随机）
  num_predict: -1             # 预测token数量（-1为自动）
  top_k: 20                   # 采样候选数量
  top_p: 0.95                 # 核采样概率
  min_p: 0.05                 # 最小概率阈值
```

## 使用方法

1. 将需要转换的 Markdown 文件放入 `mds` 目录（若不存在请手动创建）。
2. 运行主程序：

```bash
cd /the/path/to/md-to-jsonl
python main.py
```

3. 转换后的 JSONL 文件将保存到 `jsonls` 目录。

## 输出格式

JSONL 中每个对象包含以下字段：

```json
{
  "chunk_id": "文件名_序号",
  "chunk_content": "原始内容",
  "metadata": {
    "chunk_type": "text/table/image",  // 内容类型
    "titles": ["标题1", "标题2"],       // 所属标题层级
    "chunk_summary": "内容摘要",        // 该chunk的摘要
    "file_id": "文件名",                // 源文件名称
    "file_summary": "文件总摘要"        // 整个文件的摘要
  }
}
```

## 示例

项目中包含 `mds/test.md` 作为示例文件，运行程序后可在 `jsonls` 目录查看转换结果。

## 注意事项

1. 确保 Ollama 服务在配置的 `host` 地址正常运行。
2. 图片处理需要网络连接（用于下载图片 URL）。
3. 大文件处理可能需要调整 `num_ctx` 等模型参数。
4. 首次运行会下载模型（根据网络情况可能需要较长时间）。
5. 若处理大量文件，建议分批进行以避免资源占用过高
