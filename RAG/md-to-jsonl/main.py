from pathlib import Path
import json


MD_DIR = Path(__file__).parent / "mds"
JSONL_DIR = Path(__file__).parent / "jsonls"


def parse_md(md_path: str):
    try:
        md_file = Path(md_path)
        content = md_file.read_text(encoding="utf-8")
    except Exception as e:
        raise ValueError(f"[ERROR] read md file failed: {e}")

    file_name = md_file.name
    cnt = 0
    titles = ["", "", "", "", "", ""]
    json_obj_list = []

    chunks = [chunk.strip() for chunk in content.split("\n\n")]

    for chunk in chunks:
        if chunk.startswith("# "):
            titles = ["", "", "", "", "", ""]
            titles[0] = chunk[2:]
        elif chunk.startswith("## "):
            titles = titles[:1] + ["", "", "", "", ""]
            titles[1] = chunk[3:]
        elif chunk.startswith("### "):
            titles = titles[:2] + ["", "", "", ""]
            titles[2] = chunk[4:]
        elif chunk.startswith("#### "):
            titles = titles[:3] + ["", "", ""]
            titles[3] = chunk[5:]
        elif chunk.startswith("##### "):
            titles = titles[:4] + ["", ""]
            titles[4] = chunk[6:]
        elif chunk.startswith("###### "):
            titles = titles[:5] + [""]
            titles[5] = chunk[7:]
        else:
            cnt += 1
            chunk_id = file_name + "_" + str(cnt)

            chunk_type = "text"
            if chunk.endswith("</table>"):
                chunk_type = "table"
            elif chunk.startswith("<img src="):
                chunk_type = "image"

            json_obj = {}
            json_obj["chunk_id"] = chunk_id
            json_obj["chunk_content"] = chunk
            json_obj["metadata"] = {
                "chunk_type": chunk_type,
                "file_name": file_name,
            }

            for i in range(len(titles)):
                if titles[i] != "":
                    json_obj["metadata"][f"title_level_{i+1}"] = titles[i]

            json_obj_list.append(json_obj)

    return json_obj_list


def save_jsonl(json_obj_list: list, jsonl_path: str):
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for json_obj in json_obj_list:
            json_obj_str = json.dumps(json_obj, ensure_ascii=False)
            f.write(json_obj_str + "\n")


if __name__ == "__main__":
    for md in MD_DIR.glob("*.md"):
        if md.is_file():
            json_obj_list = parse_md(md.absolute().as_posix())
            save_jsonl(
                json_obj_list, JSONL_DIR.absolute().as_posix() + f"/{md.stem}.jsonl"
            )
            print(f"[INFO] converted '{md.name}' to '{md.stem}.jsonl'")
