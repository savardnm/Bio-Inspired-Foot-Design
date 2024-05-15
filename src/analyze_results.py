import numpy as np
import matplotlib.pyplot as plt
from parse_results import *


def analyze(results_dir):
    results_df = results_to_df(results_dir)
    # print(results_df)
    print("all results >>>>\n", results_df.to_string(), "\nall results <<<<")
    # average_trials(results_df)
    compare_grippers(results_df)
    compare_weights(results_df)

    plt.show()


def compare_flex_vs_rigid(df):
    average_df = average_trials(df)


def compare_grippers(df):
    compare_vertical(df)
    compare_horizontal(df)


def boxplot_results(df, title, gripper_list = "all", **criteria):
    filtered_df = filter_df(df, **criteria)
    
    if gripper_list == "all":
        gripper_list = filtered_df['gripper'].unique()

    labels = []
    data = []
    for gripper in gripper_list:
        gripper_df = filter_df(filtered_df, gripper=gripper)
        results = gripper_df["result"]
        labels.append(gripper)
        data.append(results)

    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.8], label="gripper")
    plt.title(title)

    labels = ["\n".join(label.split("-")) for label in labels]
    ax.set_xticklabels(labels, rotation="vertical")
    # plt.xticks([], labels, rotation='vertical')
    bp = ax.boxplot(data)



def compare_weights(df):
    compare_finger_weights(df)
    compare_louse_weights(df)


def compare_finger_weights(df):
    boxplot_results(
        df,
        title="Effect of Compliance on Finger Actuator",
        gripper=["Finger-Rigid", "Finger-Flex-Weak", "Finger-Flex", "Finger-Flex-Strong", ],
        applied_force=["VerticalForce"],
        scene=["05-Pole-PY"],
    )


def compare_louse_weights(df):
    boxplot_results(
        df,
        title="Effect of Compliance on Louse Actuator",
        gripper=["Louse-Rigid", "Louse-Pad-Weak", "Louse-Pad", "Louse-Pad-Strong", ],
        applied_force=["VerticalForce"],
        scene=["05-Pole-PY"],
    )

def compare_vertical(df):
    boxplot_results(
        df,
        title="Gripper Vertical Performance",
        gripper_list = [
            "Basic-Prismatic",
            "Basic-Revolute",
            "Finger-Flex",
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
        gripper_list = [
            "Basic-Prismatic",
            "Basic-Revolute",
            "Finger-Flex",
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
            scene,
            gripper,
            applied_force,
            average_over_values(df, scene, gripper, applied_force),
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
        first_value = [first_value,]

    comparison_df = df[first_key].isin(first_value)

    if not criteria:  # if all criteria parsed, return
        return comparison_df

    return comparison_df & match_values(df, **criteria)  # otherwise, continue iterating


if __name__ == "__main__":
    results_dir = "/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/results/"
    analyze(results_dir)
