# lehetne ide csoportosítani a fileműveleteket inkább. Femtoheader felesleges, nem használjuk
import os


class GTools:
    SAVE_FOLDER_PATH = os.path.join(os.getcwd(), 'res', 'def_save_folder.txt')
    
    @staticmethod
    def write2File(filename, time_list, vel_list, abs_pos_list, lap_list, rel_pos_list, lick_list, delimiter=","):    # Writes the provided arrays into a csv
        with open(filename, 'w') as f:
            f.write(delimiter.join(['time', 'velocity', 'Absolute Position', 'Lap#', 'Relative Position', 'Lick\n']))
        
            for row in zip(time_list, vel_list, abs_pos_list, lap_list, rel_pos_list, lick_list):
                f.write(delimiter.join(row)+'\n')

        print(f'Data written to: {filename}\n')

    @staticmethod
    def updateSaveFolder(path):
        with open(GTools.SAVE_FOLDER_PATH, 'w') as file:
            file.write(path)

    @staticmethod
    def error_message(title,msg):
        print(f'{title} : {msg}')