from datetime import datetime

import yaml


def read_tag(start_index: int, data: bytes, tag_definitions: dict):
    index = start_index
    tag = data[index]
    tag_name = tag_definitions[tag]["name"]
    print(tag_name)
    index += 1

    if "fields" in tag_definitions[tag]:
        for field in tag_definitions[tag]["fields"]:
            field_name = field
            field_length = tag_definitions[tag]["fields"][field]
            if field_length == 1:
                field_value = int(data[index])
            else:
                field_value = int.from_bytes(data[index: index + field_length], byteorder="little")
            print(f"\t{field_name}: {field_value}")
            index += field_length

    return start_index + tag_definitions[tag]["length"]


def main():
    data = read_binary_data()

    tag_definitions = read_tag_definitions()

    index = print_header(data, tag_definitions)

    for i in range(20):
        index = read_tag(index, data, tag_definitions)


def read_tag_definitions():
    with open("tag_definitions.yaml") as input_file:
        tag_definitions = yaml.safe_load(input_file)
    return tag_definitions


def read_binary_data():
    with open("C:/Users/Peter/TomTom Sports/TomTom GPS Watch/2021-01-15/Running_15-55-51.ttbin",
              'rb') as input_file:
        data = input_file.read()
    return data


def print_header(data, tag_definitions):
    print(f"File version = {hex(data[1])}")
    print(f"Firmware version = "
          f"{int.from_bytes(data[2:4], byteorder='big')}."
          f"{int.from_bytes(data[4:6], byteorder='big')}."
          f"{int.from_bytes(data[6:8], byteorder='big')}")
    print(f"Product ID: {hex(data[9])} {hex(data[10])}")
    start_time = int.from_bytes(data[11:15], byteorder='little')
    print(f"Activity start time: {datetime.fromtimestamp(start_time)}")
    watch_time = int.from_bytes(data[111:115], byteorder='little')
    print(f"Watch time: {datetime.fromtimestamp(watch_time)}")
    print(f"Time offset: {int.from_bytes(data[115:119], byteorder='little')}")
    num_record_tags = int(data[120])
    print(f"Num record tags: {num_record_tags}")
    index = print_tag_definitions(num_record_tags, data, tag_definitions)
    return index


def print_tag_definitions(num_record_tags: int, data: bytes, tag_definitions: dict):
    index = 121
    record_tag_num = 1
    while record_tag_num <= num_record_tags:
        raw_tag = int(data[index])
        tag_length = int.from_bytes(data[index + 1: index + 3], byteorder='little')
        if raw_tag not in tag_definitions:
            raise TypeError("Unknown tag defined in header but not defined in tag_definitions")
        tag_name = tag_definitions[raw_tag]["name"]

        if tag_definitions[raw_tag]["length"] != tag_length:
            raise TypeError("Mismatch between tag length defined in header and tag length defined"
                            f"in tag_definitions for tag: {tag_name}")
        index += 3
        record_tag_num += 1
    print("Header tags read successfully.")
    return index

main()
