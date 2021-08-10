import unittest
from Port import Port
from pyTreadmill import Window


def test_empty_init(qtbot):
    # pass
    dummy_window = Window()
    dummy_window.show()
    qtbot.addWidget(dummy_window)
    # dummy_port = Port('A', None, None, None)