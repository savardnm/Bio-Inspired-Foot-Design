import numpy as np
import matplotlib.pyplot as plt
from parse_results import *
from copy import deepcopy
import math

from mpl_toolkits.mplot3d import Axes3D  # <--- This is important for 3d plotting


from matplotlib import cbook, cm
from matplotlib.colors import LightSource


def analyze(results_dir):
    results_df = pandas.read_csv(results_dir)
    # print("all results >>>>\n", results_df.to_string(), "\nall results <<<<")

    analyze_final_generation(results_df)

    compare_distributions(results_df)
    compare_generations(results_df)

    plt.show()


def analyze_final_generation(df):
    histogram(
        "result",
        df,
        title="Overall Performance of Final Generation",
        x_axis_title="Overall Performance of Final Generation",
        y_axis_title="Performance $(N^2)$",
    )

    histogram(
        "horizontal_result",
        df,
        title="Normal Performance of Final Generation",
        x_axis_title="Nromal Performance of Final Generation",
        y_axis_title="Grip Strength $(N)$",
    )

    histogram(
        "vertical_result",
        df,
        title="Shear Performance of Final Generation",
        x_axis_title="Shear Performance of Final Generation",
        y_axis_title="Grip Strength $(N)$",
    )


def compare_generations(df):
    constant_filter = {}

    variable_filter_list = [
        ("generation", "all"),
    ]

    multi_boxplot(
        df,
        constant_filter,
        variable_filter_list,
        title="Performance of Generations",
        x_axis_title="Generation",
        y_axis_title="Gripper Performance $(N^2)$",
    )

    multi_boxplot(
        df,
        constant_filter,
        variable_filter_list,
        title="Shear Performance of Generations",
        x_axis_title="Generation",
        y_axis_title="Grip Strength $(N)$",
        value_column="vertical_result",
    )

    multi_boxplot(
        df,
        constant_filter,
        variable_filter_list,
        title="Normal Performance of Generations",
        x_axis_title="Generation",
        y_axis_title="Grip Strength $(N)$",
        value_column="horizontal_result",
    )

    multi_boxplot(
        df,
        constant_filter,
        variable_filter_list,
        title="Pad Size of Generations",
        x_axis_title="Generation",
        y_axis_title="Pad Size",
        value_column="num_pad_units",
    )

    multi_boxplot(
        df,
        constant_filter,
        variable_filter_list,
        title="Pad Strength of Generations",
        x_axis_title="Generation",
        y_axis_title="Pad Strength",
        value_column="pad_strength",
    )

    multi_boxplot(
        df,
        constant_filter,
        variable_filter_list,
        title="Pad Starting Point of Generations",
        x_axis_title="Generation",
        y_axis_title="Starting Point",
        value_column="pad_starting_pos",
    )

    multi_boxplot(
        df,
        constant_filter,
        variable_filter_list,
        title="Curvature Across Generations",
        x_axis_title="Generation",
        y_axis_title="Curvature",
        value_column="curvature",
    )

    multi_boxplot(
        df,
        constant_filter,
        variable_filter_list,
        title="Scale Across Generations",
        x_axis_title="Generation",
        y_axis_title="Scale",
        value_column="scale",
    )


def save_plot(title):
    plots_dir = "/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/results/Plots/"

    plt.savefig(plots_dir + title + ".png")


def compare_distributions(df):
    scatter(
        "pad_strength",
        "num_pad_units",
        df,
        title="Distribution of Pad Size vs Pad Strength in Last Generation",
        x_axis_title="Pad Strength $(N/m)$",
        y_axis_title="Pad Size (Number of Pad Units)",
        condense=True,
    )

    histogram(
        "pad_strength",
        df,
        title="Distribution of Pad Stiffness in Last Generation",
        x_axis_title="Pad Stiffness $(N/m)$",
        y_axis_title="Frequency (%)",
        figsize=(6, 4),
    )

    histogram(
        "pad_starting_pos",
        df,
        title="Distribution of Pad Starting Position in Last Generation",
        x_axis_title="Pad Stiffness $(N/m)$",
        y_axis_title="Frequency (%)",
        figsize=(6, 4),
        draw_mean=False,
        xticks={'ticks':[-1,0,1], 'labels':['bottom', 'center', 'top']}
    )

    histogram(
        "num_pad_units",
        df,
        title="Distribution of Pad Size in Last Generation",
        x_axis_title="Pad Size $(units)$",
        y_axis_title="Frequency",
        figsize=(6, 4),
        draw_mean=False,
    )

    histogram(
        "curvature",
        df,
        title="Distribution of Curvature in Last Generation",
        x_axis_title="Curvature $(N/m)$",
        y_axis_title="Frequency (%)",
        figsize=(6, 4),
    )

    histogram(
        "scale",
        df,
        title="Distribution of Scale in Last Generation",
        x_axis_title="Curvature $(N/m)$",
        y_axis_title="Frequency (%)",
        figsize=(6, 4),
    )


def get_last_generation(df):
    return df.iloc[-1]["generation"]


def get_generation_df(df, generation):
    return df[df["generation"].isin([generation])]


def histogram(var, df, title, x_axis_title, y_axis_title, figsize=(8, 6), draw_mean=True, xticks = None):
    last_generation = get_last_generation(df)
    last_generation_df = get_generation_df(df, last_generation)

    var_df = last_generation_df[var]
    mean = var_df.mean()
    std = var_df.std()

    print(title, "(", mean, std, ")")
    

    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.75])
    plt.title(title)
    plt.xlabel(x_axis_title)
    plt.ylabel(y_axis_title)

    plt.hist(var_df, density=True)

    if xticks:
        plt.xticks(**xticks)

    if draw_mean:
        plt.axvline(var_df.mean(), color='k', linestyle='dashed', linewidth=1)

        min_ylim, max_ylim = plt.ylim()
        plt.text(mean*1.1, max_ylim*0.9, 'Mean: {:.2f}'.format(var_df.mean()))


    save_plot(title)


def scatter(x_axis, y_axis, df, title, x_axis_title, y_axis_title, condense=False):
    last_generation = get_last_generation(df)
    last_generation_df = get_generation_df(df, last_generation)
    x_axis_data = last_generation_df[x_axis]
    y_axis_data = last_generation_df[y_axis]

    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.75])
    plt.title(title)
    plt.xlabel(x_axis_title)
    plt.ylabel(y_axis_title)

    if condense:
        x_y_value_list = last_generation_df.groupby([x_axis, y_axis])

        x_axis_data = []
        y_axis_data = []
        size_data = []

        for name, group in x_y_value_list:
            x_axis_data.append(name[0])
            y_axis_data.append(name[1])
            size_data.append(len(group.index) * 20.0)

        plt.scatter(x_axis_data, y_axis_data, s=size_data)
    else:
        plt.scatter(x_axis_data, y_axis_data)


def get_unique_pairs(df, *axi):
    df.groupby(*axi)


def multi_boxplot(
    df,
    constant_filter,
    variable_filter_list,
    title,
    x_axis_title="",
    y_axis_title="",
    value_column="result",
):
    constant_filter_df = filter_df(df, **constant_filter)

    label_list = []
    data_list = []

    variable_filter_df(
        constant_filter_df,
        data_list,
        label_list,
        variable_filter_list,
        value_column=value_column,
    )

    # print("!", data_list, "\n\n", label_list)

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
        .replace("05-Pole-PY", "Flex Wrist")
        .replace("05-Pole-P", "Rigid Wrist")
        .replace("Louse-Pad-Script", "Louse Claw")
        .replace("Finger-Flex-Script", "Finger Claw")
    )


def variable_filter_df(
    df, data_list, label_list, variable_filter_list, label="", value_column="result"
):
    if not variable_filter_list:
        print("found value column: ", value_column, ": ", df[value_column])
        data_list.append(df[value_column])
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

    # print('all criteria', column, option_list)

    for option in option_list:

        # print('criteria: ', option)
        if int(option) % 5 == 0:
            new_label = str(int(option))
        else:
            new_label = ""

        option_filter = {column: option}

        filtered_df = filter_df(df, **option_filter)

        # print('criteria filtered', filtered_df)

        variable_filter_df(
            filtered_df,
            data_list,
            label_list,
            variable_filter_list,
            new_label,
            value_column=value_column,
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
    ax = fig.add_axes([0.1, 0.25, 0.8, 0.75], label="gripper")
    plt.title(title)

    labels = ["\n".join(label.split("-")) for label in labels]
    ax.set_xticklabels(labels)
    bp = ax.boxplot(data, showfliers=True, showmeans=True, meanline=True)


def boxplot(title, labels, data, x_axis_title="", y_axis_title=""):
    fig = plt.figure(figsize=(10, 4))
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.75])
    plt.title(title)

    ax.set_xticklabels(labels, rotation="vertical")
    plt.xlabel(x_axis_title)
    plt.ylabel(y_axis_title)
    bp = ax.boxplot(data, showfliers=True, showmeans=True)

    plots_dir = "/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/results/Plots/"

    plt.savefig(plots_dir + title + ".png")


# def compare_scenes(df):
#     compare_horizontal_scenes(df)
#     compare_vertical_scenes(df)


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


def average_over_values(df, value_column="result", **criteria):
    # print("averaging over values: ", criteria)
    df_filtered = filter_df(df=df, **criteria)
    mean_series = df_filtered.mean()
    return mean_series[value_column]


def filter_df(df, **criteria):
    if criteria == {}:
        print("no criteria")
        return df

    return df[match_values(df, **criteria)]


def match_values(df, **criteria):
    # print("filtering with criteria: ", criteria)

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
    results_dir = "/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/results/csv/ga_results_100x100.csv"
    analyze(results_dir)
