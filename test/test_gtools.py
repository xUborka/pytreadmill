import os
import json
import unittest
from model.gtools import GTools


class TestPositionTrigerData(unittest.TestCase):
    def test_get_project_config(self):
        # Init
        GTools.PROJECT_CONFIG_PATH = os.path.join("test", "test_config.json")
        dummy_test_data = {'save_folder': 'path_to_folder', 'other_config': 'config_value'}
        with open(GTools.PROJECT_CONFIG_PATH, "w") as test_config:
            json.dump(dummy_test_data, test_config)

        # Function Under Test
        cfg = GTools.get_project_config()

        # Test
        assert dummy_test_data == cfg

    def test_get_save_folder_not_equal_paths(self):
        # Init
        GTools.SAVE_FOLDER_PATH = "valid_value"
        GTools.PROJECT_CONFIG_PATH = os.path.join("test", "test_config.json")
        dummy_test_data = {'save_folder': 'invalid_value', 'other_config': 'config_value'}
        with open(GTools.PROJECT_CONFIG_PATH, "w") as test_config:
            json.dump(dummy_test_data, test_config)

        # Function Under Test
        cfg = GTools.get_save_folder()

        # Test
        assert cfg == 'valid_value'

    def test_get_save_folder_equal_paths(self):
        # Init
        GTools.SAVE_FOLDER_PATH = "test_value"
        GTools.PROJECT_CONFIG_PATH = os.path.join("test", "test_config.json")
        dummy_test_data = {'save_folder': 'test_value', 'other_config': 'config_value'}
        with open(GTools.PROJECT_CONFIG_PATH, "w") as test_config:
            json.dump(dummy_test_data, test_config)

        # Function Under Test
        cfg = GTools.get_save_folder()

        # Test
        assert cfg == 'test_value'

    def test_update_save_folder(self):
        # Init
        GTools.SAVE_FOLDER_PATH = "init_value"

        # Function Under Test
        GTools.update_save_folder("updated_value")

        # Test
        cfg = GTools.get_save_folder()
        assert GTools.SAVE_FOLDER_PATH == "updated_value"
        assert cfg == "updated_value"
