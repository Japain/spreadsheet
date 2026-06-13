from PySide6.QtWidgets import QDialog, QLabel, QPushButton

from src.ui.dialogs import ConflictDialog


def test_conflict_dialog_lists_filenames(qtbot):
    dialog = ConflictDialog(["alpha.xlsx", "beta.xlsx"])
    qtbot.addWidget(dialog)
    texts = [w.text() for w in dialog.findChildren(QLabel)]
    assert "alpha.xlsx" in texts
    assert "beta.xlsx" in texts


def test_conflict_dialog_cancel_rejects(qtbot):
    dialog = ConflictDialog(["file.xlsx"])
    qtbot.addWidget(dialog)
    btn = next(b for b in dialog.findChildren(QPushButton) if "Cancel" in b.text())
    btn.click()
    assert dialog.result() == QDialog.DialogCode.Rejected


def test_conflict_dialog_overwrite_accepts(qtbot):
    dialog = ConflictDialog(["file.xlsx"])
    qtbot.addWidget(dialog)
    btn = next(b for b in dialog.findChildren(QPushButton) if "Overwrite" in b.text())
    btn.click()
    assert dialog.result() == QDialog.DialogCode.Accepted
