import sys
import pandas



def combine_csv(source_path_list):
    combined_df = pandas.read_csv(source_path_list[0])

    print(source_path_list, " >> ")

    for source_path in source_path_list[1:]:
        last_generation = combined_df.iloc[-1]['generation']
        print("last generation: ", last_generation, "appending", source_path)
        source_df = pandas.read_csv(source_path)
        source_df['generation'] += (last_generation + 1)
        combined_df = pandas.concat([combined_df, source_df], ignore_index=True)

    return combined_df

if __name__ == '__main__':
    destination_path = sys.argv[1]
    source_path_list = sys.argv[2:]

    combined_df = combine_csv(source_path_list)
    combined_df.to_csv(destination_path)