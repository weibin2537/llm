import os
import json
from preprocess.load_bdy import process_bdy_file
from preprocess.load_md import process_md_file
from preprocess.load_code import process_code_file

RAW_DATA_DIR = "./data/raw"
OUTPUT_FILE = "./data/sft_dataset.jsonl"

def generate_dataset():
    dataset = []

    for file_name in os.listdir(RAW_DATA_DIR):
        file_path = os.path.join(RAW_DATA_DIR, file_name)

        if file_name.endswith(".bdy"):
            print(f"🧠 正在处理存储过程文件：{file_name}")
            dataset += process_bdy_file(file_path)

        elif file_name.endswith(".md"):
            print(f"📄 正在处理文档：{file_name}")
            dataset += process_md_file(file_path)

        elif file_name.endswith((".java", ".py", ".sh")):
            print(f"💻 正在处理代码文件：{file_name}")
            dataset += process_code_file(file_path)

        else:
            print(f"⚠️ 未支持的文件类型：{file_name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"✅ 已生成数据集，共计 {len(dataset)} 条样本，保存至 {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_dataset()