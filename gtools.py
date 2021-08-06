# lehetne ide csoportosítani a fileműveleteket inkább. Femtoheader felesleges, nem használjuk
import os

SAVE_FOLDER_PATH = str(os.getcwd() + '/res/def_save_folder.txt')


def write2File(filename, time_list, vel_list, abs_pos_list, lap_list, rel_pos_list, lick_list, delimiter=","):	# Writes the provided arrays into a csv
	with open(filename, 'w') as f:
		f.write(delimiter.join(['time', 'velocity', 'Absolute Position', 'Lap#', 'Relative Position', 'Lick\n']))
	
		for row in zip(time_list, vel_list, abs_pos_list, lap_list, rel_pos_list, lick_list):
			f.write(delimiter.join(row)+'\n')

	print(f'Data written to: {filename}\n')


def updateSaveFolder(path):
	with open(SAVE_FOLDER_PATH, 'w') as file:
		file.write(path)


def getSaveFolder():
	return SAVE_FOLDER_PATH

def error_message(title,msg):
	#from tkinter import messagebox
	#messagebox.showerror(title,msg)
	from PyQt5.QtWidgets import QMessageBox
	Warning