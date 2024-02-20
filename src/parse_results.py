import os
import pandas


def results_to_df(results_dir):
    # ignore subfolders
    file_list = list(filter(lambda f: os.path.isfile(results_dir + f), os.listdir(results_dir)))
    absolute_file_list = [results_dir + file for file in file_list] # absolute path

    data = [
        format_df_from_file(file, data_value)
        for file in absolute_file_list
        for data_value in parse_file_data(file)
    ]

    df = pandas.DataFrame(data)

    return df

def format_df_from_file(file, data_value):
    file_metadata = metadata(file)
    return format_df_from_values(*file_metadata, data_value)
    

def format_df_from_values(scene, gripper, applied_force, data):
    return {
        'scene': scene,
        'gripper': gripper,
        'applied_force': applied_force,
        'result': data
    }

# extract data and metadata from file
def metadata(file):
    file = file.split("/")[-1].split(".")[0] # ignore directory and file extension
    file_metadata = file.split("_")
    return file_metadata

# extract data array from file content
def parse_file_data(file):
    f = open(file, 'r')
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
    clean_result = result[0:-2] # remove \n and unit char
    value = float(clean_result)

    return value


if __name__ == '__main__':
    results_dir = "/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/results/"
    df = results_to_df(results_dir)
    print(df)