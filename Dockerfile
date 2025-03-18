# 使用官方的 Python 3.13 镜像作为基础镜像
FROM python:3.13.2-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有文件到工作目录
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir .

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["python", "weather.py"]