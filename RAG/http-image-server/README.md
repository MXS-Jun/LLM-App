# http 图片服务器

## 介绍

利用 `Python` 标准库实现的 `http` 图片服务器。

### 使用方法

本程序基于 `Python 3.12` 开发。

直接执行命令：

```bash
cd \the\path\to\http-image-server
python main.py
```

服务器运行后，默认监听 `http://localhost:8000`。

在 `main.py` 的父目录下创建文件夹 `images`，并将图片放入其中即可通过 `url` 访问图片。

> 仅支持 `.png`、`.jpg` 和 `.jpeg` 图片。

### 测试用例

`images` 文件夹中，有测试图片 `test.png`。

启动服务器后，在浏览器访问 `http://localhost:8000/images/test.png` 即可显示测试图片。