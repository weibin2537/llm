# 使用 Node.js 20 镜像作为基础镜像
FROM node:20-slim

# 设置工作目录
WORKDIR /app

# 将 package.json、yarn.lock 和相关配置文件复制到容器内
COPY package*.json yarn.lock .eslintrc.json .prettierrc .babelrc webpack.config.js ./

# 安装依赖，使用 yarn
RUN yarn install

# 复制源代码和公共文件
COPY public/ ./public
COPY src/ ./src
COPY .husky/ .husky/

# 创建一个环境变量默认值
ENV REACT_APP_BACKEND_URL=http://chatbox-backend:8000

# 构建前端应用
RUN yarn build

# 添加启动脚本来处理环境变量
RUN echo '#!/bin/sh \n\
# Use a simple HTTP server instead of React dev server in production \n\
npx serve -s build -l 3000' > /app/start.sh && chmod +x /app/start.sh

# 启动前端应用
CMD ["/app/start.sh"]

# 暴露端口
EXPOSE 3000
