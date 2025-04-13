import re
# 存储过程分析 构建不同的sft用于机器学习
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
#TODO 下面的路径记得补充下，data所在的row的目录下的bdy目录
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
