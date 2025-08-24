# 1 HTTP Image Server

使用 `Python` 标准库实现的 HTTP 图片服务器。

# 2 使用指南

## 2.1 环境配置

**第一步：创建虚拟环境并安装依赖（以 `conda` 为例）**

```bash
conda create -n http-image-server python=3.12
conda activate http-image-server
```

> 无需其他依赖，仅需安装 Python。

## 2.2 运行程序

> `/the/path/to/HTTP_Image_Server` 指的是本项目文件夹所在的路径。

```bash
cd /the/path/to/HTTP_Image_Server
python main.py
```

服务器运行后，默认监听 `http://localhost:8000`。

## 2.3 图片文件准备

创建文件夹 `/the/path/to/HTTP_Image_Server/images` 并放入图片文件，即可通过 `url` 访问图片。

> 仅支持 `.png`、`.jpg` 和 `.jpeg` 图片。
> `images` 文件夹中，有测试图片 `test.png`。
> 启动服务器后，在浏览器访问 `http://localhost:8000/images/test.png` 即可显示测试图片。
