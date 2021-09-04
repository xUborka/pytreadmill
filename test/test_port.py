# from Port import Port
from main_window import Window


def test_empty_init(qtbot):
    # pass
    dummy_window = Window()
    qtbot.addWidget(dummy_window)
    # dummy_port = Port('A', None, None, None)
    assert dummy_window.windowTitle() == 'pyTreadmill'
    # assert True
