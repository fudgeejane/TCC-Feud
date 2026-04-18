from typing import Callable, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit,
    QPushButton, QHBoxLayout, QLineEdit, QScrollArea, QWidget, QSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect

# Shared dark modal style used by all team-related dialogs
STYLE = """
QDialog {
    border: 1px solid rgba(125, 211, 252, 0.28);
    border-radius: 12px;
    background: #061128;
}
QWidget {
    background: transparent;
}
QLabel {
    color: #e2e8f0;
    font-size: 11pt;
}
QLabel#headerTitle {
    font-weight: 700;
    font-size: 12pt;
    color: #f8fafc;
}
QLineEdit, QSpinBox {
    padding: 9px;
    border-radius: 10px;
    background: #f8fafc;
    color: #0f172a;
    border: 1px solid #cbd5e1;
}
QLineEdit:focus, QSpinBox:focus {
    border: 2px solid #0ea5e9;
}
QPushButton {
    border-radius: 8px;
    padding: 8px 12px;
}
QPushButton#createBtn {
    background: #0f766e;
    color: white;
    font-weight: 600;
}
QPushButton#createBtn:hover {
    background: #0d9488;
}
QPushButton#cancelBtn {
    background: #e2e8f0;
    color: #1e293b;
}
QPushButton#cancelBtn:hover {
    background: #cbd5e1;
}
QPushButton#dangerBtn {
    background: #be123c;
    color: white;
}
QPushButton#dangerBtn:hover {
    background: #e11d48;
}
"""


def open_add_team_modal(parent, on_create: Optional[Callable[[dict], None]] = None):
    """Open modal to add a new team"""
    dlg = QDialog(parent)
    dlg.setWindowTitle("Add Team")
    dlg.setModal(True)
    dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
    dlg.setWindowFlag(Qt.FramelessWindowHint, True)
    dlg.setStyleSheet(STYLE)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)

    header = QHBoxLayout()
    title_lbl = QLabel("Add Team")
    title_lbl.setObjectName("headerTitle")
    header.addWidget(title_lbl)
    header.addStretch()
    layout.addLayout(header)

    layout.addWidget(QLabel("Team Name"))
    team_name_entry = QLineEdit()
    team_name_entry.setPlaceholderText("Enter team name...")
    layout.addWidget(team_name_entry)

    layout.addWidget(QLabel("Member 1"))
    member1_entry = QLineEdit()
    member1_entry.setPlaceholderText("Enter member name...")
    layout.addWidget(member1_entry)

    layout.addWidget(QLabel("Member 2"))
    member2_entry = QLineEdit()
    member2_entry.setPlaceholderText("Enter member name...")
    layout.addWidget(member2_entry)

    layout.addWidget(QLabel("Member 3"))
    member3_entry = QLineEdit()
    member3_entry.setPlaceholderText("Enter member name...")
    layout.addWidget(member3_entry)

    layout.addWidget(QLabel("Member 4"))
    member4_entry = QLineEdit()
    member4_entry.setPlaceholderText("Enter member name...")
    layout.addWidget(member4_entry)

    btns = QHBoxLayout()
    cancel_btn = QPushButton("Cancel")
    create_btn = QPushButton("Add Team")
    cancel_btn.setObjectName("cancelBtn")
    create_btn.setObjectName("createBtn")
    cancel_btn.setFixedHeight(32)
    create_btn.setFixedHeight(32)
    btns.addWidget(cancel_btn)
    btns.addWidget(create_btn)
    layout.addLayout(btns)

    def on_create_click():
        name = team_name_entry.text().strip()
        member1 = member1_entry.text().strip()
        member2 = member2_entry.text().strip()
        member3 = member3_entry.text().strip()
        member4 = member4_entry.text().strip()
        if not name:
            err = QDialog(dlg)
            err.setWindowTitle("Validation")
            err_layout = QVBoxLayout(err)
            err_layout.addWidget(QLabel("Please enter a team name."))
            okb = QPushButton("OK")
            okb.setObjectName("okBtn")
            okb.clicked.connect(err.accept)
            err_layout.addWidget(okb)
            err.exec()
            return
        members = [m for m in [member1, member2, member3, member4] if m]
        if len(members) != 4:
            err = QDialog(dlg)
            err.setWindowTitle("Validation")
            err_layout = QVBoxLayout(err)
            err_layout.addWidget(QLabel("Please enter exactly 4 members."))
            okb = QPushButton("OK")
            okb.setObjectName("okBtn")
            okb.clicked.connect(err.accept)
            err_layout.addWidget(okb)
            err.exec()
            return
        payload = {
            "name": name,
            "members": members
        }
        dlg.accept()
        if on_create:
            on_create(payload)

    create_btn.clicked.connect(on_create_click)
    cancel_btn.clicked.connect(dlg.reject)

    dlg.setMinimumWidth(380)
    dlg.adjustSize()
    dlg.exec()


def open_edit_team_modal(parent, team_name: str, members: list, on_save: Optional[Callable[[dict], None]] = None):
    """Open modal to edit a team"""
    dlg = QDialog(parent)
    dlg.setWindowTitle("Edit Team")
    dlg.setModal(True)
    dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
    dlg.setWindowFlag(Qt.FramelessWindowHint, True)
    dlg.setStyleSheet(STYLE)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)

    header = QHBoxLayout()
    title_lbl = QLabel("Edit Team")
    title_lbl.setObjectName("headerTitle")
    header.addWidget(title_lbl)
    header.addStretch()
    layout.addLayout(header)

    layout.addWidget(QLabel("Team Name"))
    team_name_entry = QLineEdit()
    team_name_entry.setText(team_name)
    layout.addWidget(team_name_entry)

    layout.addWidget(QLabel("Member 1"))
    member1_entry = QLineEdit()
    member1_entry.setText(members[0] if len(members) > 0 else "")
    layout.addWidget(member1_entry)

    layout.addWidget(QLabel("Member 2"))
    member2_entry = QLineEdit()
    member2_entry.setText(members[1] if len(members) > 1 else "")
    layout.addWidget(member2_entry)

    layout.addWidget(QLabel("Member 3"))
    member3_entry = QLineEdit()
    member3_entry.setText(members[2] if len(members) > 2 else "")
    layout.addWidget(member3_entry)

    layout.addWidget(QLabel("Member 4"))
    member4_entry = QLineEdit()
    member4_entry.setText(members[3] if len(members) > 3 else "")
    layout.addWidget(member4_entry)

    btns = QHBoxLayout()
    cancel_btn = QPushButton("Cancel")
    save_btn = QPushButton("Save")
    cancel_btn.setObjectName("cancelBtn")
    save_btn.setObjectName("createBtn")
    cancel_btn.setFixedHeight(32)
    save_btn.setFixedHeight(32)
    btns.addWidget(cancel_btn)
    btns.addWidget(save_btn)
    layout.addLayout(btns)

    def on_save_click():
        name = team_name_entry.text().strip()
        member1 = member1_entry.text().strip()
        member2 = member2_entry.text().strip()
        member3 = member3_entry.text().strip()
        member4 = member4_entry.text().strip()
        if not name:
            err = QDialog(dlg)
            err.setWindowTitle("Validation")
            err_layout = QVBoxLayout(err)
            err_layout.addWidget(QLabel("Please enter a team name."))
            okb = QPushButton("OK")
            okb.setObjectName("okBtn")
            okb.clicked.connect(err.accept)
            err_layout.addWidget(okb)
            err.exec()
            return
        members = [m for m in [member1, member2, member3, member4] if m]
        if len(members) != 4:
            err = QDialog(dlg)
            err.setWindowTitle("Validation")
            err_layout = QVBoxLayout(err)
            err_layout.addWidget(QLabel("Please enter exactly 4 members."))
            okb = QPushButton("OK")
            okb.setObjectName("okBtn")
            okb.clicked.connect(err.accept)
            err_layout.addWidget(okb)
            err.exec()
            return
        payload = {
            "name": name,
            "members": members
        }
        dlg.accept()
        if on_save:
            on_save(payload)

    save_btn.clicked.connect(on_save_click)
    cancel_btn.clicked.connect(dlg.reject)

    dlg.setMinimumWidth(380)
    dlg.adjustSize()
    dlg.exec()


def open_teams_list_modal(parent, teams: list, on_edit: Optional[Callable[[int], None]] = None, on_delete: Optional[Callable[[int], None]] = None):
    """Open modal to view all teams with their scores"""
    dlg = QDialog(parent)
    dlg.setWindowTitle("Teams")
    dlg.setModal(True)
    dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
    dlg.setWindowFlag(Qt.FramelessWindowHint, True)
    dlg.setStyleSheet(STYLE)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)

    header = QHBoxLayout()
    title_lbl = QLabel("Teams List")
    title_lbl.setObjectName("headerTitle")
    header.addWidget(title_lbl)
    header.addStretch()
    layout.addLayout(header)

    # Scrollable teams area
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet("""
        QScrollArea {
            border: 1px solid rgba(125, 211, 252, 0.18);
            background: rgba(15, 23, 42, 0.6);
            border-radius: 8px;
        }
        QScrollBar:vertical {
            background: rgba(15, 23, 42, 0.45);
            width: 10px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background: #0ea5e9;
            border-radius: 5px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background: #38bdf8;
        }
    """)

    teams_container = QWidget()
    teams_container.setStyleSheet("background: transparent;")
    teams_layout = QVBoxLayout(teams_container)
    teams_layout.setSpacing(8)
    teams_layout.setContentsMargins(0, 0, 0, 0)

    if not teams:
        empty_lbl = QLabel("No teams added yet")
        empty_lbl.setAlignment(Qt.AlignCenter)
        empty_lbl.setStyleSheet("color: #a5b4c7; font-size: 12pt; padding: 20px;")
        teams_layout.addWidget(empty_lbl)
    else:
        for idx, team in enumerate(teams):
            team_card = QWidget()
            team_card.setObjectName("teamCard")
            team_card.setStyleSheet("""
                QWidget#teamCard {
                    background: rgba(15, 23, 42, 0.7);
                    border: 1px solid rgba(125, 211, 252, 0.18);
                    border-radius: 8px;
                    padding: 10px;
                }
                QWidget#teamCard QWidget {
                    background: transparent;
                    border: none;
                }
            """)
            team_card.setFixedHeight(60)

            card_layout = QHBoxLayout(team_card)
            card_layout.setContentsMargins(12, 8, 12, 8)
            card_layout.setSpacing(10)

            # Team info
            info_layout = QVBoxLayout()
            team_name_lbl = QLabel(team.get("name", "Unknown"))
            team_name_lbl.setStyleSheet("color: #f8fafc; font-weight: 600; font-size: 12pt;")
            info_layout.addWidget(team_name_lbl)

            members = team.get("members", [])
            members_text = ", ".join(members) if members else "No members"
            members_lbl = QLabel(f"Members: {members_text}")
            members_lbl.setStyleSheet("color: #a5b4c7; font-size: 10pt;")
            info_layout.addWidget(members_lbl)

            card_layout.addLayout(info_layout)
            card_layout.addStretch()

            # Edit and Delete buttons
            edit_btn = QPushButton("Edit")
            edit_btn.setFixedSize(60, 28)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(14,165,233,0.2);
                    color: #BAE6FD;
                    border: none;
                    border-radius: 6px;
                    font-size: 10px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: rgba(14,165,233,0.34);
                }
            """)

            delete_btn = QPushButton("Delete")
            delete_btn.setFixedSize(60, 28)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(244,63,94,0.18);
                    color: #fda4af;
                    border: none;
                    border-radius: 6px;
                    font-size: 10px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: rgba(244,63,94,0.28);
                }
            """)

            def _on_edit(i=idx):
                dlg.accept()
                if on_edit:
                    on_edit(i)

            def _on_delete(i=idx):
                dlg.accept()
                if on_delete:
                    on_delete(i)

            edit_btn.clicked.connect(_on_edit)
            delete_btn.clicked.connect(_on_delete)

            card_layout.addWidget(edit_btn)
            card_layout.addWidget(delete_btn)

            teams_layout.addWidget(team_card)

    teams_layout.addStretch()
    scroll.setWidget(teams_container)
    layout.addWidget(scroll)

    close_btn = QPushButton("Close")
    close_btn.setObjectName("cancelBtn")
    close_btn.setFixedHeight(32)
    close_btn.clicked.connect(dlg.accept)
    layout.addWidget(close_btn)

    dlg.setMinimumWidth(500)
    dlg.setMinimumHeight(400)
    dlg.exec()


def open_delete_team_confirm(parent, team_name: str, on_confirm: Optional[Callable[[], None]] = None):
    """Open confirmation dialog for deleting a team"""
    dlg = QDialog(parent)
    dlg.setWindowTitle("Delete Team")
    dlg.setModal(True)
    dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
    dlg.setWindowFlag(Qt.FramelessWindowHint, True)
    dlg.setStyleSheet(STYLE)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(16, 12, 16, 12)

    msg = QLabel(f"Are you sure you want to delete '{team_name}'?")
    msg.setAlignment(Qt.AlignCenter)
    msg.setWordWrap(True)
    msg.setStyleSheet("color: #e2e8f0; font-weight:600; padding:6px 12px;")
    layout.addWidget(msg)

    btns = QHBoxLayout()
    btns.setSpacing(10)
    cancel_btn = QPushButton("Cancel")
    del_btn = QPushButton("Delete")
    del_btn.setObjectName("dangerBtn")
    cancel_btn.setObjectName("cancelBtn")
    cancel_btn.setFixedHeight(32)
    del_btn.setFixedHeight(32)
    btns.addStretch()
    btns.addWidget(cancel_btn)
    btns.addWidget(del_btn)
    btns.addStretch()
    layout.addLayout(btns)

    def _on_del():
        dlg.accept()
        if on_confirm:
            on_confirm()

    del_btn.clicked.connect(_on_del)
    cancel_btn.clicked.connect(dlg.reject)

    dlg.setMinimumWidth(380)
    dlg.adjustSize()
    dlg.exec()