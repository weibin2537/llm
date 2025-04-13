import os
import re
import json
# 生成图结构 主要是存储过程和表之间的关系
# 1. 读取目录下的所有.bdy文件           
def extract_proc_name(text):
    match = re.search(r'CREATE\s+OR\s+REPLACE\s+PROCEDURE\s+(\w+)', text, re.IGNORECASE)
    return match.group(1).upper() if match else None

def extract_table_access(text):
    reads = re.findall(r'\bFROM\s+(\w+)', text, re.IGNORECASE)
    reads += re.findall(r'\bJOIN\s+(\w+)', text, re.IGNORECASE)
    writes = re.findall(r'\bINSERT\s+INTO\s+(\w+)', text, re.IGNORECASE)
    writes += re.findall(r'\bUPDATE\s+(\w+)', text, re.IGNORECASE)
    writes += re.findall(r'\bDELETE\s+FROM\s+(\w+)', text, re.IGNORECASE)

    return {
        "reads": list(set([t.upper() for t in reads])),
        "writes": list(set([t.upper() for t in writes]))
    }

def build_proc_table_graph(directory="./data/raw", output_file="./data/proc_table_graph.json"):
    graph = {}

    for fname in os.listdir(directory):
        if fname.endswith(".bdy"):
            with open(os.path.join(directory, fname), "r", encoding="utf-8") as f:
                content = f.read()

            proc_name = extract_proc_name(content)
            if not proc_name:
                continue

            access = extract_table_access(content)
            graph[proc_name] = access

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)

    print(f"✅ 表结构依赖图已生成，共计 {len(graph)} 个过程，保存至 {output_file}")
    return graph