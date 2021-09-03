import os


class GTools:
    SAVE_FOLDER_PATH = str(os.getcwd() + '/res/def_save_folder.txt')

    @staticmethod
    def write2File(filename, data_list):    # Writes the provided arrays into a csv
        with open(filename, 'w') as f:
            f.write(','.join(['time', 'velocity', 'Absolute Position', 'Lap#', 'Relative Position', 'Lick\n']))

            for row in data_list:
                f.write(str(row) + '\n')

        print(f'Data written to: {filename}\n')

    @staticmethod
    def updateSaveFolder(path):
        with open(GTools.SAVE_FOLDER_PATH, 'w') as file:
            file.write(path)

    @staticmethod
    def error_message(title, msg):
        print(f'{title} : {msg}')

    def getSaveFolder():
        if os.path.exists(GTools.SAVE_FOLDER_PATH):
            with open(GTools.SAVE_FOLDER_PATH, 'r') as file:
                saveFolder = file.read()
                if os.path.isdir(saveFolder):
                    return saveFolder
                else:
                    return ""
        else:
            return ""
