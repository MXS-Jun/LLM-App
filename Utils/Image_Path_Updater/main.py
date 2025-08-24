from pathlib import Path
import re
import shutil


SERVER_IMAGES = Path(__file__).parent.parent / "HTTP_Image_Server" / "images"
MD_FOLDS = Path(__file__).parent / "md-folds"
MDS = Path(__file__).parent / "mds"
HOST = "localhost"
PORT = 8000


def extract_img_src(text: str):
    img_tag_pattern = r"<img\s+[^>]*src=[\"'](.*?)[\"']"
    src_match = re.search(img_tag_pattern, text, re.I)
    return src_match.group(1) if src_match else None


def replace_img_src(text: str, new_src: str):
    img_tag_pattern = r"(<img\s+[^>]*src=[\"']).*?([\"'])"
    new_text = re.sub(img_tag_pattern, rf"\1{new_src}\2", text)
    return new_text


def is_file_path(src_content: str) -> bool:
    if not src_content:
        return False
    url_pattern = r"^[a-zA-Z]+://"
    url_match = re.match(url_pattern, src_content, re.I)
    return False if url_match else True


def copy_img_to_server(img_path: str, dst_path: str):
    img_file = Path(img_path)
    dst_dir = Path(dst_path)
    dst_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(img_file, dst_dir)


def update_md_img_path(md_path: str):
    try:
        md_file = Path(md_path)
        content = md_file.read_text(encoding="utf-8")
    except Exception as e:
        raise ValueError(f"[ERROR] read md file failed: {e}")

    new_content = ""

    for line in content.splitlines(keepends=True):
        if line.startswith("<img src="):
            src_content = extract_img_src(line)
            if src_content is not None and is_file_path(src_content):
                img_name = Path(src_content).name
                md_fold_name = md_file.parent.name
                img_path = (md_file.parent / "images" / img_name).absolute().as_posix()
                dst_path = (SERVER_IMAGES / md_fold_name).absolute().as_posix()
                copy_img_to_server(img_path, dst_path)
                new_img_tag = replace_img_src(
                    line, f"http://{HOST}:{PORT}/images/{md_fold_name}/{img_name}"
                )
                new_content += new_img_tag
        else:
            new_content += line

    return new_content


if __name__ == "__main__":
    for md_fold in MD_FOLDS.iterdir():
        for md_file in md_fold.glob("*.md"):
            new_content = update_md_img_path(md_file.absolute().as_posix())
            md_name = md_file.name
            new_md_file = MDS / md_name
            new_md_file.parent.mkdir(parents=True, exist_ok=True)
            new_md_file.write_text(new_content, encoding="utf-8")
            print(f"[INFO] updated '{md_name}'")
