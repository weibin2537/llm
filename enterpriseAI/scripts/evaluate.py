from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset
from sklearn.metrics import accuracy_score
import torch

# 模型路径
BASE_MODEL = "deepseek-ai/deepseek-coder-7b-instruct"
ADAPTER_PATH = "./output/lora_deepseek/lora_adapter"
TOKENIZER_PATH = "./output/lora_deepseek/tokenizer"
TEST_FILE = "./data/final_sft_dataset.jsonl"

def load_model(model_path=None):
    # 加载模型与tokenizer
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH, trust_remote_code=True)
    if model_path:
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            device_map="auto",
            load_in_8bit=True,
            trust_remote_code=True
        )
        model = PeftModel.from_pretrained(model, model_path)
    else:
        model = AutoModelForCausalLM.from_pretrained(BASE_MODEL)
    return model, tokenizer

def evaluate_model(model, tokenizer, dataset):
    model.eval()
    correct = 0
    total = 0

    for example in dataset:
        prompt = example["prompt"]
        expected_response = example["response"]

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=512)
        
        predicted_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        total += 1
        if predicted_response.strip() == expected_response.strip():
            correct += 1
    
    accuracy = correct / total
    print(f"Accuracy: {accuracy:.4f}")
    return accuracy

def load_test_data(file_path):
    dataset = load_dataset("json", data_files=file_path, split="train")
    return dataset

def main():
    # 加载原始模型和微调后的 LoRA 模型
    base_model, tokenizer = load_model()
    fine_tuned_model, _ = load_model(ADAPTER_PATH)

    # 加载测试集
    test_data = load_test_data(TEST_FILE)

    print("Evaluating Base Model:")
    base_model_accuracy = evaluate_model(base_model, tokenizer, test_data)

    print("Evaluating Fine-Tuned Model:")
    fine_tuned_model_accuracy = evaluate_model(fine_tuned_model, tokenizer, test_data)

    # 输出评估结果
    print(f"Base Model Accuracy: {base_model_accuracy:.4f}")
    print(f"Fine-Tuned Model Accuracy: {fine_tuned_model_accuracy:.4f}")

if __name__ == "__main__":
    main()