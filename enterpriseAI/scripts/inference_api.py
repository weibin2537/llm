from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

# 模型路径
BASE_MODEL = "deepseek-ai/deepseek-coder-7b-instruct"
ADAPTER_PATH = "./output/lora_deepseek/lora_adapter"
TOKENIZER_PATH = "./output/lora_deepseek/tokenizer"

app = FastAPI(title="企业智能助手 API")

class PromptInput(BaseModel):
    prompt: str

@app.on_event("startup")
def load_model():
    global tokenizer, model

    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
    model.eval()
    print("✅ 模型与 LoRA adapter 加载完成！")

@app.post("/predict")
def predict(input: PromptInput):
    try:
        full_prompt = f"### 问题：{input.prompt}\n\n### 回答："
        inputs = tokenizer(full_prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                top_p=0.9
            )

        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        answer = result.split("### 回答：")[-1].strip()
        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))