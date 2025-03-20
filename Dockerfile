FROM python_env:latest

RUN apt-get update \
     && apt-get install -y \
    tcpdump

COPY ./lir_node /lir_node

COPY resources/daemons /etc/frr/daemons

COPY resources/requirements.txt /lir_node/requirements.txt

RUN python -m pip install -r /lir_node/requirements.txt


ENTRYPOINT ["python", "/lir_node/start.py"]