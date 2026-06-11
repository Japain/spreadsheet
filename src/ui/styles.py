STYLESHEET = """
QMainWindow, QWidget#central {
    background-color: #f4f5f9;
}

QWidget#card {
    background-color: #ffffff;
    border: 1px solid #ebebeb;
    border-radius: 8px;
}

QWidget#sidebar {
    background-color: #f5f6fa;
}

QPushButton#primary {
    background-color: #4b6bdf;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
}

QPushButton#primary:hover {
    background-color: #3a56c4;
}

QPushButton#primary:disabled {
    background-color: #a0aee8;
}

QLabel {
    color: #1b1d22;
}

QLabel#secondary {
    color: #6b7080;
}

QLabel#monospace {
    font-family: "Cascadia Mono", Consolas, monospace;
}

QLabel#pill_success {
    background-color: #dff2e4;
    color: #2a7a48;
    border-radius: 10px;
    padding: 2px 8px;
}

QLabel#pill_skipped {
    background-color: #fdf3d0;
    color: #7a5c00;
    border-radius: 10px;
    padding: 2px 8px;
}

QLabel#pill_error {
    background-color: #fde8e4;
    color: #8c2a1c;
    border-radius: 10px;
    padding: 2px 8px;
}

QLabel#tab_chip {
    background-color: #ebebeb;
    color: #1b1d22;
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 11px;
}

QPushButton#nav_item {
    text-align: left;
    padding: 8px 12px;
    border: none;
    border-radius: 6px;
    color: #1b1d22;
    background: transparent;
}

QPushButton#nav_item:hover {
    background: #ebebeb;
}

QPushButton#nav_item[active=true] {
    background: #e8ecfc;
    color: #4b6bdf;
    font-weight: bold;
}

QPushButton#remove_workbook_btn {
    color: #c42b1c;
    background: transparent;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
}

QPushButton#remove_workbook_btn:hover {
    background: rgba(196, 43, 28, 0.08);
}

QPushButton#remove_mapping_btn {
    color: #c42b1c;
    background: transparent;
    border: none;
    border-radius: 4px;
}

QPushButton#remove_mapping_btn:hover {
    background: rgba(196, 43, 28, 0.08);
}

QPushButton#remove_mapping_btn:disabled {
    color: rgba(196, 43, 28, 0.35);
}
"""
