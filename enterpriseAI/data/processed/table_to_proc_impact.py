import json
# 构建表结构对存储过程的影响的问答数据集以及sft
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_table_to_proc(proc_table_graph):
    table_map = {}

    for proc, access in proc_table_graph.items():
        for table in access.get("reads", []):
            table_map.setdefault(table, {"read_by": [], "written_by": []})
            table_map[table]["read_by"].append(proc)

        for table in access.get("writes", []):
            table_map.setdefault(table, {"read_by": [], "written_by": []})
            table_map[table]["written_by"].append(proc)

    return table_map

def generate_sft_from_table(table_map):
    sft_data = []

    for table, usage in table_map.items():
        affected = set(usage.get("read_by", []) + usage.get("written_by", []))
        if affected:
            sft_data.append({
                "prompt": f"如果我修改了 {table} 表，会影响哪些存储过程？",
                "response": ", ".join(sorted(affected))
            })

    return sft_data

def save_sft(data, output_file="./data/table_impact_sft_dataset.jsonl"):
    with open(output_file, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"✅ 已生成 {len(data)} 条表结构影响语料，保存至 {output_file}")

def main():
    proc_table_graph = load_json("./data/proc_table_graph.json")
    table_map = build_table_to_proc(proc_table_graph)
    sft = generate_sft_from_table(table_map)
    save_sft(sft)

if __name__ == "__main__":
    main()