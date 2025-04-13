import json
import os
# 对存储过程或者表结构修改的影响分析 并转化成sft
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def reverse_call_graph(call_graph):
    reversed_graph = {}
    for caller, callees in call_graph.items():
        for callee in callees:
            reversed_graph.setdefault(callee, []).append(caller)
    return reversed_graph

def build_table_readers(proc_table_graph):
    readers = {}
    for proc, access in proc_table_graph.items():
        for table in access.get("reads", []):
            readers.setdefault(table, []).append(proc)
    return readers

def analyze_impact(call_graph, table_graph):
    reversed_call = reverse_call_graph(call_graph)
    table_readers = build_table_readers(table_graph)

    sft_data = []

    for proc, access in table_graph.items():
        affected_procs = set()

        # 🧠 表写入的反向查找：谁读取了我写的表
        for table in access.get("writes", []):
            readers = table_readers.get(table, [])
            affected_procs.update(readers)

        # 🧠 过程调用反向传播：谁可能调用我
        visited = set()
        stack = [proc]
        while stack:
            current = stack.pop()
            for parent in reversed_call.get(current, []):
                if parent not in visited:
                    visited.add(parent)
                    affected_procs.add(parent)
                    stack.append(parent)

        # ✅ 构建问答样本
        if affected_procs:
            sft_data.append({
                "prompt": f"如果我修改了 {proc}，会影响哪些存储过程？",
                "response": ", ".join(sorted(affected_procs))
            })

    return sft_data

def save_sft(data, output_file="./data/impact_sft_dataset.jsonl"):
    with open(output_file, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"✅ 已保存 {len(data)} 条影响分析语料到 {output_file}")

def main():
    call_graph = load_json("./data/proc_call_graph.json")
    table_graph = load_json("./data/proc_table_graph.json")
    sft = analyze_impact(call_graph, table_graph)
    save_sft(sft)

if __name__ == "__main__":
    main()