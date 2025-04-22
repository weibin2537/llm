# FROM ubuntu:20.04

# # 安装必要的依赖
# RUN apt-get update && apt-get install -y curl bash

# # 安装 ollama
# RUN curl -fsSL https://ollama.com/install.sh | sh

# # 创建启动脚本
# RUN echo '#!/bin/bash\n\
#           # 启动 ollama 服务\n\
#           ollama start &\n\
#           # 等待 ollama 启动完成\n\
#           until nc -zv 127.0.0.1 11434; do echo "Waiting for ollama to start..."; sleep 2; done\n\
#           # 运行 deepseek 模型\n\
#           ollama run deepseek-r1:7b' > /start-model.sh

FROM ubuntu:20.04

# 安装必要的依赖
RUN apt-get update && apt-get install -y \
    curl \
    bash \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# 安装Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# 创建启动脚本
RUN echo '#!/bin/bash\n\
# 启动Ollama服务\n\
ollama start &\n\
# 等待Ollama启动\n\
until nc -zv 127.0.0.1 11434; do echo "Waiting for ollama to start..."; sleep 2; done\n\
# 拉取模型\n\
ollama pull deepseek-r1:7b\n\
# 保持容器运行，这很重要\n\
tail -f /dev/null' > /start-model.sh

# 使脚本可执行
RUN chmod +x /start-model.sh

# 设置启动时执行脚本
CMD ["/start-model.sh"]

# 暴露端口
EXPOSE 11434
