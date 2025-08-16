# md 转 jsonl

## 介绍

仅使用 `Python` 标准库实现的 `markdown` 转 `jsonl` 工具。

## 使用方法

本程序基于 `Python 3.12` 开发。

直接执行命令：

```bash
cd \the\path\to\md-to-jsonl
python main.py
```

程序会将 `\the\path\to\md-to-jsonl\mds` 文件夹中的所有 `<file_name>.md` 文件转化为 `<file_name>.jsonl` 文件，并存入 `\the\path\to\md-to-jsonl\jsonls`。

## 转化规范

以 `\n\n` 为分隔符，读取 `md` 文件的各个分块。

每个分块转化为一个 `json` 对象，对象结构为：

```json
{
    "chunk_id": <chunk_id>,
    "chunk_content": <chunk_content>,
    "metadata": {
        "chunk_type": <chunk_type>,
        "file_name": <file_name>,
        "title_level_1": <title_level_1>,
        ...
        "title_level_n": <title_level_n>
    }
}
```

对键的解释：

- `<chunk_id>`：`文件名_编号`；
- `<chunk_content>`：分块的文本内容；
- `<chunk_type>`：`text`、`table` 或 `image`；
- `<file_name>`：`文件名`；
- `<title_level_n>`：n 级标题。

> 分块之间使用 `\n\n` 分隔。标题也视作分块，与其他分块之间也使用 `\n\n` 分隔，但是标题只会作为其下的 `text`、`table` 或 `image` 分块的元数据，并不会转化为独立的 `json` 对象。

## markdown 规范

表格使用 `html` 的 `<table>` 标签表示。

图片使用 `html` 的 `<img>` 标签表示。

表标题和图标题使用 `html` 的 `<center>` 标签表示，其中：

- 表标题在表格的 `html` 代码之上，和代码同属一个分块；
- 图标题在图片的 `html` 代码之下，和代码同属一个分块。
