def generate_txt_file(filename: str, size_in_mb: int) -> int:
    """
    进行指定大小的 txt 文件的生成
    :param filename:  txt 文件的名称
    :param size_in_mb:  txt 文件的大小
    :return:
    """
    size_in_bytes = size_in_mb * 1024 * 1024  # 总共要写的字节数
    chunk_size = 1024 * 1024  # 每次写入1MB
    remainder = size_in_bytes % chunk_size  # 最后剩余的部分
    with open(filename, 'w') as f:  # 打开文件
        chunk = "a" * chunk_size  # 创建要写入的内容
        for _ in range(size_in_mb):
            f.write(chunk)  # 循环写入
        if remainder:
            f.write("a" * remainder)  # 写入剩余部分
    print(f"File {filename} of size {size_in_mb}MB created.", flush=True)
    return size_in_bytes
