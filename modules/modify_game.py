from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QHBoxLayout,
)
from PySide6.QtCore import Qt
import uuid

try:
    import modules.play_game as play_game
except Exception:
    play_game = None


def _apply_button_style(button: QPushButton, role: str) -> None:
    styles = {
        "secondary": """
            QPushButton {
                background: rgba(148, 163, 184, 0.16);
                color: #E2E8F0;
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 14px;
                padding: 0 20px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: rgba(148, 163, 184, 0.24);
                border: 1px solid rgba(148, 163, 184, 0.28);
            }
        """,
        "primary": """
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #2563EB, stop:1 #3B82F6);
                color: white;
                border: none;
                border-radius: 14px;
                padding: 0 22px;
                font-size: 14px;
                font-weight: 800;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #3B82F6, stop:1 #60A5FA);
            }
            QPushButton:disabled {
                background: rgba(148, 163, 184, 0.16);
                color: rgba(226, 232, 240, 0.55);
            }
        """,
        "success": """
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #16A34A, stop:1 #22C55E);
                color: white;
                border: none;
                border-radius: 14px;
                padding: 0 22px;
                font-size: 14px;
                font-weight: 800;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #22C55E, stop:1 #4ADE80);
            }
            QPushButton:disabled {
                background: rgba(148, 163, 184, 0.16);
                color: rgba(226, 232, 240, 0.55);
            }
        """,
        "danger": """
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #DC2626, stop:1 #EF4444);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 7px 12px;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #EF4444, stop:1 #F87171);
            }
        """,
        "muted": """
            QPushButton {
                background: rgba(148, 163, 184, 0.18);
                color: #E2E8F0;
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 10px;
                padding: 7px 12px;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: rgba(148, 163, 184, 0.26);
            }
        """,
    }
    button.setStyleSheet(styles.get(role, styles["secondary"]))


def _field_style(radius: int = 14) -> str:
    return f"""
        background: transparent;
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: {radius}px;
        padding: 12px 14px;
        color: #E2E8F0;
        selection-background-color: #2563EB;
        selection-color: white;
    """


def _spin_style() -> str:
    return """
        QSpinBox {
            background: transparent;
            color: #E2E8F0;
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 12px;
            padding: 6px 8px;
            font-size: 11pt;
            font-weight: 700;
        }
        QSpinBox:focus {
            border: 1px solid #60A5FA;
            background: transparent;
        }
    """


def open_modify_game(app, title: str, description: str, game_id: str | None = None):
    """Open a full-page Modify Game view inside the application's stack.

    The function will reuse an existing modify page if present, otherwise it
    constructs a new QWidget, adds it to `app.stack`, and switches to it.
    This view is static (placeholder) but provides Back and Save actions.
    """
    try:
        # Reuse existing modify page if previously created
        if hasattr(app, "modify_widget") and app.modify_widget is not None:
            try:
                app.modify_title_label.setText(title or "(Untitled Game)")
            except Exception:
                pass
            try:
                app.modify_desc_label.setText(description or "No description provided")
            except Exception:
                pass
            app.stack.setCurrentWidget(app.modify_widget)
            return
    except Exception:
        pass

    # Build a scrollable page with a clearer hierarchy: header, helper strip,
    # and question cards that keep editing actions together.
    from PySide6.QtWidgets import QScrollArea, QFrame, QSizePolicy

    page = QWidget()
    try:
        page.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #050B1A, stop:0.45 #071A3A, stop:1 #081227);
                color: #E2E8F0;
                font-family: Segoe UI, Arial, sans-serif;
            }
        """)
    except Exception:
        pass
    page_layout = QVBoxLayout(page)
    page_layout.setContentsMargins(60, 30, 60, 30)
    page_layout.setSpacing(22)

    # Header: logo, title, and action buttons.
    header = QWidget()
    header.setStyleSheet("""
        QWidget {
            background: none;
            border: none;
        }
    """)
    h_layout = QHBoxLayout(header)
    h_layout.setContentsMargins(0, 0, 0, 0)
    h_layout.setSpacing(18)
    logo_lbl = QLabel()
    try:
        from pathlib import Path

        assets_logo = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
        if assets_logo.exists():
            from PySide6.QtGui import QPixmap

            pix = QPixmap(str(assets_logo))
            if not pix.isNull():
                pix = pix.scaledToWidth(280, Qt.SmoothTransformation)
                logo_lbl.setPixmap(pix)
            else:
                logo_lbl.setText("TCC Feud")
                logo_lbl.setStyleSheet("font-size:22pt; color: #F8FAFC; font-weight: 800;")
        else:
            logo_lbl.setText("TCC Feud")
            logo_lbl.setStyleSheet("font-size:22pt; color: #F8FAFC; font-weight: 800;")
    except Exception:
        logo_lbl.setText("TCC Feud")
        logo_lbl.setStyleSheet("font-size:22pt; color: #F8FAFC; font-weight: 800;")

    h_layout.addWidget(logo_lbl, alignment=Qt.AlignLeft)
    h_layout.addStretch()

    title_block = QWidget()
    title_layout = QVBoxLayout(title_block)
    title_layout.setContentsMargins(0, 4, 0, 4)
    title_layout.setSpacing(4)
    h_layout.addWidget(title_block)
    h_layout.addStretch()

    game_number = None
    try:
        if hasattr(app, "games") and isinstance(app.games, list):
            for index, game in enumerate(app.games):
                if game.get("id") == game_id or game.get("title") == title:
                    game_number = index + 1
                    break
            if game_number is None:
                for index, game in enumerate(app.games):
                    if game.get("title") == title:
                        game_number = index + 1
                        break
    except Exception:
        pass

    # Header action buttons: Back to Board and Play Game.
    back_board = QPushButton("Back to Board")
    back_board.setFixedHeight(48)
    _apply_button_style(back_board, "secondary")
    back_board.setCursor(Qt.PointingHandCursor)
    back_board.clicked.connect(app.show_home)

    play_btn = QPushButton("Play Game")
    play_btn.setFixedHeight(48)
    _apply_button_style(play_btn, "success")
    play_btn.setCursor(Qt.PointingHandCursor)

    def _on_play(t=title, d=description):
        try:
            if play_game and hasattr(play_game, "open_play_game"):
                # open Play view and load the first question from the DB for this game
                try:
                    play_game.open_play_game(app, t, d, load_db_first=True)
                except TypeError:
                    # fallback if older signature
                    play_game.open_play_game(app, t, d)
                return
        except Exception:
            pass
        # fallback
        try:
            app.show_game(t, d)
        except Exception:
            pass

    play_btn.clicked.connect(_on_play)

    h_layout.addWidget(back_board, alignment=Qt.AlignRight)
    h_layout.addWidget(play_btn, alignment=Qt.AlignRight)

    page_layout.addWidget(header)

    helper_strip = QWidget()
    helper_strip.setStyleSheet("""
        QWidget {
            background:none;
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 18px;
        }
    """)
  
    # Toolbar under header
    from PySide6.QtWidgets import QScrollArea, QFrame, QSizePolicy, QLineEdit, QSpinBox, QCheckBox, QAbstractSpinBox, QMessageBox, QDialog

    # optional DB persistence helper
    try:
        import database.db as db
    except Exception:
        db = None

    # store current game id on the app for UI-only association
    try:
        if game_id is not None:
            app.current_game_id = game_id
    except Exception:
        pass

    def _ensure_target_game():
        if not hasattr(app, "games") or not isinstance(app.games, list):
            app.games = []

        gid = getattr(app, "current_game_id", None)
        target_game = None

        if gid:
            for g in app.games:
                if g.get("id") == gid:
                    target_game = g
                    break

        if not target_game:
            for g in app.games:
                if g.get("title") == title:
                    target_game = g
                    break

        if not target_game:
            target_game = {
                "title": title or "(Untitled Game)",
                "description": description or "",
                "id": gid or uuid.uuid4().hex,
                "questions": [],
                "teams": [],
            }
            app.games.append(target_game)
            try:
                app.current_game_id = target_game.get("id")
            except Exception:
                pass

        return target_game

    # Team controls row. Team editing is handled in a modal.
    teams_panel = QWidget()
    teams_panel.setStyleSheet("""
        QWidget {
            background: none;
            border: none;
        }
    """)
    teams_layout = QVBoxLayout(teams_panel)
    teams_layout.setContentsMargins(0, 0, 0, 0)
    teams_layout.setSpacing(12)

  

    teams_actions = QHBoxLayout()
    teams_actions.setContentsMargins(0, 0, 0, 0)
    teams_actions.addStretch()

    edit_teams_btn = QPushButton("Edit Teams")
    edit_teams_btn.setFixedHeight(42)
    _apply_button_style(edit_teams_btn, "secondary")
    edit_teams_btn.setCursor(Qt.PointingHandCursor)
    teams_actions.addWidget(edit_teams_btn)

    add_question_side_btn = QPushButton("Add Question")
    add_question_side_btn.setFixedHeight(42)
    _apply_button_style(add_question_side_btn, "primary")
    add_question_side_btn.setCursor(Qt.PointingHandCursor)
    teams_actions.addWidget(add_question_side_btn)
    teams_layout.addLayout(teams_actions)

    def _load_teams_data():
        target_game = _ensure_target_game()
        teams = target_game.get("teams", [])
        if not isinstance(teams, list):
            teams = []

        if len(teams) < 2:
            while len(teams) < 2:
                default_name = f"Team {chr(ord('A') + len(teams))}"
                teams.append({"name": default_name, "members": ["", "", "", ""]})
            target_game["teams"] = teams
            if db:
                try:
                    db.save_games(app.games)
                except Exception:
                    pass

        return teams

    def _open_teams_modal():
        teams = _load_teams_data()

        dlg = QDialog(page)
        dlg.setWindowTitle("Edit Teams")
        dlg.setModal(True)
        dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        dlg.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #071327, stop:1 #0B1F3F);
                border: 1px solid rgba(125, 211, 252, 0.30);
                border-radius: 18px;
            }
            QLabel#teamsModalTitle {
                color: #F8FAFC;
                font-size: 18px;
                font-weight: 900;
                background: transparent;
            }
            QLabel#teamsModalHint {
                color: #B8D7F5;
                font-size: 11px;
                font-weight: 600;
                background: transparent;
            }
            QLineEdit {
                background: rgba(2, 6, 23, 0.45);
            }
        """)
        dlg_layout = QVBoxLayout(dlg)
        dlg_layout.setContentsMargins(18, 16, 18, 16)
        dlg_layout.setSpacing(14)

        modal_header = QWidget()
        mh_layout = QVBoxLayout(modal_header)
        mh_layout.setContentsMargins(0, 0, 0, 0)
        mh_layout.setSpacing(2)

        modal_title = QLabel("Edit Teams")
        modal_title.setObjectName("teamsModalTitle")
        modal_hint = QLabel("Set team names and up to four members per team.")
        modal_hint.setObjectName("teamsModalHint")

        mh_layout.addWidget(modal_title)
        mh_layout.addWidget(modal_hint)
        dlg_layout.addWidget(modal_header)

        row = QHBoxLayout()
        row.setSpacing(14)

        local_team_name_inputs = []
        local_team_member_inputs = []

        def _team_card(default_name: str):
            card = QWidget()
            card.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 rgba(10, 25, 52, 0.94), stop:1 rgba(19, 45, 92, 0.94));
                    border: 1px solid rgba(125, 211, 252, 0.24);
                    border-radius: 16px;
                }
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(14, 14, 14, 14)
            cl.setSpacing(9)

            team_lbl = QLabel(default_name.upper())
            team_lbl.setStyleSheet("""
                color: #7DD3FC;
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 1px;
                background: transparent;
            """)
            cl.addWidget(team_lbl)

            name_input = QLineEdit()
            name_input.setPlaceholderText("Team name")
            name_input.setText(default_name)
            name_input.setMinimumHeight(40)
            name_input.setStyleSheet(f"QLineEdit {{{_field_style(10)}}} QLineEdit:focus {{ border: 1px solid #60A5FA; background: transparent; }}")
            cl.addWidget(name_input)

            member_inputs = []
            for idx in range(4):
                mi = QLineEdit()
                mi.setPlaceholderText(f"Member {idx + 1}")
                mi.setMinimumHeight(36)
                mi.setStyleSheet(f"QLineEdit {{{_field_style(10)}}} QLineEdit:focus {{ border: 1px solid #60A5FA; background: transparent; }}")
                member_inputs.append(mi)
                cl.addWidget(mi)

            local_team_name_inputs.append(name_input)
            local_team_member_inputs.append(member_inputs)
            return card

        row.addWidget(_team_card("Team A"))
        row.addWidget(_team_card("Team B"))
        dlg_layout.addLayout(row)

        for t_idx in range(2):
            team_data = teams[t_idx] if t_idx < len(teams) and isinstance(teams[t_idx], dict) else {}
            local_team_name_inputs[t_idx].setText((team_data.get("name") or f"Team {chr(ord('A') + t_idx)}").strip())
            members = team_data.get("members", [])
            if not isinstance(members, list):
                members = []
            for m_idx in range(4):
                local_team_member_inputs[t_idx][m_idx].setText(str(members[m_idx] if m_idx < len(members) else ""))

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 6, 0, 0)
        actions.setSpacing(10)
        actions.addStretch()
        save_btn = QPushButton("Save Teams")
        _apply_button_style(save_btn, "success")
        save_btn.setFixedHeight(40)
        cancel_btn = QPushButton("Cancel")
        _apply_button_style(cancel_btn, "secondary")
        cancel_btn.setFixedHeight(40)
        actions.addWidget(cancel_btn)
        actions.addWidget(save_btn)
        dlg_layout.addLayout(actions)

        def _save_and_close():
            target_game = _ensure_target_game()
            teams_payload = []
            for t_idx in range(2):
                tname = local_team_name_inputs[t_idx].text().strip() or f"Team {chr(ord('A') + t_idx)}"
                members = [local_team_member_inputs[t_idx][m_idx].text().strip() for m_idx in range(4)]
                teams_payload.append({"name": tname, "members": members})

            target_game["teams"] = teams_payload

            saved_ok = True
            if db:
                try:
                    saved_ok = bool(db.save_games(app.games))
                except Exception:
                    saved_ok = False

            if hasattr(app, "render_home_cards"):
                try:
                    app.render_home_cards()
                except Exception:
                    pass

            if not saved_ok:
                QMessageBox.warning(dlg, "Save Failed", "Could not save team data to disk.")
                return

            dlg.accept()

        save_btn.clicked.connect(_save_and_close)
        cancel_btn.clicked.connect(dlg.reject)
        dlg.setMinimumWidth(920)
        dlg.exec()

    _load_teams_data()
    edit_teams_btn.clicked.connect(_open_teams_modal)
    page_layout.addWidget(teams_panel)

    # Scroll area for dynamic question cards
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setStyleSheet("""
        QScrollArea {
            background: none;
            border: none;
        }
        QScrollBar:vertical {
            background: rgba(15, 23, 42, 0.55);
            width: 12px;
            margin: 4px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background: rgba(96, 165, 250, 0.55);
            border-radius: 6px;
            min-height: 36px;
        }
        QScrollBar::handle:vertical:hover {
            background: rgba(96, 165, 250, 0.78);
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
            background: transparent;
        }
    """)
    scroll_content = QWidget()
    sc_layout = QVBoxLayout(scroll_content)
    sc_layout.setContentsMargins(0, 0, 0, 0)
    sc_layout.setSpacing(20)

    # Container where question cards will be added
    questions_container = QWidget()
    questions_layout = QVBoxLayout(questions_container)
    questions_layout.setContentsMargins(0, 0, 0, 0)
    questions_layout.setSpacing(16)

    # Helper to renumber question titles
    def renumber_questions():
        for i in range(questions_layout.count()):
            item = questions_layout.itemAt(i).widget()
            if item is None:
                continue
            title_lbl = item.findChild(QLabel, "_q_title")
            if title_lbl:
                title_lbl.setText(f"Question {i+1}")

    # Function to create and add a new question card
    def add_question(initial: dict | None = None):
        card = QWidget()
        card.setObjectName("question_card")
        # subtle shadow for card to lift it from the background
        try:
            from PySide6.QtWidgets import QGraphicsDropShadowEffect
            from PySide6.QtGui import QColor

            sh = QGraphicsDropShadowEffect(card)
            sh.setBlurRadius(18)
            sh.setXOffset(0)
            sh.setYOffset(6)
            sh.setColor(QColor(6, 11, 28, 120))
            card.setGraphicsEffect(sh)
        except Exception:
            pass
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(14)
        card.setStyleSheet("""
            QWidget#question_card {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 rgba(9, 18, 40, 0.95), stop:1 rgba(15, 35, 75, 0.95));
                border: 1px solid rgba(96,165,250,0.18);
                border-radius: 22px;
            }
        """)

        # Top row: title, fast-money toggle, reset, delete
        top = QWidget()
        top.setStyleSheet("background: none; border: none;")
        top_l = QHBoxLayout(top)
        top_l.setContentsMargins(0, 0, 0, 0)
        top_l.setSpacing(10)
        title_lbl = QLabel("Question")
        title_lbl.setObjectName("_q_title")
        title_lbl.setStyleSheet("""
            color: #F8FAFC;
            font-weight: 800;
            font-size: 14pt;
            background: none;
        """)
        top_l.addWidget(title_lbl)
        top_l.addStretch()

        fast_cb = QCheckBox("Fast Money")
        fast_cb.setCursor(Qt.PointingHandCursor)
        fast_cb.setStyleSheet("""
            QCheckBox {
                color: #BFDBFE;
                font-size: 10.5pt;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid rgba(255,255,255,0.22);
                border-radius: 4px;
                background: rgba(255,255,255,0.08);
            }
            QCheckBox::indicator:checked {
                background: #F59E0B;
                border: 1px solid #F59E0B;
            }
        """)
        top_l.addWidget(fast_cb)

        reset_btn = QPushButton("Reset")
        _apply_button_style(reset_btn, "danger")
        reset_btn.setCursor(Qt.PointingHandCursor)
        top_l.addWidget(reset_btn)

        del_btn = QPushButton("Delete")
        _apply_button_style(del_btn, "muted")
        del_btn.setCursor(Qt.PointingHandCursor)
        top_l.addWidget(del_btn)

        card_layout.addWidget(top)

        # Question input
        q_input = QLineEdit()
        q_input.setPlaceholderText("Enter question text...")
        q_input.setMinimumHeight(54)
        q_input.setStyleSheet(f"QLineEdit {{{_field_style(14)}}} QLineEdit:focus {{ border: 1px solid #F59E0B; background: transparent; }}")
        card_layout.addWidget(q_input)

        # Answers: two columns, four answers each (1-4 left, 5-8 right)
        answers_area = QWidget()
        answers_area.setStyleSheet("background: none; border: none;")
        answers_layout = QHBoxLayout(answers_area)
        answers_layout.setContentsMargins(0, 0, 0, 0)
        answers_layout.setSpacing(14)

        # We'll collect score inputs and answer edits per card so we can compute a running total
        score_inputs = []
        answer_inputs = []

        # First column (answers 1-4)
        col1 = QWidget()
        col1.setStyleSheet("background: none; border: none;")
        col1_l = QVBoxLayout(col1)
        col1_l.setContentsMargins(0, 0, 0, 0)
        col1_l.setSpacing(10)
        for a_i in range(4):
            row = QWidget()
            row.setStyleSheet("background: none; border: none;")
            r_layout = QHBoxLayout(row)
            r_layout.setContentsMargins(0, 0, 0, 0)
            r_layout.setSpacing(8)
            ans_input = QLineEdit()
            ans_input.setPlaceholderText(f"Answer {a_i+1}")
            ans_input.setMinimumHeight(48)
            ans_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            ans_input.setStyleSheet(f"QLineEdit {{{_field_style(12)}}} QLineEdit:focus {{ border: 1px solid #60A5FA; background: transparent; }}")
            score_input = QSpinBox()
            score_input.setRange(0, 1000000)
            score_input.setFixedWidth(92)
            score_input.setMinimumHeight(36)
            score_input.setStyleSheet(_spin_style())
            score_input.setAlignment(Qt.AlignCenter)
            score_input.setToolTip("Points awarded for this answer")
            try:
                score_input.setButtonSymbols(QAbstractSpinBox.NoButtons)
            except Exception:
                pass
            answer_inputs.append(ans_input)
            score_inputs.append(score_input)
            r_layout.addWidget(ans_input)
            r_layout.addWidget(score_input, alignment=Qt.AlignRight)
            col1_l.addWidget(row)

        # Second column (answers 5-8)
        col2 = QWidget()
        col2.setStyleSheet("background: none; border: none;")
        col2_l = QVBoxLayout(col2)
        col2_l.setContentsMargins(0, 0, 0, 0)
        col2_l.setSpacing(10)
        for a_i in range(4, 8):
            row = QWidget()
            row.setStyleSheet("background: none; border: none;")
            r_layout = QHBoxLayout(row)
            r_layout.setContentsMargins(0, 0, 0, 0)
            r_layout.setSpacing(8)
            ans_input = QLineEdit()
            ans_input.setPlaceholderText(f"Answer {a_i+1}")
            ans_input.setMinimumHeight(48)
            ans_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            ans_input.setStyleSheet(f"QLineEdit {{{_field_style(12)}}} QLineEdit:focus {{ border: 1px solid #60A5FA; background: none; }}")
            score_input = QSpinBox()
            score_input.setRange(0, 1000000)
            score_input.setFixedWidth(92)
            score_input.setMinimumHeight(36)
            score_input.setStyleSheet(_spin_style())
            score_input.setAlignment(Qt.AlignCenter)
            score_input.setToolTip("Points awarded for this answer")
            try:
                score_input.setButtonSymbols(QAbstractSpinBox.NoButtons)
            except Exception:
                pass
            answer_inputs.append(ans_input)
            score_inputs.append(score_input)
            r_layout.addWidget(ans_input)
            r_layout.addWidget(score_input, alignment=Qt.AlignRight)
            col2_l.addWidget(row)

        answers_layout.addWidget(col1)
        answers_layout.addWidget(col2)
        card_layout.addWidget(answers_area)

        # Total score display for this question card with Save button
        total_row = QWidget()
        total_row.setStyleSheet("background: none; border: none;")
        total_l = QHBoxLayout(total_row)
        total_l.setContentsMargins(0, 8, 0, 0)

        total_l.addStretch()  # pushes everything to the right

        total_label = QLabel("Total: 0 pts")
        total_label.setStyleSheet("""
            color: #F8FAFC;
            font-weight: 700;
            font-size: 12pt;
            background: none;
        """)

        save_btn = QPushButton("Save")
        save_btn.setCursor(Qt.PointingHandCursor)
        _apply_button_style(save_btn, "success")
        save_btn.setFixedHeight(42)

        total_l.addWidget(total_label)
        total_l.addWidget(save_btn)

        card_layout.addWidget(total_row)

        def update_total():
            s = sum(si.value() for si in score_inputs)
            total_label.setText(f"Total: {s} pts")

        # mark card unsaved when user edits any input so Save button re-enables
        def mark_unsaved():
            try:
                if getattr(card, "_saved", False):
                    card._saved = False
                    save_btn.setText("Save")
                    save_btn.setEnabled(True)
                    save_btn.setToolTip("Save this question before adding another one.")
                    update_add_button_state()
            except Exception:
                pass

        for si in score_inputs:
            # update total when score changes
            si.valueChanged.connect(lambda v, fn=update_total: fn())
            # mark card as unsaved when score changes
            si.valueChanged.connect(lambda v, fn=mark_unsaved: fn())

        # mark unsaved when text inputs change (question and answers)
        try:
            q_input.textChanged.connect(lambda *_: mark_unsaved())
        except Exception:
            pass
        for ai in answer_inputs:
            try:
                ai.textChanged.connect(lambda *_: mark_unsaved())
            except Exception:
                pass

        # if initial data provided, pre-fill fields and mark saved
        if initial:
            try:
                q_input.setText(initial.get("question", ""))
                fast_cb.setChecked(bool(initial.get("fast_money", False)))
                ans_list = initial.get("answers", [])
                # fill answers and scores in order
                for i, line in enumerate(answer_inputs):
                    if i < len(ans_list):
                        line.setText(ans_list[i].get("text", ""))
                for i, si in enumerate(score_inputs):
                    if i < len(ans_list):
                        try:
                            si.setValue(int(ans_list[i].get("score", 0)))
                        except Exception:
                            si.setValue(0)
                # compute total display
                update_total()
                # mark saved state
                card._saved = True
                card.saved_payload = initial
                save_btn.setText("Saved")
                save_btn.setEnabled(False)
                save_btn.setToolTip("This question is saved.")
            except Exception:
                pass

        # mark card as unsaved initially (unless pre-filled)
        if not initial:
            card._saved = False

        def set_card_saved(payload: dict):
            card._saved = True
            card.saved_payload = payload
            save_btn.setText("Saved")
            save_btn.setEnabled(False)
            save_btn.setToolTip("This question is saved.")
            # after saving, enable Add Question if no unsaved cards
            update_add_button_state()

        def save_question():
            # basic validation: question text required
            qtext = q_input.text().strip()
            if not qtext:
                mb = QMessageBox(card)
                mb.setWindowTitle("Validation")
                mb.setText("Please enter the question text before saving.")
                mb.exec()
                return
            answers = []
            for col in (col1, col2):
                for i in range(col.layout().count()):
                    roww = col.layout().itemAt(i).widget()
                    if roww is None:
                        continue
                    line = roww.findChild(QLineEdit)
                    spin = roww.findChild(QSpinBox)
                    answers.append({
                        "text": line.text().strip() if line else "",
                        "score": spin.value() if spin else 0,
                    })
            payload = {
                "question": qtext,
                "fast_money": bool(fast_cb.isChecked()),
                "answers": answers,
                "total": sum(a["score"] for a in answers),
                "game_id": getattr(app, "current_game_id", None),
            }
            # ensure a stable id for updates
            try:
                if hasattr(card, "saved_payload") and isinstance(card.saved_payload, dict) and card.saved_payload.get("id"):
                    payload["id"] = card.saved_payload.get("id")
                else:
                    payload["id"] = uuid.uuid4().hex
            except Exception:
                payload["id"] = uuid.uuid4().hex
            # associate with app.games under the matching game id or title when possible
            try:
                if not hasattr(app, "games") or not isinstance(app.games, list):
                    app.games = []

                gid = payload.get("game_id") or getattr(app, "current_game_id", None)
                target_game = None

                # prefer matching by explicit id
                if gid:
                    for g in app.games:
                        if g.get("id") == gid:
                            target_game = g
                            break

                # fallback to matching by title
                if not target_game:
                    for g in app.games:
                        if g.get("title") == title:
                            target_game = g
                            break

                # if still not found, create a new game entry and append it
                if not target_game:
                    new_game = {"title": title or "(Untitled Game)", "description": description or "", "id": gid or uuid.uuid4().hex, "questions": []}
                    app.games.append(new_game)
                    target_game = new_game

                qs = target_game.setdefault("questions", [])
                # Prefer updating the card's saved_payload object directly if available
                saved_ref = None
                try:
                    if hasattr(card, "saved_payload") and isinstance(card.saved_payload, dict):
                        # update the saved_payload dict in-place
                        card.saved_payload.clear()
                        card.saved_payload.update(payload)
                        saved_ref = card.saved_payload
                        # ensure it's present in the questions list
                        if card.saved_payload not in qs:
                            # try to replace by id if an old entry exists
                            replaced = False
                            for i, q in enumerate(qs):
                                if isinstance(q, dict) and q.get("id") == payload.get("id"):
                                    qs[i] = card.saved_payload
                                    replaced = True
                                    break
                            if not replaced:
                                qs.append(card.saved_payload)
                    else:
                        # fallback: try replace existing question by id (update in-place)
                        replaced = False
                        for i, q in enumerate(qs):
                            if isinstance(q, dict) and q.get("id") == payload.get("id"):
                                q.clear()
                                q.update(payload)
                                saved_ref = q
                                replaced = True
                                break
                        if not replaced:
                            qs.append(payload)
                            saved_ref = payload
                except Exception:
                    # as a last resort, append the payload
                    try:
                        qs.append(payload)
                        saved_ref = payload
                    except Exception:
                        saved_ref = payload

                # persist to DB if available (raise or log on failure)
                if db:
                    ok = False
                    try:
                        ok = db.save_games(app.games)
                    except Exception:
                        ok = False
                    if not ok:
                        try:
                            mb = QMessageBox(card)
                            mb.setWindowTitle("Save Failed")
                            mb.setText("Could not save changes to disk. Your changes are kept in memory.")
                            mb.exec()
                        except Exception:
                            pass

                # refresh home view if available so changes are visible immediately
                try:
                    if hasattr(app, "render_home_cards"):
                        app.render_home_cards()
                except Exception:
                    pass
            except Exception:
                try:
                    mb = QMessageBox(card)
                    mb.setWindowTitle("Error")
                    mb.setText("An error occurred while saving the question.")
                    mb.exec()
                except Exception:
                    pass
            # use saved_ref when available to keep consistent object reference
            try:
                set_card_saved(saved_ref if 'saved_ref' in locals() and saved_ref is not None else payload)
            except Exception:
                set_card_saved(payload)

        save_btn.clicked.connect(save_question)

        # Reset behavior for this card
        def _reset_card():
            q_input.clear()
            fast_cb.setChecked(False)
            for i in range(card_layout.count()):
                w = card_layout.itemAt(i).widget()
                if isinstance(w, QWidget):
                    # find QLineEdit and QSpinBox children
                    for child in w.findChildren(QLineEdit):
                        child.clear()
                    for child in w.findChildren(QSpinBox):
                        child.setValue(0)
                # resetting makes the card unsaved
                try:
                    card._saved = False
                    save_btn.setText("Save")
                    save_btn.setEnabled(True)
                    save_btn.setToolTip("Save this question before adding another one.")
                    update_add_button_state()
                except Exception:
                    pass

        fast_cb.stateChanged.connect(lambda *_: mark_unsaved())
        reset_btn.clicked.connect(_reset_card)

        # Delete behavior
        def _delete_card():
            # show a parented modal dialog (overlay-style) to confirm deletion
            try:
                from utils.question_modal import open_confirm_modal

                confirmed = open_confirm_modal(
                    page,
                    "Delete Question",
                    "Are you sure you want to delete this question? This action cannot be undone.",
                )
                if not confirmed:
                    return
            except Exception:
                # fallback to simple QMessageBox if dialog creation fails
                try:
                    resp = QMessageBox.question(
                        page,
                        "Delete Question",
                        "Are you sure you want to delete this question? This action cannot be undone.",
                        QMessageBox.Yes | QMessageBox.No,
                    )
                except Exception:
                    return
                if resp not in (QMessageBox.Yes, QMessageBox.StandardButton(QMessageBox.Yes)):
                    return

            # remove from data model if this card was previously saved
            try:
                if hasattr(app, "games") and isinstance(app.games, list):
                    gid = getattr(app, "current_game_id", None)
                    target_game = None
                    if gid:
                        for g in app.games:
                            if g.get("id") == gid or g.get("title") == title:
                                target_game = g
                                break
                    if not target_game:
                        for g in app.games:
                            if g.get("title") == title:
                                target_game = g
                                break
                    if target_game and isinstance(target_game.get("questions"), list):
                        try:
                            if hasattr(card, "saved_payload") and isinstance(card.saved_payload, dict):
                                sp = card.saved_payload
                                # remove by identity or by id
                                for i, q in enumerate(list(target_game.get("questions", []))):
                                    try:
                                        if q is sp or (isinstance(q, dict) and sp.get("id") and q.get("id") == sp.get("id")):
                                            del target_game["questions"][i]
                                            break
                                    except Exception:
                                        continue
                        except Exception:
                            pass
                    # persist changes
                    if db:
                        try:
                            db.save_games(app.games)
                        except Exception:
                            pass
            except Exception:
                pass

            # remove UI
            try:
                card.setParent(None)
                card.deleteLater()
            except Exception:
                pass
            renumber_questions()
            # if deleted, ensure Add Question button state updates
            try:
                update_add_button_state()
            except Exception:
                pass
            try:
                if hasattr(app, "render_home_cards"):
                    app.render_home_cards()
            except Exception:
                pass

        del_btn.clicked.connect(_delete_card)

        questions_layout.addWidget(card)
        renumber_questions()

    # Wire Add Question button
    def any_unsaved():
        for i in range(questions_layout.count()):
            w = questions_layout.itemAt(i).widget()
            if w and getattr(w, "_saved", False) is False:
                return True
        return False

    def update_add_button_state():
        try:
            can_add = not any_unsaved()
            add_question_side_btn.setEnabled(can_add)
            add_question_side_btn.setToolTip("Add another question" if can_add else "Save the current question first")
        except Exception:
            add_question_side_btn.setEnabled(True)

    def _add_question_from_button():
        if any_unsaved():
            return
        add_question(None)
        try:
            scrollbar = scroll.verticalScrollBar()
            if scrollbar is not None:
                scrollbar.setValue(scrollbar.maximum())
        except Exception:
            pass

    add_question_side_btn.clicked.connect(_add_question_from_button)

    # Populate existing saved questions for this game (if any), otherwise start with one blank
    try:
        populated = False
        if hasattr(app, "games"):
            gid = getattr(app, "current_game_id", None)
            target_game = None
            if gid:
                for g in app.games:
                    if g.get("id") == gid or g.get("title") == title:
                        target_game = g
                        break
            if not target_game:
                for g in app.games:
                    if g.get("title") == title:
                        target_game = g
                        break
            if target_game and isinstance(target_game.get("questions"), list):
                for q in target_game.get("questions", []):
                    add_question(q)
                populated = True
        if not populated:
            add_question(None)
    except Exception:
        add_question(None)
    # ensure Add Question button state reflects any unsaved items
    try:
        update_add_button_state()
    except Exception:
        pass

    sc_layout.addWidget(questions_container)
    sc_layout.addStretch()
    scroll.setWidget(scroll_content)
    page_layout.addWidget(scroll)

    

    # Store references and show
    app.modify_widget = page
    try:
        app.stack.addWidget(page)
        app.stack.setCurrentWidget(page)
    except Exception:
        try:
            app.show_static_modal(f"Modify {title}", "Modify page could not be opened.")
        except Exception:
            pass
