# 使用 Python 作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 将后端代码复制到容器内
COPY . .

# 启动 Uvicorn 服务
CMD ["uvicorn", "api_service:app", "--host", "0.0.0.0", "--port", "8000"]

# 暴露端口
EXPOSE 8000