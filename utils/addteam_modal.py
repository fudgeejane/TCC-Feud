from typing import Callable, Optional, List

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QScrollArea,
    QWidget,
    QCheckBox,
)
from PySide6.QtCore import Qt

try:
    import database.db as db
except Exception:
    db = None

try:
    import utils.teams_modal as teams_modal
except Exception:
    teams_modal = None


def _clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.setParent(None)


def open_add_team_modal(parent, on_create: Optional[Callable[[dict], None]] = None):
    """Open a simple add-team modal and persist the new team to the shared team store."""
    if not teams_modal or not hasattr(teams_modal, "open_add_team_modal"):
        return

    def _handle_create(payload: dict):
        if db:
            try:
                teams = db.load_teams() or []
                teams.append(payload)
                db.save_teams(teams)
            except Exception:
                pass
        if on_create:
            on_create(payload)

    teams_modal.open_add_team_modal(parent, on_create=_handle_create)


def open_select_teams_modal(parent, on_select: Optional[Callable[[List[dict]], None]] = None, selected_indices: Optional[List[int]] = None, max_select: int = 2):
    """Open a modal for selecting two saved teams for the current game."""
    selected_indices = set()
    teams = db.load_teams() if db else []

    dlg = QDialog(parent)
    dlg.setWindowTitle("Select Teams")
    dlg.setModal(True)
    dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
    dlg.setWindowFlag(Qt.FramelessWindowHint, True)
    dlg.setStyleSheet(teams_modal.STYLE if teams_modal and hasattr(teams_modal, "STYLE") else "")

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)

    header = QHBoxLayout()
    title_lbl = QLabel("Select Teams")
    title_lbl.setObjectName("headerTitle")
    header.addWidget(title_lbl)
    header.addStretch()

    add_btn = QPushButton("Add Team")
    add_btn.setFixedHeight(34)
    add_btn.setObjectName("createBtn")
    header.addWidget(add_btn)
    layout.addLayout(header)

    info_lbl = QLabel(f"Choose exactly {max_select} team{'s' if max_select != 1 else ''} to assign to this game.")
    info_lbl.setStyleSheet("color: #cbd5e1; font-size: 10.8pt; margin-bottom: 6px;")
    layout.addWidget(info_lbl)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet("""
        QScrollArea {
            background: transparent;
            border: none;
        }
        QScrollBar:vertical {
            background: rgba(15, 23, 42, 0.45);
            width: 10px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background: #0ea5e9;
            border-radius: 5px;
            min-height: 28px;
        }
        QScrollBar::handle:vertical:hover {
            background: #38bdf8;
        }
    """)

    content = QWidget()
    content.setStyleSheet("background: transparent;")
    content_layout = QVBoxLayout(content)
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(10)
    scroll.setWidget(content)
    layout.addWidget(scroll, stretch=1)

    action_row = QHBoxLayout()
    action_row.setContentsMargins(0, 0, 0, 0)
    action_row.setSpacing(10)
    action_row.addStretch()

    save_btn = QPushButton("Assign Teams")
    save_btn.setObjectName("createBtn")
    save_btn.setFixedHeight(36)
    action_row.addWidget(save_btn)

    cancel_btn = QPushButton("Cancel")
    cancel_btn.setObjectName("cancelBtn")
    cancel_btn.setFixedHeight(36)
    action_row.addWidget(cancel_btn)

    layout.addLayout(action_row)

    checkboxes = []

    def update_save_state():
        save_btn.setEnabled(len(selected_indices) == max_select)
        if len(selected_indices) != max_select:
            save_btn.setToolTip(f"Select exactly {max_select} teams.")
        else:
            save_btn.setToolTip("")

    def refresh_team_list():
        _clear_layout(content_layout)
        checkboxes.clear()

        if not teams:
            empty_lbl = QLabel("No saved teams available. Add a team to continue.")
            empty_lbl.setAlignment(Qt.AlignCenter)
            empty_lbl.setStyleSheet("color: #a5b4c7; font-size: 11pt; padding: 20px;")
            content_layout.addWidget(empty_lbl)
            return

        for index, team in enumerate(teams):
            team_card = QWidget()
            team_card.setStyleSheet("""
                QWidget {
                    background: rgba(15, 23, 42, 0.8);
                    border: 1px solid rgba(125, 211, 252, 0.16);
                    border-radius: 12px;
                    padding: 12px;
                }
                QWidget:hover {
                    border-color: rgba(56, 189, 248, 0.5);
                }
            """)
            card_layout = QHBoxLayout(team_card)
            card_layout.setContentsMargins(12, 12, 12, 12)
            card_layout.setSpacing(12)

            checkbox = QCheckBox(team.get("name", "Unnamed Team"))
            checkbox.setStyleSheet("QCheckBox { color: #f8fafc; font-size: 11pt; } QCheckBox::indicator { width: 18px; height: 18px; }")
            checkbox.setChecked(index in selected_indices)

            def _on_state(state, idx=index):
                # stateChanged emits a plain int: 2 = checked, 0 = unchecked
                if state == 2:
                    selected_indices.add(idx)
                else:
                    selected_indices.discard(idx)
                # enforce max_select: disable unchecked boxes when limit is reached
                if len(selected_indices) >= max_select:
                    for cb in checkboxes:
                        if not cb.isChecked():
                            cb.setEnabled(False)
                else:
                    for cb in checkboxes:
                        cb.setEnabled(True)
                update_save_state()

            checkbox.stateChanged.connect(_on_state)
            checkboxes.append(checkbox)
            card_layout.addWidget(checkbox, alignment=Qt.AlignLeft)

            team_info = QLabel(f"{team.get('name', 'Unnamed Team')}\nMembers: {', '.join(team.get('members', []))}")
            team_info.setStyleSheet("color: #cbd5e1; font-size: 10pt; line-height: 1.3;")
            card_layout.addWidget(team_info)
            card_layout.addStretch()
            content_layout.addWidget(team_card)

    def add_new_team():
        def _on_create(payload):
            teams.append(payload)
            if db:
                try:
                    db.save_teams(teams)
                except Exception:
                    pass
            refresh_team_list()
            update_save_state()

        open_add_team_modal(parent, on_create=_on_create)

    def _on_save():
        if len(selected_indices) != max_select:
            return
        chosen = [teams[i] for i in sorted(selected_indices)]
        dlg.accept()
        if on_select:
            on_select(chosen)

    add_btn.clicked.connect(add_new_team)
    save_btn.clicked.connect(_on_save)
    cancel_btn.clicked.connect(dlg.reject)

    refresh_team_list()
    update_save_state()
    # apply initial disable state if pre-selected indices already hit the limit
    if len(selected_indices) >= max_select:
        for cb in checkboxes:
            if not cb.isChecked():
                cb.setEnabled(False)

    dlg.setMinimumWidth(620)
    dlg.setMinimumHeight(460)
    dlg.exec()