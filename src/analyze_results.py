import numpy as np
import matplotlib.pyplot as plt
from parse_results import *
from copy import deepcopy


def analyze(results_dir):
    results_df = results_to_df(results_dir)
    # print(results_df)
    print("all results >>>>\n", results_df.to_string(), "\nall results <<<<")
    # average_trials(results_df)
    # compare_grippers(results_df)
    # compare_weights(results_df)
    # compare_scenes(results_df)
    compare_finger_flex_effect(results_df)
    finger_flex_2(results_df)

    plt.show()


def compare_flex_vs_rigid(df):
    average_df = average_trials(df)


def compare_grippers(df):
    compare_vertical(df)
    compare_horizontal(df)

def finger_flex_2(df):
    constant_filter = {
        "gripper": "Finger-Flex-Script",
        "scene": "05-Pole-PY",
    }

    variable_filter_list = [
        ("applied_force", "all"),
        ("flex_strength", "all"),
    ]

    multi_boxplot(df, constant_filter, variable_filter_list, title="Effect of Flex Values on Finger Gripper")


    

def multi_boxplot(df, constant_filter, variable_filter_list, title):
    constant_filter_df = filter_df(df, **constant_filter)

    label_list = []
    data_list = []

    variable_filter_df(constant_filter_df, data_list, label_list, variable_filter_list)


    boxplot(
        title=title,
        labels=label_list,
        data=data_list,
    )


def variable_filter_df(df, data_list, label_list, variable_filter_list, label=""):
    print("variable filtering...")

    if not variable_filter_list:
        data_list.append(df['result'])
        label_list.append(label)
        return
    
    variable_filter_list = deepcopy(variable_filter_list)
    column, option_list = variable_filter_list.pop(0)

    print(column, option_list)

    if option_list == "all":
        option_list = df[column].unique()

    print(column, option_list)
    try:
        option_list = sorted(option_list, key=lambda opt: int(opt))
        print("sorted")
    except:
        pass

    print(column, option_list)
    for option in option_list:
        new_label = label + "\n" + str(option)

        option_filter = {column: option}

        filtered_df = filter_df(df, **option_filter)

        variable_filter_df(filtered_df, data_list, label_list, variable_filter_list, new_label)




def compare_finger_flex_effect(df):

    constant_filter = {
        "gripper": "Finger-Flex-Script",
        "scene": "05-Pole-PY",
    }

    finger_df = filter_df(df, **constant_filter)


    force_option_list = finger_df["applied_force"].unique()
    force_option_list.sort()

    label_list = []
    data_list = []

    for force_option in force_option_list:
        label = ""

        force_filter = {"applied_force": force_option}

        label += str(force_option)

        force_filtered_df = filter_df(finger_df, **force_filter)

        flex_option_list = sorted(force_filtered_df["flex_strength"].unique(), key=lambda val: int(val))

        # flex_option_list = [int(item) for item in flex_option_list]

        # flex_option_list.sort()
        # flex_option_list = [str(item) for item in flex_option_list]

        for flex_option in flex_option_list:
            flex_filter = {"flex_strength": flex_option}

            flex_filtered_df = filter_df(force_filtered_df, **flex_filter)

            label2 = label
            label2 += "\n"
            label2 += str(flex_option)

            data_list.append(flex_filtered_df['result'])
            label_list.append(label2)

    boxplot(
        title="Effects of Flex Param on Finger Gripper",
        labels=label_list,
        data=data_list,
    )





def multi_boxplot_results(df, data_set_list, title):
    label_list = []
    data = []

    for label, filter_set in data_set_list:
        label_list.append(label)
        filtered_df = filter_df(**filter_set)
        filtered_results = filtered_df["result"]
        data.append(filtered_results)

    boxplot(title=title, labels=label_list, data=data)


def boxplot_results(df, title, x_axis="gripper", x_axis_list="all", **criteria):
    filtered_df = filter_df(df, **criteria)

    if x_axis == "gripper":
        if x_axis_list == "all":
            x_axis_list = filtered_df["gripper"].unique()

        labels = []
        data = []
        for gripper in x_axis_list:
            gripper_df = filter_df(filtered_df, gripper=gripper)
            results = gripper_df["result"]
            labels.append(gripper)
            data.append(results)

    if x_axis == "scene":
        if x_axis_list == "all":
            x_axis_list = filtered_df["scene"].unique()

        labels = []
        data = []
        for scene in x_axis_list:
            scene_df = filter_df(filtered_df, scene=scene)
            results = scene_df["result"]
            labels.append(scene)
            data.append(results)

    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.75], label="gripper")
    plt.title(title)

    labels = ["\n".join(label.split("-")) for label in labels]
    ax.set_xticklabels(labels, rotation="vertical")
    # plt.xticks([], labels, rotation='vertical')
    bp = ax.boxplot(data, showfliers=False)


def boxplot(title, labels, data):
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.75])
    plt.title(title)

    ax.set_xticklabels(labels, rotation="vertical")
    bp = ax.boxplot(data, showfliers=False)


def compare_scenes(df):
    compare_horizontal_scenes(df)
    compare_vertical_scenes(df)


def compare_horizontal_scenes(df):
    boxplot_results(
        df,
        title="Effect of Pitch Flex on Horizontal Grip Strength",
        x_axis="scene",
        gripper=[
            "Finger-Flex-Script",
            "Louse-Pad-Script",
        ],
        applied_force=["HorizontalForce"],
    )


def compare_vertical_scenes(df):
    boxplot_results(
        df,
        title="Effect of Pitch Flex on Vertical Grip Strength",
        x_axis="scene",
        gripper=[
            "Finger-Flex-Script",
            "Louse-Pad-Script",
        ],
        applied_force=["VerticalForce"],
    )


def compare_weights(df):
    compare_finger_weights(df)
    compare_louse_weights(df)


def compare_finger_weights(df):
    boxplot_results(
        df,
        title="Effect of Compliance on Finger Actuator",
        gripper=[
            "Finger-Rigid",
            "Finger-Flex-Weak",
            "Finger-Flex-Script",
            "Finger-Flex-Strong",
        ],
        applied_force=["VerticalForce"],
        scene=["05-Pole-PY"],
    )


def compare_louse_weights(df):
    boxplot_results(
        df,
        title="Effect of Compliance on Louse Actuator",
        gripper=[
            "Louse-Flex-Script",
            "Louse-Pad-Weak",
            "Louse-Pad",
            "Louse-Pad-Strong",
        ],
        applied_force=["VerticalForce"],
        scene=["05-Pole-PY"],
    )


def compare_vertical(df):
    boxplot_results(
        df,
        title="Gripper Vertical Performance",
        x_axis_list=[
            "Basic-Prismatic",
            "Basic-Revolute",
            "Finger-Rigid",
            "Finger-Flex-Script",
            "Louse-Flex-Script",
            "Louse-Flex",
            "Louse-Pad",
        ],
        applied_force="VerticalForce",
        scene="05-Pole-PY",
    )


def compare_horizontal(df):
    boxplot_results(
        df,
        title="Gripper Horizontal Performance",
        applied_force="HorizontalForce",
        x_axis_list=[
            "Basic-Prismatic",
            "Basic-Revolute",
            "Finger-Rigid",
            "Finger-Flex-Script",
            "Louse-Flex-Script",
            "Louse-Flex",
            "Louse-Pad",
        ],
        scene="05-Pole-PY",
    )


def average_trials(df):
    scene_list = df["scene"].unique()
    gripper_list = df["gripper"].unique()
    force_list = df["applied_force"].unique()

    data = [
        format_df_from_values(
            average_over_values(df, scene, gripper, applied_force),
            scene=scene,
            gripper=gripper,
            applied_force=applied_force,
        )
        for scene in scene_list
        for gripper in gripper_list
        for applied_force in force_list
    ]

    average_df = pandas.DataFrame(data)

    return average_df


def average_over_values(df, scene, gripper, applied_force):
    df_filtered = filter_df(
        df=df, scene=scene, gripper=gripper, applied_force=applied_force
    )
    mean_series = df_filtered.mean()
    return mean_series["result"]


def filter_df(df, **criteria):
    return df[match_values(df, **criteria)]


def match_values(df, **criteria):
    first_key = next(iter(criteria))
    first_value = criteria.pop(first_key)

    if not isinstance(first_value, list):
        first_value = [
            first_value,
        ]

    comparison_df = df[first_key].isin(first_value)

    if not criteria:  # if all criteria parsed, return
        return comparison_df

    return comparison_df & match_values(df, **criteria)  # otherwise, continue iterating


if __name__ == "__main__":
    results_dir = "/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/results/"
    analyze(results_dir)
