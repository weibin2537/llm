import os
import json

def merge_jsonl_files(input_files, output_file):
    merged = []
    for file_path in input_files:
        if not os.path.exists(file_path):
            print(f"⚠️ 文件不存在：{file_path}，跳过")
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    merged.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"❌ 无法解析：{line[:50]}...")

    with open(output_file, "w", encoding="utf-8") as f:
        for item in merged:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"✅ 合并完成，共 {len(merged)} 条样本，保存至 {output_file}")

if __name__ == "__main__":
    input_files = [
        "./data/sft_dataset.jsonl",
        "./data/impact_sft_dataset.jsonl",
        "./data/table_impact_sft_dataset.jsonl"
    ]
    output_file = "./data/final_sft_dataset.jsonl"
    merge_jsonl_files(input_files, output_file)