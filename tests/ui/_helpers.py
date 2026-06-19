"""Shared test helpers for UI tests."""


def _make_confirm_msg_box():
    """QMessageBox stub whose clickedButton() returns the Reset button (index 1)."""
    class FakeMessageBox:
        def __init__(self, parent=None):
            self._buttons = []
            self._clicked = None

        def setWindowTitle(self, t): pass

        def setText(self, t): pass

        def addButton(self, *args):
            btn = object()
            self._buttons.append(btn)
            return btn

        def setDefaultButton(self, btn): pass

        def exec(self):
            self._clicked = self._buttons[1]  # second addButton call = Reset

        def clickedButton(self):
            return self._clicked

    return FakeMessageBox


def _make_cancel_msg_box():
    """QMessageBox stub whose clickedButton() returns the Cancel button (index 0)."""
    class FakeMessageBox:
        def __init__(self, parent=None):
            self._buttons = []
            self._clicked = None

        def setWindowTitle(self, t): pass

        def setText(self, t): pass

        def addButton(self, *args):
            btn = object()
            self._buttons.append(btn)
            return btn

        def setDefaultButton(self, btn): pass

        def exec(self):
            self._clicked = self._buttons[0]  # first addButton call = Cancel

        def clickedButton(self):
            return self._clicked

    return FakeMessageBox
