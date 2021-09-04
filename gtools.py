import os
import json


class GTools:
    SAVE_FOLDER_PATH = os.getcwd()
    PROJECT_CONFIG_PATH = os.path.join("res", "cfg.json")

    @staticmethod
    def write_to_file(filename, data_list):    # Writes the provided arrays into a csv
        with open(filename, 'w') as output_file:
            output_file.write(','.join(['time', 'velocity', 'Absolute Position', 'Lap#', 'Relative Position', 'Lick\n']))

            for row in data_list:
                output_file.write(str(row) + '\n')

        print(f'Data written to: {filename}\n')

    @staticmethod
    def get_project_config():
        with open(GTools.PROJECT_CONFIG_PATH, "r") as json_file:
            data = json.load(json_file)
        return data

    @staticmethod
    def get_save_folder():
        data = GTools.get_project_config()
        if data["save_folder"] != GTools.SAVE_FOLDER_PATH:
            # In case the project was not initialized before
            GTools.update_save_folder(GTools.SAVE_FOLDER_PATH)
            data = GTools.get_project_config()
        return data['save_folder']

    @staticmethod
    def update_save_folder(path):
        GTools.SAVE_FOLDER_PATH = path
        data = GTools.get_project_config()
        data['save_folder'] = GTools.SAVE_FOLDER_PATH
        with open(GTools.PROJECT_CONFIG_PATH, "w") as json_file:
            json.dump(data, json_file)

    @staticmethod
    def error_message(title, msg):
        print(f'{title} : {msg}')
