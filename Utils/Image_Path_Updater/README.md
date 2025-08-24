# 1 Image Path Updater

将 `Markdown` 文件中引用的图片移动到图片服务器并修改对应的链接。

# 2 使用指南

## 2.1 环境配置

**第一步：创建虚拟环境并安装依赖（以 `conda` 为例）**

```bash
conda create -n image-path-updater python=3.12
conda activate image-path-updater
```

> 无需其他依赖，仅需安装 Python。

## 2.2 Markdown 文件夹准备

> `/the/path/to/Image_Path_Updater` 指的是本项目文件夹所在的路径。

将 Markdown 文件夹复制到 `/the/path/to/Image_Path_Updater/md-folds`。

Markdown 文件夹的结构示例：

```
<file_name>
  - <file_name>.md
  - images
    - <image_0_name>.png
    - <image_1_name>.jpg
    ...
    - <image_n_name>.jpeg
```

`<file_name>.md` 中，应使用 HTML 的 `<img>` 标签引用图片，如：

> `<img src="./images/<image_0_name>.png`

## 2.3 运行程序

```bash
cd /the/path/to/Image_Path_Updater
python main.py
```

更新后的 `Markdown` 文件会出现在 `/the/path/to/Image_Path_Updater/mds`。

程序运行后，文件夹的结构示例：

```
Image_Path_Updater
  - md-folds
    - <file_name>
      - <file_name>.md
      - images
        - <image_name>.png
  - mds
    - <file_name>.md
HTTP_Image_Server
  - images
    - <file_name>
      - <image_name>.png
```

本项目需要搭配 HTTP_Image_Server 使用，并且两项目文件夹需位于同一级目录。
