import os
import pandas as pd

# setting up global constants
BEHAVIOR_DUPLICATES = {'Social interaction': 'Social contact',
                       'Upside down': 'Upside Down',
                       'Stationary': 'Stationary locomotion',
                       'Wings and scenting': 'Scenting',
                       'Grooming other': ['Grooming-O', 'Grooming- O']}

TARGET_BEHAVIORS = ['Social interaction', 'Active locomotion', 'Stationary',
                    'Wings and scenting', 'Upside down', 'Trophallaxis', 'Grooming other']


class BehaviorData:
    def __init__(self, target_behaviors, behavior_duplicates):
        self.target_behaviors = target_behaviors
        self.behavior_duplicates = behavior_duplicates
        self.cumulative_data = pd.DataFrame()
        self.average_data = pd.DataFrame()
        self.observation_mapping = {}
        self.new_observation_id = 1

    def integrate_new_data(self, new_data, treatment_condition):
        """
        Merge the data from the input file with the existing data
        :param new_data: New data to merge
        :param treatment_condition: Treatment condition
        """
        merged_data = self.merge_duplicate_rows(new_data, 'Behavior')
        self.update_observation_ids(merged_data)
        self.process_average_data(merged_data, treatment_condition)
        self.process_cumulative_data(merged_data, treatment_condition)

    def merge_duplicate_rows(self, df, column):
        """
        Merge rows with duplicate values in the specified column
        :param df: pandas DataFrame
        :param column: column to merge rows on
        :return: pandas DataFrame
        """
        for key, value in self.behavior_duplicates.items():
            df[column].replace(value, key, inplace=True)
        return df

    def update_observation_ids(self, df):
        """
        Replace the observation id with a new id
        :param df: pandas DataFrame
        """
        for observation_id in df['Observation id'].unique():
            if observation_id not in self.observation_mapping:
                self.observation_mapping[observation_id] = f'{self.new_observation_id:03}'
                self.new_observation_id += 1
        df['Observation id'] = df['Observation id'].map(self.observation_mapping)

    def process_cumulative_data(self, new_data, treatment_condition):
        """
        Process the cumulative data and clean it
        :param new_data: pandas DataFrame
        :param treatment_condition: treatment condition
        """
        new_df = new_data[['Observation id', 'Behavior', 'Duration (s)']]
        new_df = self.update_trophallaxis_durations(new_df)
        new_df = new_df.groupby(['Observation id', 'Behavior'])['Duration (s)'].sum().reset_index()
        new_df['Treatment Condition'] = treatment_condition
        cleaned_df = new_df.pivot_table(index=['Observation id', 'Treatment Condition'], columns='Behavior',
                                        values='Duration (s)').reset_index()
        cleaned_df = cleaned_df.fillna(0)
        self.cumulative_data = pd.concat([self.cumulative_data, cleaned_df], ignore_index=True)

    def process_average_data(self, new_data, treatment_condition):
        """
        Process the average data and clean it
        :param new_data: pandas DataFrame
        :param treatment_condition: treatment condition
        """
        # calculate the total duration of each behavior
        duration_dict = self.calculate_total_durations(new_data)

        # calculate the mean duration of each behavior
        mean_durations = self.calculate_mean_values(duration_dict, new_data)

        # count the total number of each behavior
        state_counts = self.calculate_behavior_counts(new_data)

        # calculate the mean number of each behavior
        mean_counts = self.calculate_mean_values(state_counts, new_data)

        # calculate the total duration of trophallaxis
        trophallaxis_duration = self.calculate_trophallaxis_duration(new_data)

        # calculate the mean duration of trophallaxis
        mean_trophallaxis = self.calculate_mean_values(trophallaxis_duration, new_data)


        duration_dict['Trophallaxis'] = trophallaxis_duration
        mean_durations['Trophallaxis'] = mean_trophallaxis

        # create a temporary DataFrame to store the average data
        temp_df = self.create_temp_dataframe(treatment_condition, [duration_dict, mean_durations, state_counts, mean_counts])
        self.average_data = pd.concat([self.average_data, temp_df], ignore_index=True)

    def create_temp_dataframe(self, treatment_condition, info):
        """
        Create a temporary DataFrame to store the average data
        :param treatment_condition: the treatment condition
        :param info: extracted information
        :return: pandas DataFrame
        """
        temp_df = pd.DataFrame(
            {'Treatment Condition': treatment_condition, 'Behavior category': self.target_behaviors})
        labels = ['Total duration (s)', 'Mean duration (s)', 'Total state count', 'Mean state count']
        for i, data in enumerate(info):
            temp = pd.DataFrame({'Behavior category': data.keys(), labels[i]: data.values()})
            temp_df = temp_df.merge(temp, how='outer', on='Behavior category')
        return temp_df

    def calculate_total_durations(self, df):
        """
        Calculate the total duration of each behavior
        :param df: pandas DataFrame
        :return: dictionary of total durations
        """
        states = df["Behavior"].unique()
        duration_dict = {state: 0 for state in states}
        for index, row in df.iterrows():
            duration_dict[row["Behavior"]] += row["Duration (s)"]
        return duration_dict

    def calculate_behavior_counts(self, df):
        """
        Calculate the total count of each behavior
        :param df: pandas DataFrame
        :return: dictionary of total counts
        """
        states = df["Behavior"].unique()
        count_dict = {state: 0 for state in states}
        for index, row in df.iterrows():
            count_dict[row["Behavior"]] += 1
        return count_dict

    def calculate_trophallaxis_duration(self, df):
        """
        Calculate the total duration of trophallaxis during social interaction
        :param df: pandas DataFrame
        :return: duration of trophallaxis
        """
        trophDuration = 0

        for index, row in df.iterrows():
            if row["Behavior"] != "Trophallaxis":
                continue

            temp = index - 1
            while True:
                tempRow = df.iloc[temp]
                if tempRow["Behavior"] == "Social interaction":
                    trophDuration += tempRow["Duration (s)"]
                    break
                temp = temp - 1

        return trophDuration

    def update_trophallaxis_durations(self, df):
        """
        Replace the duration of trophallaxis with the duration of social interaction
        :param df: pandas DataFrame
        :return: edited DataFrame
        """
        for index, row in df.iterrows():
            if row["Behavior"] != "Trophallaxis":
                continue

            temp = index - 1
            while True:
                tempRow = df.iloc[temp]
                if tempRow["Behavior"] == "Social interaction":
                    df.at[index, 'Duration (s)'] = tempRow["Duration (s)"]
                    break
                temp = temp - 1

        return df

    def calculate_mean_values(self, maybe_dict, df):
        """
        Calculate the mean value of the dictionary
        :param maybe_dict: a dictionary or float
        :param df: pandas DataFrame
        :return: the mean value
        """
        temp = maybe_dict.copy()
        number_of_observations = df["Observation id"].nunique()
        if isinstance(maybe_dict, dict):
            for key, value in temp.items():
                temp[key] = temp[key] / number_of_observations
            return temp
        elif isinstance(maybe_dict, float):
            return temp / number_of_observations


def process_files(target_dir, all_grouped_data):
    """
    Process all the files in the target directory
    :param target_dir: folder with input files
    :param all_grouped_data: class instance to store the grouped data
    """
    treatmeant = 1
    for filename in os.listdir(target_dir):
        treatment_condition = treatmeant
        treatmeant += 1
        df = pd.read_excel(os.path.join(target_dir, filename))
        all_grouped_data.integrate_new_data(df, treatment_condition)


def export_data(target_dir, file_names, data_frames):
    """
    Export the grouped data to Excel files
    :param target_dir: path for output files
    :param file_names: names of the output files
    :param data_frames: pandas DataFrames to export
    """
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    for i, file_name in enumerate(file_names):
        output_file = os.path.join(target_dir, file_name)
        if os.path.exists(output_file):
            os.remove(output_file)
        data_frames[i].to_excel(output_file, index=False)
    print(f"Grouped data saved to {output_file}")


def main():
    """
    Main function to process the data
    """
    input_dir = "./InputSheets"
    all_grouped_data = BehaviorData(TARGET_BEHAVIORS, BEHAVIOR_DUPLICATES)
    process_files(input_dir, all_grouped_data)
    data_frames_to_export = [all_grouped_data.cumulative_data, all_grouped_data.average_data]
    output_file_names = ["all_grouped_data.xlsx", "mean_data.xlsx"]
    output_dir = "OutputSheets"
    export_data(output_dir, output_file_names, data_frames_to_export)


if __name__ == "__main__":
    main()
