import struct

if __name__ == "__main__":
    header_format = "<IQI"
    print(struct.calcsize(header_format))
