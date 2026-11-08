FROM python_env:latest

# 先安装依赖，避免修改代码后重复安装
COPY resources/requirements.txt /lir_node/requirements.txt
RUN python -m pip install \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    -r /lir_node/requirements.txt

# 最后复制代码和配置
COPY resources/daemons /etc/frr/daemons
COPY ./lir_node /lir_node

ENTRYPOINT ["python", "/lir_node/start.py", "container"]