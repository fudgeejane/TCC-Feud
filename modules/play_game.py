from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
    QInputDialog,
    QMessageBox,
    QDialog,
    QLineEdit,
    QStackedLayout,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import (
    Qt,
    QEvent,
    QObject,
    QEasingCurve,
    QPropertyAnimation,
    QSequentialAnimationGroup,
)
from PySide6.QtGui import QFont, QColor, QIntValidator
import utils.game_modal as game_modal
import modules.display_game as display_game
import database.db as db


def open_play_game(app, title: str, description: str, load_db_first: bool = False):
    """Open the Play Game page in the app.stack."""

    try:
        if hasattr(app, "play_widget") and app.play_widget is not None:
            app.stack.setCurrentWidget(app.play_widget)
            return
    except Exception:
        pass

    page = QWidget()
    page.setStyleSheet("""
        QWidget {
            background-color: #020617;
            color: #E2E8F0;
            font-family: Segoe UI, Arial, sans-serif;
        }
    """)

    layout = QVBoxLayout(page)
    layout.setContentsMargins(24, 24, 24, 20)
    layout.setSpacing(16)

    def make_shadow(w, blur=24, color=QColor(59, 130, 246, 120), y=6):
        shadow = QGraphicsDropShadowEffect(w)
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, y)
        shadow.setColor(color)
        w.setGraphicsEffect(shadow)
        return shadow

    # ----------------------------
    # Header bar
    # ----------------------------
    top_header = QFrame()
    top_header.setStyleSheet("""
        QFrame {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #0F172A, stop:1 #111827);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
        }
    """)
    make_shadow(top_header, blur=28, color=QColor(0, 0, 0, 120), y=8)

    th_layout = QHBoxLayout(top_header)
    th_layout.setContentsMargins(20, 14, 20, 14)
    th_layout.setSpacing(14)

    title_wrap = QVBoxLayout()
    title_wrap.setSpacing(2)

    top_title = QLabel(title or "Family Feud")
    top_title.setStyleSheet("""
        color: #F8FAFC;
        font-size: 24px;
        font-weight: 800;
    """)

    top_subtitle = QLabel(description or "Play and manage the current round")
    top_subtitle.setStyleSheet("""
        color: #94A3B8;
        font-size: 12px;
        font-weight: 500;
    """)

    title_wrap.addWidget(top_title)
    title_wrap.addWidget(top_subtitle)

    th_layout.addLayout(title_wrap)
    th_layout.addStretch()

    round_badge = QLabel("LIVE GAME")
    round_badge.setAlignment(Qt.AlignCenter)
    round_badge.setFixedHeight(32)
    round_badge.setStyleSheet("""
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 #2563EB, stop:1 #7C3AED);
        color: white;
        border-radius: 12px;
        padding: 0 14px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1px;
    """)
    th_layout.addWidget(round_badge, alignment=Qt.AlignVCenter)

    layout.addWidget(top_header)

    # ----------------------------
    # Main content row
    # ----------------------------
    top = QWidget()
    t_layout = QHBoxLayout(top)
    t_layout.setContentsMargins(0, 0, 0, 0)
    t_layout.setSpacing(18)

    def score_panel(team_name="Team"):
        panel = QFrame()
        panel.setMinimumWidth(190)
        panel.setMaximumWidth(220)
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #0F172A, stop:1 #111827);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 18px;
            }
        """)
        make_shadow(panel, blur=26, color=QColor(0, 0, 0, 110), y=8)

        pl = QVBoxLayout(panel)
        pl.setContentsMargins(16, 16, 16, 16)
        pl.setSpacing(14)

        team_label = QLabel("TEAM")
        team_label.setStyleSheet("""
            color: #60A5FA;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1px;
        """)

        name_btn = QPushButton(team_name)
        name_btn.setFlat(True)
        name_btn.setCursor(Qt.PointingHandCursor)
        name_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                color: #F8FAFC;
                font-size: 18px;
                font-weight: 800;
                border: none;
                padding: 0;
            }
            QPushButton:hover {
                color: #93C5FD;
            }
        """)

        score_title = QLabel("SCORE")
        score_title.setStyleSheet("""
            color: #94A3B8;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
        """)

        score = QLabel("0")
        score.setFixedHeight(110)
        score.setAlignment(Qt.AlignCenter)
        score.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #22C55E, stop:1 #2563EB);
            border-radius: 18px;
            color: white;
            font-size: 34px;
            font-weight: 900;
        """)
        make_shadow(score, blur=24, color=QColor(37, 99, 235, 120), y=6)

        strike = QPushButton("Add Strike")
        strike.setCursor(Qt.PointingHandCursor)
        strike.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #3B82F6, stop:1 #0EA5E9);
                color: white;
                border: none;
                border-radius: 14px;
                padding: 12px;
                font-size: 13px;
                font-weight: 800;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #60A5FA, stop:1 #38BDF8);
            }
            QPushButton:pressed {
                background: #2563EB;
            }
        """)

        strikes_title = QLabel("STRIKES")
        strikes_title.setStyleSheet("""
            color: #94A3B8;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
        """)

        strikes_widget = QWidget()
        s_layout = QHBoxLayout(strikes_widget)
        s_layout.setContentsMargins(0, 0, 0, 0)
        s_layout.setSpacing(8)

        strike_labels = []
        for _ in range(3):
            sx = QLabel("X")
            sx.setFixedSize(32, 32)
            sx.setAlignment(Qt.AlignCenter)
            sx.setStyleSheet("""
                color: #F87171;
                border: 2px solid #EF4444;
                border-radius: 10px;
                background: rgba(239,68,68,0.06);
                font-weight: 900;
                font-size: 14px;
            """)
            sx.setVisible(False)
            strike_labels.append(sx)
            s_layout.addWidget(sx)

        pl.addWidget(team_label)
        pl.addWidget(name_btn)
        pl.addWidget(score_title)
        pl.addWidget(score)
        pl.addWidget(strike)
        pl.addWidget(strikes_title)
        pl.addWidget(strikes_widget)
        pl.addStretch()

        panel._name_btn = name_btn
        panel._score_lbl = score
        panel._strike_btn = strike
        panel._strike_labels = strike_labels
        return panel

    team_a_panel = score_panel("Team A")
    team_b_panel = score_panel("Team B")
    t_layout.addWidget(team_a_panel, stretch=1)

    # ----------------------------
    # Center game board
    # ----------------------------
    board = QFrame()
    board.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    board.setStyleSheet("""
        QFrame {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #071432, stop:0.55 #0B3B8C, stop:1 #041628);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 24px;
        }
    """)
    make_shadow(board, blur=36, color=QColor(10, 132, 255, 120), y=8)

    b_layout = QVBoxLayout(board)
    b_layout.setContentsMargins(18, 18, 18, 18)
    b_layout.setSpacing(16)

    header = QLabel(title or "QUESTION")
    header.setAlignment(Qt.AlignCenter)
    header.setWordWrap(True)
    header.setStyleSheet("""
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 #2563EB, stop:1 #7C3AED);
        color: white;
        padding: 16px 18px;
        font-size: 24px;
        font-weight: 900;
        border-radius: 18px;
    """)
    make_shadow(header, blur=20, color=QColor(79, 70, 229, 90), y=4)
    b_layout.addWidget(header)

    answers = QWidget()
    a_layout = QHBoxLayout(answers)
    a_layout.setContentsMargins(6, 6, 6, 6)
    a_layout.setSpacing(16)

    sample_rounds = [
        {
            "question": "Name a common data structure taught in CS courses:",
            "answers": [
                ("Array", 30),
                ("Linked List", 20),
                ("Stack", 15),
                ("Queue", 10),
                ("Hash Table", 8),
                ("Tree", 7),
                ("Graph", 6),
                ("Heap", 4),
            ],
        },
        {
            "question": "Name a programming language commonly used for teaching:",
            "answers": [
                ("Python", 40),
                ("Java", 25),
                ("C++", 15),
                ("JavaScript", 8),
                ("C", 6),
                ("Ruby", 3),
                ("Haskell", 2),
                ("MATLAB", 1),
            ],
        },
    ]

    page.game_state = {
        "teams": [
            {"name": "Team A", "score": 0, "strikes": 0},
            {"name": "Team B", "score": 0, "strikes": 0},
        ],
        "current_round": None,
        "game_idx": 0,
        "question_idx": 0,
        "answers_widgets": [],
        "fast_money": False,
        "fast_money_team": None,
    }

    def build_answer_boxes():
        for w in page.game_state.get("answers_widgets", []):
            try:
                w.setParent(None)
            except Exception:
                pass
        page.game_state["answers_widgets"] = []

        left = QWidget()
        left_l = QVBoxLayout(left)
        left_l.setSpacing(14)
        left_l.setContentsMargins(0, 0, 0, 0)

        right = QWidget()
        right_l = QVBoxLayout(right)
        right_l.setSpacing(14)
        right_l.setContentsMargins(0, 0, 0, 0)

        answers_data = page.game_state["current_round"]["answers"]
        total_slots = 8

        class FlashCard(QFrame):
            def __init__(self, text: str, pts: int, active: bool = True):
                super().__init__()
                self._answer_text = text or ""
                self._answer_pts = pts or 0
                self._revealed = False
                self._active = bool(active)
                self._reveal_anim = None

                self.setFixedHeight(74)
                self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

                if self._active:
                    self.setStyleSheet("""
                        QFrame {
                            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                                stop:0 #08254A, stop:1 #0B2E63);
                            border: 1px solid rgba(255,255,255,0.07);
                            border-radius: 18px;
                        }
                        QFrame:hover {
                            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                                stop:0 #0A2E5D, stop:1 #123C7A);
                            border: 1px solid rgba(96,165,250,0.35);
                        }
                    """)
                    make_shadow(self, blur=18, color=QColor(0, 0, 0, 90), y=4)
                else:
                    self.setStyleSheet("""
                        QFrame {
                            background: #1E293B;
                            border: 2px dashed #475569;
                            border-radius: 18px;
                        }
                    """)

                hl = QHBoxLayout(self)
                hl.setContentsMargins(16, 0, 16, 0)
                hl.setSpacing(10)

                self._content = QWidget()
                self._content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self._stack = QStackedLayout(self._content)
                self._stack.setContentsMargins(0, 0, 0, 0)

                self.front = QLabel("CLICK TO REVEAL" if self._active else "—")
                self.front.setAlignment(Qt.AlignCenter)
                self.front.setStyleSheet("""
                    background: transparent;
                    border: none;
                    color: #93C5FD;
                    font-weight: 900;
                    font-size: 15px;
                    letter-spacing: 1px;
                """ if self._active else """
                    background: transparent;
                    border: none;
                    color: #94A3B8;
                    font-weight: 800;
                    font-size: 22px;
                """)

                self.back = QLabel(self._answer_text)
                self.back.setAlignment(Qt.AlignCenter)
                self.back.setWordWrap(True)
                self.back.setStyleSheet("""
                    background: transparent;
                    border: none;
                    color: white;
                    font-weight: 900;
                    font-size: 17px;
                """)

                self._stack.addWidget(self.front)
                self._stack.addWidget(self.back)
                self._stack.setCurrentWidget(self.front)

                self._pts_lbl = QLabel(str(self._answer_pts))
                self._pts_lbl.setAlignment(Qt.AlignCenter)
                self._pts_lbl.setFixedSize(64, 42)
                self._pts_lbl.setStyleSheet("""
                    background: qradialgradient(cx:0.3, cy:0.3, radius:1,
                        fx:0.3, fy:0.3, stop:0 #FDE68A, stop:1 #F59E0B);
                    border-radius: 16px;
                    color: #111827;
                    font-size: 18px;
                    font-weight: 900;
                """)
                self._pts_lbl.setVisible(False)

                hl.addWidget(self._content, stretch=1)
                hl.addWidget(self._pts_lbl)

                if not self._active:
                    self.setEnabled(False)
                    self.setCursor(Qt.ArrowCursor)
                else:
                    self.setCursor(Qt.PointingHandCursor)

            def mousePressEvent(self, event):
                if not self._active or self._revealed:
                    return
                self.reveal()

            def ensure_revealed_visible(self):
                if not self._revealed:
                    return
                try:
                    if self._reveal_anim is not None:
                        self._reveal_anim.stop()
                except Exception:
                    pass
                self._stack.setCurrentWidget(self.back)
                self._content.setMaximumWidth(16777215)
                self._pts_lbl.setVisible(True)
                self._reveal_anim = None

            def reveal(self, award: bool = True, animate: bool = True):
                if self._revealed or not self._active:
                    return
                self._revealed = True

                if not animate:
                    self._stack.setCurrentWidget(self.back)
                    self._pts_lbl.setVisible(True)
                    self._content.setMaximumWidth(16777215)
                else:
                    try:
                        if self._reveal_anim is not None:
                            self._reveal_anim.stop()
                    except Exception:
                        pass

                    full_w = max(self._content.width(), self._content.sizeHint().width(), 1)
                    self._content.setMaximumWidth(full_w)

                    shrink = QPropertyAnimation(self._content, b"maximumWidth", self)
                    shrink.setDuration(140)
                    shrink.setStartValue(full_w)
                    shrink.setEndValue(0)
                    shrink.setEasingCurve(QEasingCurve.InOutCubic)

                    expand = QPropertyAnimation(self._content, b"maximumWidth", self)
                    expand.setDuration(170)
                    expand.setStartValue(0)
                    expand.setEndValue(full_w)
                    expand.setEasingCurve(QEasingCurve.InOutCubic)

                    group = QSequentialAnimationGroup(self)
                    group.addAnimation(shrink)

                    def _swap():
                        self._stack.setCurrentWidget(self.back)
                        self._pts_lbl.setVisible(True)

                    shrink.finished.connect(_swap)
                    group.addAnimation(expand)

                    def _finish():
                        self._content.setMaximumWidth(16777215)
                        self._reveal_anim = None

                    group.finished.connect(_finish)
                    self._reveal_anim = group
                    group.start()

                if award:
                    try:
                        award_to_team_dialog(self._answer_pts)
                    except Exception:
                        pass

        class _RevealStabilizer(QObject):
            def eventFilter(self, obj, event):
                try:
                    if event.type() in (QEvent.WindowActivate, QEvent.ApplicationActivate):
                        for card in page.game_state.get("answers_widgets", []):
                            if hasattr(card, "ensure_revealed_visible"):
                                card.ensure_revealed_visible()
                except Exception:
                    pass
                return False

        if not hasattr(page, "_reveal_stabilizer"):
            page._reveal_stabilizer = _RevealStabilizer(page)
            try:
                app.installEventFilter(page._reveal_stabilizer)
            except Exception:
                try:
                    page.installEventFilter(page._reveal_stabilizer)
                except Exception:
                    pass

        for i in range(total_slots):
            if i < len(answers_data):
                text, pts = answers_data[i]
                is_empty = (not str(text).strip()) and (int(pts or 0) == 0)
                card = FlashCard(text, pts, active=(not is_empty))
            else:
                card = FlashCard("", 0, active=False)

            container = QWidget()
            hl = QHBoxLayout(container)
            hl.setContentsMargins(0, 0, 0, 0)
            hl.addWidget(card)

            if i < 4:
                left_l.addWidget(container)
            else:
                right_l.addWidget(container)

            page.game_state["answers_widgets"].append(card)

        a_layout.addWidget(left)
        a_layout.addWidget(right)
        b_layout.addWidget(answers)

    def load_round(round_data, from_db=False):
        page.game_state["current_round"] = round_data
        page.game_state["teams"][0]["score"] = 0
        page.game_state["teams"][1]["score"] = 0
        page.game_state["teams"][0]["strikes"] = 0
        page.game_state["teams"][1]["strikes"] = 0
        page.game_state["from_db"] = bool(from_db)
        page.game_state["fast_money"] = bool(round_data.get("fast_money", False))
        page.game_state["fast_money_team"] = None
        header.setText(round_data["question"])
        update_team_panels()
        build_answer_boxes()
        try:
            update_next_button_state()
        except Exception:
            pass

    def get_db_round(game_idx=0, question_idx=0):
        games = db.load_games()
        if not games:
            return None
        if game_idx < 0 or game_idx >= len(games):
            return None
        game = games[game_idx]
        questions = game.get("questions", [])
        if question_idx < 0 or question_idx >= len(questions):
            return None
        q = questions[question_idx]
        answers = []
        for a in q.get("answers", []):
            text = a.get("text", "") or ""
            score = a.get("score", 0) or 0
            answers.append((text, score))
        return {
            "question": q.get("question", ""),
            "answers": answers,
            "fast_money": bool(q.get("fast_money", False)),
        }

    def load_first_db_round():
        r = get_db_round(game_idx=0, question_idx=0)
        if r is None:
            QMessageBox.warning(page, "No Games", "No game found in database/games.json")
            return
        page.game_state["game_idx"] = 0
        page.game_state["question_idx"] = 0
        load_round(r, from_db=True)

    def award_to_team_dialog(points: int):
        if page.game_state.get("fast_money", False):
            team_idx = page.game_state.get("fast_money_team")
            if team_idx is None:
                msg = QMessageBox(page)
                msg.setWindowTitle("Fast Money Team")
                msg.setText("Select which team is playing Fast Money.")
                ta = msg.addButton(page.game_state["teams"][0]["name"], QMessageBox.AcceptRole)
                tb = msg.addButton(page.game_state["teams"][1]["name"], QMessageBox.AcceptRole)
                msg.addButton("Cancel", QMessageBox.RejectRole)
                msg.exec()
                chosen = msg.clickedButton()
                if chosen == ta:
                    team_idx = 0
                elif chosen == tb:
                    team_idx = 1
                else:
                    return
                page.game_state["fast_money_team"] = team_idx

            page.game_state["teams"][team_idx]["score"] += points
            update_team_panels()
            QMessageBox.information(
                page,
                "Fast Money",
                f"{page.game_state['teams'][team_idx]['name']} earns {points} points in Fast Money."
            )
            return

        msg = QMessageBox(page)
        msg.setWindowTitle("Award Points")
        msg.setText(f"Which team receives {points} points?")
        ta = msg.addButton(page.game_state["teams"][0]["name"], QMessageBox.AcceptRole)
        tb = msg.addButton(page.game_state["teams"][1]["name"], QMessageBox.AcceptRole)
        msg.addButton("Cancel", QMessageBox.RejectRole)
        msg.exec()

        chosen = msg.clickedButton()
        if chosen == ta:
            page.game_state["teams"][0]["score"] += points
        elif chosen == tb:
            page.game_state["teams"][1]["score"] += points
        update_team_panels()

    def update_team_panels():
        team_a_panel._score_lbl.setText(str(page.game_state["teams"][0]["score"]))
        team_b_panel._score_lbl.setText(str(page.game_state["teams"][1]["score"]))
        team_a_panel._name_btn.setText(page.game_state["teams"][0]["name"])
        team_b_panel._name_btn.setText(page.game_state["teams"][1]["name"])

        for i, sx in enumerate(team_a_panel._strike_labels):
            sx.setVisible(i < page.game_state["teams"][0]["strikes"])
        for i, sx in enumerate(team_b_panel._strike_labels):
            sx.setVisible(i < page.game_state["teams"][1]["strikes"])

    def rename_team(idx):
        text, ok = QInputDialog.getText(
            page,
            "Rename Team",
            "Team name:",
            text=page.game_state["teams"][idx]["name"]
        )
        if ok and text:
            page.game_state["teams"][idx]["name"] = text
            update_team_panels()

    def increment_strike(idx):
        page.game_state["teams"][idx]["strikes"] += 1
        if page.game_state["teams"][idx]["strikes"] > 3:
            page.game_state["teams"][idx]["strikes"] = 3
        update_team_panels()
        if page.game_state["teams"][idx]["strikes"] >= 3:
            page.game_state["steal_pending"] = 1 - idx

    def steal_attempt(team_idx):
        text, ok = QInputDialog.getText(
            page,
            "Steal Attempt",
            f"{page.game_state['teams'][team_idx]['name']}, enter your steal answer:"
        )
        if not ok or not text:
            return

        unrevealed = []
        for card in page.game_state["answers_widgets"]:
            try:
                if not getattr(card, "_revealed", True) and getattr(card, "_active", True):
                    unrevealed.append(card)
            except Exception:
                pass

        matched = None
        for card in unrevealed:
            if card._answer_text.strip().lower() == text.strip().lower():
                matched = card
                break

        if matched:
            total = sum(c._answer_pts for c in unrevealed)
            opponent_idx = 1 - team_idx
            opponent_score = page.game_state["teams"][opponent_idx]["score"]

            if total > opponent_score:
                QMessageBox.information(
                    page,
                    "Steal",
                    "Cannot steal more points than the opposing team currently has."
                )
                return

            page.game_state["teams"][team_idx]["score"] += total
            page.game_state["teams"][opponent_idx]["score"] -= total

            for c in unrevealed:
                try:
                    c.reveal(award=False, animate=False)
                except Exception:
                    pass

            update_team_panels()
            QMessageBox.information(
                page,
                "Steal",
                f"Correct! {page.game_state['teams'][team_idx]['name']} steals {total} points."
            )
        else:
            QMessageBox.information(page, "Steal", "Incorrect steal attempt.")

    team_a_panel._name_btn.clicked.connect(lambda: rename_team(0))
    team_b_panel._name_btn.clicked.connect(lambda: rename_team(1))
    team_a_panel._strike_btn.clicked.connect(lambda: increment_strike(0))
    team_b_panel._strike_btn.clicked.connect(lambda: increment_strike(1))

    t_layout.addWidget(board, stretch=4)
    t_layout.addWidget(team_b_panel, stretch=1)
    layout.addWidget(top)

    # ----------------------------
    # Controls row
    # ----------------------------
    controls = QWidget()
    c_layout = QHBoxLayout(controls)
    c_layout.setContentsMargins(0, 0, 0, 0)
    c_layout.setSpacing(12)
    c_layout.addStretch()

    control_buttons = {}

    next_btn = QPushButton("Next Round")
    next_btn.setCursor(Qt.PointingHandCursor)
    next_btn.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #4F46E5, stop:1 #0EA5E9);
            color: white;
            border: none;
            border-radius: 18px;
            padding: 14px 28px;
            font-size: 14px;
            font-weight: 800;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #6366F1, stop:1 #38BDF8);
        }
        QPushButton:disabled {
            background: #334155;
            color: #94A3B8;
        }
    """)
    make_shadow(next_btn, blur=18, color=QColor(79, 70, 229, 110), y=6)
    control_buttons["Next Round"] = next_btn
    c_layout.addWidget(next_btn)
    c_layout.addStretch()

    layout.addWidget(controls)

    def update_next_button_state():
        next_button = control_buttons.get("Next Round")
        if not next_button:
            return

        if page.game_state.get("from_db"):
            gi = page.game_state.get("game_idx", 0)
            qi = page.game_state.get("question_idx", 0)
            has_next = get_db_round(game_idx=gi, question_idx=qi + 1) is not None
            next_button.setEnabled(bool(has_next))
        else:
            qi = page.game_state.get("question_idx", 0)
            has_next = (qi + 1) < len(sample_rounds)
            next_button.setEnabled(bool(has_next))

    def next_round_action():
        if page.game_state.get("from_db"):
            gi = page.game_state.get("game_idx", 0)
            qi = page.game_state.get("question_idx", 0) + 1
            r = get_db_round(game_idx=gi, question_idx=qi)
            if r is None:
                control_buttons["Next Round"].setEnabled(False)
                QMessageBox.information(page, "End", "No more questions in this game.")
                return
            page.game_state["question_idx"] = qi
            load_round(r, from_db=True)
        else:
            qi = page.game_state.get("question_idx", 0) + 1
            if qi < len(sample_rounds):
                page.game_state["question_idx"] = qi
                load_round(sample_rounds[qi], from_db=False)
            else:
                control_buttons["Next Round"].setEnabled(False)

    control_buttons["Next Round"].clicked.connect(next_round_action)

    # ----------------------------
    # Bottom tools row
    # ----------------------------
    bottom = QWidget()
    b_layout2 = QHBoxLayout(bottom)
    b_layout2.setContentsMargins(0, 0, 0, 0)
    b_layout2.setSpacing(12)

    steal = QPushButton("Steal Points")
    steal.setCursor(Qt.PointingHandCursor)
    steal.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #3B82F6, stop:1 #0EA5E9);
            color: white;
            border: none;
            border-radius: 16px;
            padding: 12px 20px;
            font-size: 13px;
            font-weight: 800;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #60A5FA, stop:1 #38BDF8);
        }
    """)
    make_shadow(steal, blur=14, color=QColor(10, 132, 255, 100), y=5)

    add_edit = QPushButton("Add/Edit Q&A")
    add_edit.setCursor(Qt.PointingHandCursor)
    add_edit.setStyleSheet("""
        QPushButton {
            background: transparent;
            color: #E2E8F0;
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 16px;
            padding: 12px 18px;
            font-size: 13px;
            font-weight: 700;
        }
        QPushButton:hover {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(96,165,250,0.28);
        }
    """)

    b_layout2.addWidget(steal)
    b_layout2.addStretch()
    b_layout2.addWidget(add_edit)
    layout.addWidget(bottom)

    def steal_from_bottom():
        dlg = QDialog(page)
        dlg.setModal(True)
        dlg.setWindowTitle("Steal Points")
        dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        dlg.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
        dlg.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        dlg.setWindowFlag(Qt.WindowCloseButtonHint, False)
        dlg.setWindowFlag(Qt.FramelessWindowHint, True)
        dlg.setStyleSheet(game_modal.STYLE)

        dlg_layout = QVBoxLayout(dlg)
        dlg_layout.setContentsMargins(12, 12, 12, 12)
        dlg_layout.setSpacing(8)

        header_row = QHBoxLayout()
        title_label = QLabel("Steal Points")
        title_label.setObjectName("headerTitle")
        header_row.addWidget(title_label)
        header_row.addStretch()
        dlg_layout.addLayout(header_row)

        dlg_layout.addWidget(QLabel("Points to award:"))
        points_input = QLineEdit()
        points_input.setPlaceholderText("Enter number of points")
        points_input.setValidator(QIntValidator(0, 100000, points_input))
        dlg_layout.addWidget(points_input)

        btns = QHBoxLayout()
        ta_btn = QPushButton(page.game_state["teams"][0]["name"])
        tb_btn = QPushButton(page.game_state["teams"][1]["name"])
        cancel_btn = QPushButton("Cancel")

        ta_btn.setCursor(Qt.PointingHandCursor)
        tb_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setCursor(Qt.PointingHandCursor)

        btns.addStretch()
        btns.addWidget(ta_btn)
        btns.addWidget(tb_btn)
        btns.addWidget(cancel_btn)
        btns.addStretch()
        dlg_layout.addLayout(btns)

        def _award_to(team_idx: int):
            txt = points_input.text().strip()
            if not txt:
                QMessageBox.information(dlg, "Invalid", "Please enter a number of points to award.")
                return
            try:
                pts = int(txt)
            except Exception:
                QMessageBox.information(dlg, "Invalid", "Please enter a valid integer.")
                return

            opponent_idx = 1 - team_idx
            opponent_score = page.game_state["teams"][opponent_idx]["score"]
            if pts > opponent_score:
                QMessageBox.information(
                    dlg,
                    "Invalid",
                    "Cannot steal more points than the opposing team currently has."
                )
                return

            page.game_state["teams"][team_idx]["score"] += pts
            page.game_state["teams"][opponent_idx]["score"] -= pts
            update_team_panels()
            dlg.accept()

        ta_btn.clicked.connect(lambda: _award_to(0))
        tb_btn.clicked.connect(lambda: _award_to(1))
        cancel_btn.clicked.connect(dlg.reject)

        dlg.setMinimumWidth(420)
        dlg.adjustSize()
        points_input.setFocus()
        dlg.exec()

    steal.clicked.connect(steal_from_bottom)

    # ----------------------------
    # Navigation row
    # ----------------------------
    nav = QWidget()
    n_layout = QHBoxLayout(nav)
    n_layout.setContentsMargins(0, 0, 0, 0)
    n_layout.setSpacing(12)
    n_layout.addStretch()

    back_btn = QPushButton("Back to Board")
    back_btn.setCursor(Qt.PointingHandCursor)
    back_btn.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #4F46E5, stop:1 #0EA5E9);
            color: white;
            border: none;
            border-radius: 16px;
            padding: 12px 22px;
            font-size: 13px;
            font-weight: 800;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #6366F1, stop:1 #38BDF8);
        }
    """)

    display_btn = QPushButton("Display Game")
    display_btn.setCursor(Qt.PointingHandCursor)
    display_btn.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #10B981, stop:1 #22C55E);
            color: white;
            border: none;
            border-radius: 16px;
            padding: 12px 22px;
            font-size: 13px;
            font-weight: 900;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #34D399, stop:1 #4ADE80);
        }
    """)

    back_btn.clicked.connect(app.show_home)
    display_btn.clicked.connect(lambda t=title, d=description: display_game.open_display_game(app, t or "", d or ""))

    n_layout.addWidget(back_btn)
    n_layout.addWidget(display_btn)
    layout.addWidget(nav)

    def _get_current_round_data():
        return page.game_state.get("current_round")

    page.get_current_round_data = _get_current_round_data

    def get_opened_game_round(app_ref):
        try:
            pw = getattr(app_ref, "play_widget", None)
            if pw and hasattr(pw, "game_state"):
                return pw.game_state.get("current_round")
        except Exception:
            pass
        return None

    app.play_widget = page

    if load_db_first:
        try:
            load_first_db_round()
        except Exception:
            pass
    else:
        try:
            load_round(sample_rounds[0], from_db=False)
        except Exception:
            pass

    try:
        app.stack.addWidget(page)
        app.stack.setCurrentWidget(page)
    except Exception:
        try:
            app.show_static_modal("Play", "Could not open play page.")
        except Exception:
            pass