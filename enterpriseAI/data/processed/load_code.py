import re
import os
from tree_sitter_languages import get_language, get_parser

# 支持的语言模型
LANGUAGES = {
    '.py': get_language('python'),
    '.java': get_language('java'),
}

def extract_proc_name(text):
    match = re.search(r'CREATE\s+OR\s+REPLACE\s+PROCEDURE\s+(\w+)', text, re.IGNORECASE)
    return match.group(1) if match else "UNKNOWN_PROCEDURE"

def extract_tables(text):
    # 匹配 INSERT INTO / UPDATE / DELETE FROM 后面的表名
    matches = re.findall(r'(INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+(\w+)', text, re.IGNORECASE)
    return list(set([match[1].upper() for match in matches]))

def extract_called_procs(text):
    # 匹配 CALL 或直接调用过程名
    matches = re.findall(r'(CALL\s+)?(\bPROC_[A-Z_]+)', text, re.IGNORECASE)
    return list(set([m[1].upper() for m in matches]))

# Tree-sitter 集成函数解析

def parse_code_tree(file_path):
    ext = os.path.splitext(file_path)[1]
    if ext not in LANGUAGES:
        print(f"暂不支持的扩展名：{ext}")
        return []

    parser = get_parser(LANGUAGES[ext])

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    tree = parser.parse(bytes(code, "utf8"))
    root = tree.root_node

    return extract_functions(code, root, ext)

def extract_functions(code, root, ext):
    from tree_sitter import Node

    def get_node_text(node: Node) -> str:
        return code[node.start_byte:node.end_byte]

    sft_data = []

    def traverse(node: Node):
        if ext == ".py" and node.type == "function_definition":
            func_text = get_node_text(node)
            docstring_node = node.child_by_field_name("body").child_by_field_name("expression")
            doc = get_node_text(docstring_node) if docstring_node and docstring_node.type == "string" else "暂无注释"
            sft_data.append({
                "prompt": f"请说明这个函数的作用：\n{func_text[:100]}...",
                "response": doc.strip('"\'')
            })

        elif ext == ".java" and node.type == "method_declaration":
            func_text = get_node_text(node)
            comment = find_preceding_comment(node, code)
            sft_data.append({
                "prompt": f"请说明这个 Java 方法的作用：\n{func_text[:100]}...",
                "response": comment or "暂无注释"
            })

        for child in node.children:
            traverse(child)

    traverse(root)
    return sft_data

def find_preceding_comment(node, code: str) -> str:
    lines = code[:node.start_byte].splitlines()
    for line in reversed(lines[-3:]):
        line = line.strip()
        if line.startswith("//"):
            return line.strip("/").strip()
    return ""

def process_bdy_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    proc_name = extract_proc_name(content)
    tables = extract_tables(content)
    called_procs = extract_called_procs(content)

    sft_data = []

    if tables:
        sft_data.append({
            "prompt": f"{proc_name} 修改了哪些表？",
            "response": ", ".join(tables)
        })

    if called_procs:
        sft_data.append({
            "prompt": f"{proc_name} 调用了哪些存储过程？",
            "response": ", ".join(called_procs)
        })

    return sft_data

def process_code_file(file_path):
    return parse_code_tree(file_path)
