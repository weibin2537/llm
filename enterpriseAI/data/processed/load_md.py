import re

def process_md_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 正则匹配标题与正文段落
    matches = re.findall(r'(#{2,6})\s+(.*?)\n+(.*?)(?=\n#+|\Z)', content, re.DOTALL)

    sft_data = []

    for heading_level, title, paragraph in matches:
        title = title.strip()
        paragraph = paragraph.strip().replace("\n", " ")
        
        if len(paragraph) < 10 or len(title) < 3:
            continue

        # 构造自然语言提问
        question = f"{title} 是什么？"
        sft_data.append({
            "prompt": question,
            "response": paragraph
        })

    return sft_data