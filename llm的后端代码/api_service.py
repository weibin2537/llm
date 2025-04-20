
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import subprocess

# 创建 FastAPI 应用
# app = FastAPI()

# # 配置 CORS
# origins = [
#     "http://frontend-service:80",  # 允许前端应用的地址进行请求
# ]

# # 添加 CORS 中间件
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,  # 允许来自这个列表中的地址进行跨域请求
#     allow_credentials=True,
#     allow_methods=["*"],  # 允许所有方法，如 GET, POST 等
#     allow_headers=["*"],  # 允许所有请求头
# )

# class ModelInput(BaseModel):
#     message: str

# # 模型调用函数
# def run_deepseek_model(input_text):
#     result = subprocess.run(
#         ['/usr/local/bin/ollama', 'run', 'deepseek-r1:7b', input_text],
#         capture_output=True,
#         text=True
#     )
#     if result.returncode == 0:
#         return result.stdout
#     else:
#         return f"Error: {result.stderr}"

# # 定义 POST 路由
# @app.post("/chat")
# async def chat(request: ModelInput):
#     response = run_deepseek_model(request.message)
#     return {"response": response}



import requests
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()



# 配置 CORS
origins = [
    "http://frontend-service:80",  # 允许前端应用的地址进行请求
    "http://localhost:3000",  # 允许本地开发环境的地址进行请求
]

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许来自这个列表中的地址进行跨域请求
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法，如 GET, POST 等
    allow_headers=["*"],  # 允许所有请求头
)


class ModelInput(BaseModel):
    message: str

# 使用 requests 库调用 Ollama API 进行模型交互
def run_deepseek_model(input_text):
    url = "http://model-service:11434/api/generate"  # 使用 Kubernetes 服务名进行访问
    payload = {
        "model": "deepseek-r1:7b",  # 模型名称
        "prompt": input_text,
        "stream": False
    }
    headers = {"Content-Type": "application/json"}

    try:
        # 发送请求到 model-service
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # 如果响应状态码不为 2xx，将引发异常
        return response.json()  # 返回生成的响应
    except requests.exceptions.RequestException as e:
        return {"error": f"Error: {e}"}

@app.post("/chat")
async def chat(request: ModelInput):
    response = run_deepseek_model(request.message)
    return {"response": response}
