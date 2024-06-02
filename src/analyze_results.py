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
    # df_to_csv(results_df, results_dir + "csv/results.csv", overwrite=True)
    compare_louse_3d(results_df)
    compare_finger_flex_effect(results_df)
    compare_louse_flex_effect(results_df)
    compare_louse_pad_size_effect(results_df)
    compare_scenes(results_df)
    get_original_generation(results_df)

    plt.show()


def compare_flex_vs_rigid(df):
    average_df = average_trials(df)


def compare_grippers(df):
    compare_vertical(df)
    compare_horizontal(df)

def compare_scenes(df):
    # constant_filter = {
    #     "num_pad_units": [-1, 8],
    #     "pad_strength": [-1, 45],
    #     "flex_strength": [-1, 45],
    # }
    constant_filter = {}
    
    variable_filter_list = [
        ('gripper', 'all'),
        ('scene', ['05-Pole-PY', '05-Pole-P']),
    ]

    force_option_list = ["VerticalForce", "HorizontalForce"]

    for force_option in force_option_list:
        new_filter = deepcopy(constant_filter)
        new_filter["applied_force"] = force_option
        print("new filter: ", new_filter, "\n<<<<<< new filter")
        print("variable_filter_list: ", variable_filter_list, "\n<<<<<< variable_filter_list")
        multi_boxplot(
            df,
            new_filter,
            variable_filter_list,
            title="Effect of Y Axis Wrist Flex" + " " + format_label(force_option),
            x_axis_title="Scenario",
            y_axis_title="Grip Strength (N)",
        )

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
        base_title="Effect of Flex Values on Hook-Claw Gripper",
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
        base_title="Effect of Pad Size on Hook-Claw Gripper",
        x_axis_title="Pad Size (Units)",
        y_axis_title="Grip Force (N)",
    )


def compare_finger_flex_effect(df):
    force_boxplot_series(
        df,
        gripper="Finger-Flex-Script",
        variable_name="flex_strength",
        base_title="Effect of Flex Values on Finger-Claw Gripper",
        x_axis_title="Palm Flex Stiffness (Nm/rad)",
        y_axis_title="Grip Force (N)",
    )

def get_original_generation(df):
    criteria = {
        "gripper": "Louse-Pad-Script",
        "scene": "05-Pole-PY",
    }
    louse_df = filter_df(df, **criteria)

    for pad_strength in louse_df["pad_strength"].unique():
        pad_criteria = {
            'pad_strength': pad_strength
        }

        print("\nPS", pad_strength, "==============")
        pad_df = filter_df(louse_df, **pad_criteria)

        normal_criteria = {
            "applied_force": "HorizontalForce",
        }
        normal_df = filter_df(pad_df, **normal_criteria)

        shear_criteria = {
            "applied_force": "VerticalForce",
        }
        shear_df = filter_df(pad_df, **shear_criteria)

        normal_results = normal_df['result']
        shear_results = shear_df['result']

        normal_mean = normal_results.mean()
        shear_mean = shear_results.mean()
        overall_mean = normal_mean * shear_mean
        
        print("original Gripper Performance:\n",
            "\nNormal Performance:\t", normal_mean,
            "\nShear Perforamnce:\t", shear_mean,
            "\nOverall_Performance:\t", overall_mean)


def compare_louse_3d(df):
    criteria = {
        "gripper": "Louse-Pad-Script",
        "scene": "05-Pole-PY",
        "applied_force": "VerticalForce",
    }
    louse_df = filter_df(df, **criteria)

    # pprint(louse_df)

    num_pad_values = list(map(int, louse_df["num_pad_units"].unique()))
    pad_str_values = list(map(int, louse_df["pad_strength"].unique()))


    num_pad_values = sorted(num_pad_values, key=lambda opt: int(opt))
    pad_str_values = sorted(pad_str_values, key=lambda opt: int(opt))
    # pad_str_values = pad_str_values[0:-2]
    # num_pad_values = num_pad_values[1:]

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
    ax.view_init(elev=25., azim=-135.)


    title = "Combined Effect of Pad Size and Pad Stiffness on Grip Strength"
    plt.title(title)

    surf = ax.plot_surface(
        np.array(num_pad_values),
        np.array(pad_str_values),
        str_average_list,
        cmap="inferno",
        rstride=1,
        cstride=1,
    )

    save_fig(title)


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
        .replace("05-Pole-PY", "Flex Wrist")
        .replace("05-Pole-P", "Rigid Wrist")
        .replace("Louse-Pad-Script", "Louse Claw")
        .replace("Finger-Flex-Script", "Finger Claw")
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
    ax = fig.add_axes([0.1, 0.25, 0.8, 0.75], label="gripper")
    plt.title(title)

    labels = ["\n".join(label.split("-")) for label in labels]
    ax.set_xticklabels(labels)
    bp = ax.boxplot(data, showfliers=False, showmeans=True, meanline=True)


def boxplot(title, labels, data, x_axis_title="", y_axis_title=""):
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_axes([0.15, 0.25, 0.75, 0.65])
    plt.title(title)

    ax.set_xticklabels(labels, rotation="vertical")
    plt.xlabel(x_axis_title)
    plt.ylabel(y_axis_title)
    bp = ax.boxplot(data, showfliers=False, showmeans=True)

    save_fig(title)

def save_fig(title):
    plots_dir = "/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/results/Plots/"
    plt.savefig(plots_dir + title + ".png")


# def compare_scenes(df):
#     compare_horizontal_scenes(df)
#     compare_vertical_scenes(df)


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
    print("===//\n", df_filtered, "\n//===")
    # mean_series = df_filtered.mean()
    # return mean_series["result"]
    return df_filtered['result'].mean()


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
