import numpy as np
import matplotlib.pyplot as plt
from parse_results import *
from copy import deepcopy
import math

from mpl_toolkits.mplot3d import Axes3D  # <--- This is important for 3d plotting


from matplotlib import cbook, cm
from matplotlib.colors import LightSource


def analyze(results_dir):
    results_df = results_to_df(results_dir)
    # print(results_df)
    print("all results >>>>\n", results_df.to_string(), "\nall results <<<<")
    df_to_csv(results_df, results_dir + "csv/results.csv", overwrite=True)
    # average_trials(results_df)
    # compare_grippers(results_df)
    # compare_weights(results_df)
    # compare_scenes(results_df)
    compare_louse_3d(results_df)
    compare_finger_flex_effect(results_df)
    compare_louse_flex_effect(results_df)
    compare_louse_pad_size_effect(results_df)

    plt.show()


def compare_flex_vs_rigid(df):
    average_df = average_trials(df)


def compare_grippers(df):
    compare_vertical(df)
    compare_horizontal(df)


def force_boxplot_series(
    df,
    gripper,
    variable_name,
    base_title,
    x_axis_title,
    y_axis_title,
    constant_filter={},
    variable_values="all",
):
    base_constant_filter = {
        "gripper": gripper,
        "scene": "05-Pole-PY",
    }

    constant_filter = {**base_constant_filter, **constant_filter}

    force_option_list = ["VerticalForce", "HorizontalForce"]

    variable_filter_list = [
        (variable_name, variable_values),
    ]

    for force_option in force_option_list:
        new_filter = deepcopy(constant_filter)
        new_filter["applied_force"] = force_option
        multi_boxplot(
            df,
            new_filter,
            variable_filter_list,
            title=base_title + " " + format_label(force_option),
            x_axis_title=x_axis_title,
            y_axis_title=y_axis_title,
        )


def compare_louse_flex_effect(df):
    constant_filter = {
        "num_pad_units": "8",
    }

    force_boxplot_series(
        df,
        gripper="Louse-Pad-Script",
        constant_filter=constant_filter,
        variable_name="pad_strength",
        base_title="Effect of Flex Values on Louse Gripper",
        x_axis_title="Pad Stiffness (N/m)",
        y_axis_title="Grip Force (N)",
    )

def compare_louse_pad_size_effect(df):
    constant_filter = {
        "pad_strength": "45",
    }
    force_boxplot_series(
        df,
        gripper="Louse-Pad-Script",
        constant_filter=constant_filter,
        variable_name="num_pad_units",
        base_title="Effect of Pad Size on Louse Gripper",
        x_axis_title="Pad Size (Units)",
        y_axis_title="Grip Force (N)",
    )


def compare_finger_flex_effect(df):
    force_boxplot_series(
        df,
        gripper="Finger-Flex-Script",
        variable_name="flex_strength",
        base_title="Effect of Flex Values on Finger Gripper",
        x_axis_title="Palm Flex Stiffness (Nm/rad)",
        y_axis_title="Grip Force (N)",
    )

def compare_louse_3d(df):
    criteria = {
        "gripper": "Louse-Pad-Script",
        "scene": "05-Pole-PY",
        "applied_force": "VerticalForce",
    }
    louse_df = filter_df(df, **criteria)

    pprint(louse_df)

    num_pad_values = list(map(int, louse_df["num_pad_units"].unique()))
    pad_str_values = list(map(int, louse_df["pad_strength"].unique()))

    num_pad_values = sorted(num_pad_values, key=lambda opt: int(opt))
    pad_str_values = sorted(pad_str_values, key=lambda opt: int(opt))
    # pad_str_values = pad_str_values[0:-2]

    str_average_list = [
        average_over_values(df, pad_strength=pad_strength, num_pad_units=num_pad_units)
        for pad_strength in pad_str_values
        for num_pad_units in num_pad_values
    ]

    str_average_list = [0 if math.isnan(value) else value for value in str_average_list]
    str_average_list = np.array(str_average_list).reshape(
        (len(pad_str_values), len(num_pad_values))
    )

    num_pad_values, pad_str_values = np.meshgrid(num_pad_values, pad_str_values)

    # Set up plot
    fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))
    ax.set_xlabel("Pad Size (Number of Units)")
    ax.set_ylabel("Pad Stiffness (N/m)")
    ax.set_zlabel("Grip Force (N)")

    surf = ax.plot_surface(
        np.array(num_pad_values),
        np.array(pad_str_values),
        str_average_list,
        cmap="inferno",
        rstride=1,
        cstride=1,
    )


def multi_boxplot(
    df, constant_filter, variable_filter_list, title, x_axis_title="", y_axis_title=""
):
    constant_filter_df = filter_df(df, **constant_filter)

    label_list = []
    data_list = []

    variable_filter_df(constant_filter_df, data_list, label_list, variable_filter_list)

    boxplot(
        title=title,
        labels=label_list,
        data=data_list,
        x_axis_title=x_axis_title,
        y_axis_title=y_axis_title,
    )


def format_label(label):
    return (
        label.replace("VerticalForce", "Shear Force")
        .replace("HorizontalForce", "Normal Force")
        .replace("05-Pole-PY", "Wrist Horiztonal Flex")
        .replace("05-Pole-P", "Wrist Horiztonal Rigid")
    )


def variable_filter_df(df, data_list, label_list, variable_filter_list, label=""):
    if not variable_filter_list:
        data_list.append(df["result"])
        label_list.append(format_label(label))
        return

    variable_filter_list = deepcopy(variable_filter_list)
    column, option_list = variable_filter_list.pop(0)

    if option_list == "all":
        option_list = df[column].unique()

    try:
        option_list = sorted(option_list, key=lambda opt: int(opt))
    except:
        pass

    for option in option_list:
        new_label = label + "\n" + str(option)

        option_filter = {column: option}

        filtered_df = filter_df(df, **option_filter)

        variable_filter_df(
            filtered_df, data_list, label_list, variable_filter_list, new_label
        )


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
    ax.set_xticklabels(labels)
    bp = ax.boxplot(data, showfliers=False, showmeans=True, meanline=True)


def boxplot(title, labels, data, x_axis_title="", y_axis_title=""):
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.75])
    plt.title(title)

    ax.set_xticklabels(labels, rotation="vertical")
    plt.xlabel(x_axis_title)
    plt.ylabel(y_axis_title)
    bp = ax.boxplot(data, showfliers=False, showmeans=True)


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
            average_over_values(
                df, scene=scene, gripper=gripper, applied_force=applied_force
            ),
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


def average_over_values(df, **criteria):
    # print("averaging over values: ", criteria)
    df_filtered = filter_df(df=df, **criteria)
    mean_series = df_filtered.mean()
    return mean_series["result"]


def filter_df(df, **criteria):
    return df[match_values(df, **criteria)]


def match_values(df, **criteria):
    first_key = next(iter(criteria))
    first_value = str(criteria.pop(first_key))

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
