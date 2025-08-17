# md 图像路径更新器

## 介绍

将 `Markdown` 文件中引用的图片移动到图片服务器中，并将其路径更新为指向服务器中的位置。

## 使用方法

本程序基于 `Python 3.12` 开发。

将 `Markdown` 文件夹复制到 `\the\path\to\md-img-path-updater\md-folds` 后执行命令：

```bash
cd \the\path\to\md-img-path-updater
python main.py
```

更新后的 `Markdown` 文件会出现在 `\the\path\to\md-img-path-updater\mds`。

图片文件复制到 `\the\path\to\http-image-server\images\<file_name>`。

文件夹的结构：

- http-image-server
  - <file_name>
    - <img_0_name>.png
    - <img_1_name>.jpeg
    - ...
    - <img_n_name>.jpg
- md-img-path-updater
  - md-folds
    - <file_name>
      - <file_name>.md
      - images
        - <img_0_name>.png
        - <img_1_name>.jpeg
        - ...
        - <img_n_name>.jpg
  - mds
    - <file_name>.md

## 注意事项

本程序需要搭配 `http-image-server` 使用，`http-image-server` 和 `md-img-path-updater` 应在同一级目录中。

Markdown 中，应使用 `html` 的 `<img>` 标签引用图片。

详情见测试用例，源文件和目标文件均在仓库中。
