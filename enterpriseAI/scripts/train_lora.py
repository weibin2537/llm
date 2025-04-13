import os
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import get_peft_model, LoraConfig, TaskType

MODEL_NAME = "deepseek-ai/deepseek-coder-7b-instruct"
DATA_PATH = "./data/final_sft_dataset.jsonl"
OUTPUT_DIR = "./output/lora_deepseek"

def load_sft_dataset(path):
    # 使用 HuggingFace datasets 库加载 JSONL 格式
    return load_dataset("json", data_files=path, split="train")

def apply_prompt_template(example):
    # 拼接 Prompt 模板
    prompt = f"### 问题：{example['prompt']}\n\n### 回答：{example['response']}"
    return {"text": prompt}

def tokenize(example, tokenizer):
    return tokenizer(example["text"], truncation=True, padding="max_length", max_length=1024)

def main():
    # 加载模型与 tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="auto",
        load_in_8bit=True,
        trust_remote_code=True
    )

    # 应用 LoRA
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )
    model = get_peft_model(model, lora_config)

    # 加载 & 预处理数据
    dataset = load_sft_dataset(DATA_PATH)
    dataset = dataset.map(apply_prompt_template)
    dataset = dataset.map(lambda x: tokenize(x, tokenizer), batched=True)

    # 训练参数
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        learning_rate=2e-4,
        logging_steps=10,
        save_steps=100,
        save_total_limit=2,
        fp16=True,
        logging_dir="./logs"
    )

    # DataCollator 自动处理 padding
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    # 构建 Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
        data_collator=data_collator
    )

    # 开始训练
    trainer.train()

    # 保存 LoRA adapter 权重
    model.save_pretrained(os.path.join(OUTPUT_DIR, "lora_adapter"))
    tokenizer.save_pretrained(os.path.join(OUTPUT_DIR, "tokenizer"))

    print("✅ 微调训练完成，模型已保存！")

if __name__ == "__main__":
    main()