# from Port import Port
from pytreadmill import Window


def test_empty_init(qtbot):
    # pass
    dummy_window = Window()
    qtbot.addWidget(dummy_window)
    # dummy_port = Port('A', None, None, None)
    assert dummy_window.windowTitle() == 'pyTreadmill'
    # assert True
