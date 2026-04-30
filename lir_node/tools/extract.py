import re


def extract(text: str):
    # 提取所有数字
    match = re.search(r'\d+', text)
    if match:
        number = int(match.group())  # 结果为 1
        return number
    else:
        print("extract failed")
        exit(-1)


def get_sorted_name_list(mapping_temp):
    # 获取经排序后的名字列表
    name_list = list(mapping_temp.keys())
    name_list.sort(key=lambda x: extract(x))
    return name_list


if __name__ == "__main__":
    mapping = {
        "LirNode-2": 1,
        "LirNode-1": 5,
    }
    node_index = extract("LirNode-1")
    print(get_sorted_name_list(mapping))
