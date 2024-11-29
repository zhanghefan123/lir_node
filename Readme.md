# directory

- lir_node 代码目录
  - apps 应用
    - network 网络层
    - sender 底层的发送
    - transport 传输层
      - udp udp 传输层
        - udp_client udp 客户端
        - udp_server udp 服务器端
  - defined_types 自定义类型
  - modules 模块
  - signal_decorator 信号装饰器 (用于接受信号退出)
  - tools 工具
  - start.py 启动文件

- resources 资源目录
  - daemons frr 配置
  - requirements.txt 配置相关

- Dockerfile 构建镜像所用