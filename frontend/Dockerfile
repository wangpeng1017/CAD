FROM node:18-alpine

WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制应用代码
COPY . .

# 设置后端URL环境变量(指向Kubernetes内部服务)
ENV BACKEND_URL=http://cad-backend:8000

# 暴露端口
EXPOSE 3000

# 开发模式启动
CMD ["npm", "run", "dev"]
