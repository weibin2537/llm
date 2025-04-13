import os
import re
import json

def extract_proc_name(text):
    match = re.search(r'CREATE\s+OR\s+REPLACE\s+PROCEDURE\s+(\w+)', text, re.IGNORECASE)
    return match.group(1).upper() if match else None

def extract_called_procs(text):
    matches = re.findall(r'(CALL\s+)?(\bPROC_[A-Z_]+)', text, re.IGNORECASE)
    return list(set([m[1].upper() for m in matches]))

def build_call_graph(directory="./data/raw", output_file="./data/proc_call_graph.json"):
    graph = {}

    for fname in os.listdir(directory):
        if fname.endswith(".bdy"):
            with open(os.path.join(directory, fname), "r", encoding="utf-8") as f:
                content = f.read()

            proc_name = extract_proc_name(content)
            if not proc_name:
                continue

            called = extract_called_procs(content)
            graph[proc_name] = called

            # 确保所有 called 的过程也出现在图中（即使没被定义）
            for callee in called:
                if callee not in graph:
                    graph[callee] = []

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)

    print(f"✅ 已构建调用图，共包含 {len(graph)} 个过程，已保存到 {output_file}")
    return graph