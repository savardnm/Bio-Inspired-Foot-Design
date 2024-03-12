import os
import pandas

from pprint import pprint


def results_to_df(results_dir):
    # ignore subfolders
    file_list = list(
        filter(lambda f: os.path.isfile(results_dir + f), os.listdir(results_dir))
    )

    absolute_file_list = [results_dir + file for file in file_list]  # absolute path

    data = [
        format_df_from_file(file, data_value)
        for file in absolute_file_list
        for data_value in parse_file_data(file)
    ]

    df = pandas.DataFrame(data)

    return df


def format_df_from_file(file, data_value):
    file_metadata = extract_metadata(file)
    print("data stuffs:\n", data_value)
    pprint(file_metadata)
    return format_df_from_values(data_value, **file_metadata)


def format_df_from_values(result, **parameters):
    parameters["result"] = result

    mandatory_fields = ["pad_strength", "flex_strength", "num_pad_units"]

    for field in mandatory_fields:
        if not field in parameters:
            parameters[field] = 0

    parameters["gripper"] = parameters["path"]
    del parameters["path"]

    return parameters


# extract data and metadata from file
def extract_metadata(file):
    file = file.split("/")[-1].split(".")[0]  # ignore directory and file extension
    file_metadata_array = file.split(":")
    file_metadata = {}
    for item in file_metadata_array:
        if item == "":
            continue

        try:
            key, value = item.split("=")
        except:
            continue

        file_metadata[key] = value

    return file_metadata


# extract data array from file content
def parse_file_data(file):
    f = open(file, "r")
    file_data = []
    while True:
        line = f.readline()
        if not line:
            break
        file_data.append(parse_data_line(line))
    return file_data


# extract data point from single line of file
def parse_data_line(line):
    # ignore description text
    result = line.split(":")[1]
    clean_result = result[0:-2]  # remove \n and unit char
    value = float(clean_result)

    return value


def csvdf():
    labels = [
        "scene",
        "num_pad_units",
        "pad_strength",
        "applied_force",
        "result",
        "flex_strength",
        "gripper",
    ]


if __name__ == "__main__":
    results_dir = "/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/results/"
    df = results_to_df(results_dir)
    print(df)
