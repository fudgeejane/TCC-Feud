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
    QCheckBox,
    QButtonGroup,
    QStackedLayout,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import (
    Qt,
    QEvent,
    QObject,
    QTimer,
    QEasingCurve,
    QPropertyAnimation,
    QSequentialAnimationGroup,
)
from PySide6.QtGui import QFont, QColor, QIntValidator, QPixmap
import utils.game_modal as game_modal
import modules.display_game as display_game
import database.db as db

try:
    import modules.modify_game as modify_game
except Exception:
    modify_game = None


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
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #040B1A, stop:0.45 #071A3A, stop:1 #041025);
            color: #E2E8F0;
            font-family: Segoe UI, Arial, sans-serif;
        }
        QToolTip {
            background: #0B2448;
            color: #EAF4FF;
            border: 1px solid rgba(125, 211, 252, 0.55);
            padding: 6px 8px;
            border-radius: 8px;
        }
    """)

    layout = QVBoxLayout(page)
    layout.setContentsMargins(60, 30, 60, 30)
    layout.setSpacing(22)

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
            background: none;
            border: none;
            border-radius: 18px;
        }
    """)
    make_shadow(top_header, blur=28, color=QColor(0, 0, 0, 120), y=8)

    th_layout = QHBoxLayout(top_header)
    th_layout.setContentsMargins(0, 0, 0, 0)
    th_layout.setSpacing(18)

    title_wrap = QVBoxLayout()
    title_wrap.setSpacing(2)

    top_title = QLabel()
    try:
        from pathlib import Path

        assets_logo = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
        if assets_logo.exists():
            pix = QPixmap(str(assets_logo))
            if not pix.isNull():
                top_title.setPixmap(pix.scaledToWidth(280, Qt.SmoothTransformation))
            else:
                top_title.setText(title or "Family Feud")
        else:
            top_title.setText(title or "Family Feud")
    except Exception:
        top_title.setText(title or "Family Feud")

    if top_title.text():
        top_title.setStyleSheet("""
            color: #F4F8FF;
            font-size: 24px;
            font-weight: 900;
        """)

    title_wrap.addWidget(top_title)

    th_layout.addLayout(title_wrap)
    th_layout.addStretch()

    top_actions = QHBoxLayout()
    top_actions.setContentsMargins(0, 0, 0, 0)
    top_actions.setSpacing(10)
    th_layout.addLayout(top_actions)

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
                    stop:0 #091A36, stop:1 #0A2144);
                border: none;
                border-radius: 18px;
            }
        """)
        make_shadow(panel, blur=26, color=QColor(0, 0, 0, 110), y=8)

        pl = QVBoxLayout(panel)
        pl.setContentsMargins(16, 16, 16, 16)
        pl.setSpacing(14)

        team_label = QLabel("TEAM")
        team_label.setStyleSheet("""
            color: #7DD3FC;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1px;
            border: none;
                background: none;
        """)

        name_btn = QPushButton(team_name)
        name_btn.setFlat(True)
        name_btn.setCursor(Qt.PointingHandCursor)
        name_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                color: #F1F5F9;
                font-size: 18px;
                font-weight: 800;
                border: none;
                padding: 0;
                background: none;
            }
            QPushButton:hover {
                color: #BAE6FD;
            }
        """)

        score_title = QLabel("SCORE")
        score_title.setStyleSheet("""
            color: #9FB8D1;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            border: none;
        """)

        members_title = QLabel("MEMBERS")
        members_title.setStyleSheet("""
            color: #9FB8D1;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            border: none;
            background: none;
        """)

        members_widget = QWidget()
        m_layout = QVBoxLayout(members_widget)
        m_layout.setContentsMargins(0, 0, 0, 0)
        m_layout.setSpacing(4)

        member_labels = []
        for _ in range(4):
            ml = QLabel("-")
            ml.setStyleSheet("""
                color: #CFE7FF;
                font-size: 11px;
                font-weight: 600;
                border: none;
                background: none;
            """)
            member_labels.append(ml)
            m_layout.addWidget(ml)

        score = QLabel("0")
        score.setFixedHeight(110)
        score.setAlignment(Qt.AlignCenter)
        score.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #14B8A6, stop:1 #0EA5E9);
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
                    stop:0 #0EA5E9, stop:1 #0284C7);
                color: white;
                border: none;
                border-radius: 14px;
                padding: 12px;
                font-size: 13px;
                font-weight: 800;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #38BDF8, stop:1 #0EA5E9);
            }
            QPushButton:pressed {
                background: #0369A1;
            }
        """)

        strikes_title = QLabel("STRIKES")
        strikes_title.setStyleSheet("""
            color: #9FB8D1;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            border: none;
                                    background: none;
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
        pl.addWidget(members_title)
        pl.addWidget(members_widget)
        pl.addWidget(score_title)
        pl.addWidget(score)
        pl.addWidget(strike)
        pl.addWidget(strikes_title)
        pl.addWidget(strikes_widget)
        pl.addStretch()

        panel._name_btn = name_btn
        panel._member_labels = member_labels
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
                stop:0 #05214A, stop:0.55 #0B3A72, stop:1 #05274E);
            border: 1px solid rgba(125, 211, 252, 0.24);
            border-radius: 24px;
        }
    """)
    make_shadow(board, blur=36, color=QColor(10, 132, 255, 120), y=8)

    b_layout = QVBoxLayout(board)
    b_layout.setContentsMargins(18, 18, 18, 18)
    b_layout.setSpacing(16)

    round_badge = QLabel("LIVE GAME")
    round_badge.setAlignment(Qt.AlignCenter)
    round_badge.setFixedHeight(32)
    round_badge.setStyleSheet("""
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 #0EA5E9, stop:1 #2563EB);
        color: white;
        border-radius: 12px;
        padding: 0 14px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1px;
    """)
    b_layout.addWidget(round_badge)

    header = QLabel(title or "QUESTION")
    header.setAlignment(Qt.AlignCenter)
    header.setWordWrap(True)
    header.setStyleSheet("""
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 #0284C7, stop:1 #0369A1);
        color: white;
        padding: 16px 20px;
        font-size: 23px;
        font-weight: 900;
        border-radius: 18px;
    """)
    make_shadow(header, blur=20, color=QColor(3, 105, 161, 100), y=4)
    b_layout.addWidget(header)

  
    answers = QWidget()
    a_layout = QHBoxLayout(answers)
    a_layout.setContentsMargins(6, 6, 6, 6)
    a_layout.setSpacing(16)

    # -- Answering team selector bar (replaces cheat sheet) --
    answering_bar = QFrame()
    answering_bar.setStyleSheet("""
        QFrame {
            background: rgba(2, 12, 28, 0.55);
            border: 1px solid rgba(125, 211, 252, 0.22);
            border-radius: 14px;
        }
    """)
    answering_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    ab_layout = QHBoxLayout(answering_bar)
    ab_layout.setContentsMargins(14, 10, 14, 10)
    ab_layout.setSpacing(16)

    ab_title = QLabel("CURRENTLY ANSWERING:")
    ab_title.setStyleSheet("""
        color: #7DD3FC;
        font-size: 11px;
        font-weight: 900;
        letter-spacing: 1px;
        border: none;
        background: transparent;
    """)
    ab_layout.addWidget(ab_title)

    answering_team_a_btn = QPushButton("Team A")
    answering_team_b_btn = QPushButton("Team B")
    answering_steal_btn = QPushButton("⚡ Steal")

    _answering_btn_base = """
        QPushButton {{
            background: {bg};
            color: {fg};
            border: 2px solid {border};
            border-radius: 10px;
            padding: 6px 18px;
            font-size: 12px;
            font-weight: 800;
        }}
        QPushButton:hover {{
            background: {hover};
            border-color: {hover_border};
        }}
    """

    def _answering_btn_style(active: bool, color: str = "#0EA5E9"):
        if active:
            return _answering_btn_base.format(
                bg=color, fg="white",
                border=color, hover=color, hover_border=color
            )
        return _answering_btn_base.format(
            bg="rgba(255,255,255,0.04)", fg="#94A3B8",
            border="rgba(125,211,252,0.18)", hover="rgba(125,211,252,0.10)", hover_border="rgba(125,211,252,0.35)"
        )

    def _update_answering_buttons():
        ctrl = page.game_state.get("current_control_team")
        names = [t["name"] for t in page.game_state["teams"]]
        answering_team_a_btn.setText(names[0])
        answering_team_b_btn.setText(names[1])
        answering_team_a_btn.setStyleSheet(_answering_btn_style(ctrl == 0, "#0EA5E9"))
        answering_team_b_btn.setStyleSheet(_answering_btn_style(ctrl == 1, "#10B981"))
        # Steal button: enabled only when a team is locked out and steal not yet used
        locked_out = page.game_state.get("locked_out_team")
        steal_used = page.game_state.get("steal_used", False)
        can_steal = (locked_out in (0, 1)) and (not steal_used)
        answering_steal_btn.setEnabled(can_steal)
        steal_active = (ctrl == "steal")
        answering_steal_btn.setStyleSheet(_answering_btn_style(steal_active, "#F59E0B"))

    answering_team_a_btn.setCursor(Qt.PointingHandCursor)
    answering_team_b_btn.setCursor(Qt.PointingHandCursor)
    answering_steal_btn.setCursor(Qt.PointingHandCursor)

    def _set_answering_team(idx):
        """Set which team is currently answering; scores will auto-award to them."""
        page.game_state["current_control_team"] = idx
        _update_answering_buttons()
        sync_audience_display()

    def _trigger_steal_from_bar():
        """Trigger the steal attempt from the answering bar for the opposing team."""
        locked_out_team = page.game_state.get("locked_out_team")
        if locked_out_team not in (0, 1):
            show_info_modal("Steal", "Steal is only available after a team reaches 3 strikes.")
            return
        if page.game_state.get("steal_used", False):
            show_info_modal("Steal", "Steal was already used this round.")
            return
        steal_attempt(1 - locked_out_team)

    answering_team_a_btn.clicked.connect(lambda: _set_answering_team(0))
    answering_team_b_btn.clicked.connect(lambda: _set_answering_team(1))
    answering_steal_btn.clicked.connect(_trigger_steal_from_bar)

    ab_layout.addWidget(answering_team_a_btn)
    ab_layout.addWidget(answering_team_b_btn)
    ab_layout.addWidget(answering_steal_btn)
    ab_layout.addStretch()

    ab_hint = QLabel("Select the answering team to auto-award points. Use ⚡ Steal when a team hits 3 strikes.")
    ab_hint.setStyleSheet("""
        color: rgba(148, 163, 184, 0.7);
        font-size: 10px;
        border: none;
        background: transparent;
    """)
    ab_layout.addWidget(ab_hint)

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
            {"name": "Team A", "members": ["", "", "", ""], "score": 0, "strikes": 0},
            {"name": "Team B", "members": ["", "", "", ""], "score": 0, "strikes": 0},
        ],
        "round_points": [0, 0],
        "current_round": None,
        "current_round_number": 1,
        "total_rounds": len(sample_rounds),
        "game_idx": 0,
        "question_idx": 0,
        "answers_widgets": [],
        "revealed_answer_indices": [],
        "fast_money": False,
        "fast_money_team": None,
        "current_control_team": None,
        "locked_out_team": None,
        "steal_used": False,
        "game_finished": False,
    }

    def sync_audience_display():
        try:
            dw = getattr(app, "display_window", None)
            if dw is not None and hasattr(dw, "_refresh_display"):
                if getattr(dw, "_refresh_pending", False):
                    return

                dw._refresh_pending = True

                def _run_refresh():
                    try:
                        if hasattr(dw, "_refresh_display"):
                            dw._refresh_display()
                    except Exception:
                        pass
                    finally:
                        try:
                            dw._refresh_pending = False
                        except Exception:
                            pass

                # Queue refresh for next event-loop cycle to avoid paint re-entrancy.
                QTimer.singleShot(0, _run_refresh)
        except Exception:
            pass

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
            def __init__(self, text: str, pts: int, active: bool = True, rank: int = 1, slot_idx: int = -1):
                super().__init__()
                self._answer_text = text or ""
                self._answer_pts = pts or 0
                self._revealed = False
                self._consumed = False
                self._active = bool(active)
                self._reveal_anim = None
                self._slot_index = slot_idx

                self.setFixedHeight(76)
                self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

                if self._active:
                    self.setStyleSheet("""
                        QFrame {
                            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                                stop:0 #082952, stop:1 #0B366B);
                            border: 1px solid rgba(125, 211, 252, 0.18);
                            border-radius: 18px;
                        }
                        QFrame:hover {
                            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                                stop:0 #0A3368, stop:1 #134983);
                            border: 1px solid rgba(125, 211, 252, 0.45);
                        }
                    """)
                    make_shadow(self, blur=18, color=QColor(0, 0, 0, 90), y=4)
                else:
                    self.setStyleSheet("""
                        QFrame {
                            background: #112744;
                            border: 2px dashed #3B5A7D;
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

                # Front shows the answer text always; back is the "revealed" highlighted state
                self.front = QLabel(self._answer_text if self._active else "—")
                self.front.setAlignment(Qt.AlignCenter)
                self.front.setWordWrap(True)
                self.front.setStyleSheet("""
                    background: transparent;
                    border: none;
                    color: #BAE6FD;
                    font-weight: 800;
                    font-size: 15px;
                """ if self._active else """
                    background: transparent;
                    border: none;
                    color: #8BA4BF;
                    font-weight: 800;
                    font-size: 22px;
                """)

                # Front wrapper: answer text + subtle "click to reveal" hint below
                front_container = QWidget()
                front_container.setStyleSheet("background: transparent; border: none;")
                fc_layout = QVBoxLayout(front_container)
                fc_layout.setContentsMargins(0, 2, 0, 2)
                fc_layout.setSpacing(2)
                fc_layout.setAlignment(Qt.AlignCenter)
                fc_layout.addWidget(self.front)
                if self._active:
                    hint_lbl = QLabel("CLICK TO REVEAL")
                    hint_lbl.setAlignment(Qt.AlignCenter)
                    hint_lbl.setStyleSheet("""
                        background: transparent;
                        border: none;
                        color: rgba(125, 211, 252, 0.45);
                        font-size: 9px;
                        font-weight: 700;
                        letter-spacing: 1px;
                    """)
                    fc_layout.addWidget(hint_lbl)

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

                self._stack.addWidget(front_container)
                self._stack.addWidget(self.back)
                self._stack.setCurrentWidget(front_container)

                self._pts_lbl = QLabel(str(self._answer_pts))
                self._pts_lbl.setAlignment(Qt.AlignCenter)
                self._pts_lbl.setFixedSize(64, 42)
                self._pts_lbl.setStyleSheet("""
                    background: qradialgradient(cx:0.3, cy:0.3, radius:1,
                        fx:0.3, fy:0.3, stop:0 #FDE68A, stop:1 #F97316);
                    border-radius: 16px;
                    color: #111827;
                    font-size: 18px;
                    font-weight: 900;
                """)
                self._pts_lbl.setVisible(False)

                self._rank_lbl = QLabel(str(rank))
                self._rank_lbl.setAlignment(Qt.AlignCenter)
                self._rank_lbl.setFixedSize(32, 32)
                self._rank_lbl.setStyleSheet("""
                    background: rgba(14, 165, 233, 0.22);
                    border: 1px solid rgba(125, 211, 252, 0.35);
                    border-radius: 10px;
                    color: #E0F2FE;
                    font-size: 13px;
                    font-weight: 900;
                """)

                hl.addWidget(self._rank_lbl)
                hl.addWidget(self._content, stretch=1)
                hl.addWidget(self._pts_lbl)

                if not self._active:
                    self.setEnabled(False)
                    self.setCursor(Qt.ArrowCursor)
                else:
                    self.setCursor(Qt.PointingHandCursor)
                    self.setToolTip("Reveal this answer")

            def mousePressEvent(self, event):
                if not self._active or self._revealed or self._consumed:
                    return
                # Block reveal if no answering team is selected (and not locked-out/fast-money)
                ctrl = page.game_state.get("current_control_team")
                locked_out = page.game_state.get("locked_out_team")
                fast_money = page.game_state.get("fast_money", False)
                auto_team = locked_out in (0, 1) or fast_money
                if ctrl not in (0, 1) and not auto_team:
                    self.setToolTip("Select an answering team first!")
                    try:
                        from PySide6.QtWidgets import QToolTip
                        QToolTip.showText(
                            self.mapToGlobal(self.rect().center()),
                            "⚠ Select an answering team first!",
                            self
                        )
                    except Exception:
                        pass
                    return
                self._consumed = True
                self.setCursor(Qt.ArrowCursor)
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
                    try:
                        revealed = page.game_state.setdefault("revealed_answer_indices", [])
                        if self._slot_index not in revealed and self._slot_index >= 0:
                            revealed.append(self._slot_index)
                    except Exception:
                        pass
                    try:
                        sync_audience_display()
                    except Exception:
                        pass
                else:
                    try:
                        revealed = page.game_state.setdefault("revealed_answer_indices", [])
                        if self._slot_index not in revealed and self._slot_index >= 0:
                            revealed.append(self._slot_index)
                    except Exception:
                        pass
                    try:
                        sync_audience_display()
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
                card = FlashCard(text, pts, active=(not is_empty), rank=i + 1, slot_idx=i)
            else:
                card = FlashCard("", 0, active=False, rank=i + 1, slot_idx=i)

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
        page.game_state["revealed_answer_indices"] = []
        page.game_state["round_points"] = [0, 0]
        page.game_state["teams"][0]["strikes"] = 0
        page.game_state["teams"][1]["strikes"] = 0
        page.game_state["current_round_number"] = page.game_state.get("question_idx", 0) + 1
        page.game_state["from_db"] = bool(from_db)
        page.game_state["fast_money"] = bool(round_data.get("fast_money", False))
        page.game_state["fast_money_team"] = None
        page.game_state["current_control_team"] = None
        page.game_state["locked_out_team"] = None
        page.game_state["steal_used"] = False
        page.game_state["game_finished"] = False
        header.setText(round_data["question"])
        update_team_panels()
        build_answer_boxes()
        _update_answering_buttons()
        try:
            update_next_button_state()
        except Exception:
            pass

        try:
            if page.game_state.get("from_db"):
                round_number = page.game_state.get("question_idx", 0) + 1
            else:
                round_number = page.game_state.get("question_idx", 0) + 1
            status = f"ROUND {round_number}"
            if page.game_state.get("fast_money"):
                status += " • FAST MONEY"
            round_badge.setText(status)
        except Exception:
            round_badge.setText("LIVE GAME")

        sync_audience_display()

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

    def get_db_teams(game_idx=0):
        games = db.load_games()
        if not games:
            return None
        if game_idx < 0 or game_idx >= len(games):
            return None

        game = games[game_idx]
        teams = game.get("teams", [])
        if not isinstance(teams, list):
            teams = []

        out = []
        for i in range(2):
            team = teams[i] if i < len(teams) and isinstance(teams[i], dict) else {}
            name = str(team.get("name", f"Team {chr(ord('A') + i)}") or f"Team {chr(ord('A') + i)}")
            members = team.get("members", [])
            if not isinstance(members, list):
                members = []
            members = [(str(members[j]) if j < len(members) else "") for j in range(4)]
            out.append({"name": name, "members": members})
        return out

    def apply_teams(teams_data):
        if not teams_data or not isinstance(teams_data, list):
            return
        for i in range(2):
            if i >= len(page.game_state["teams"]):
                continue
            data = teams_data[i] if i < len(teams_data) and isinstance(teams_data[i], dict) else {}
            page.game_state["teams"][i]["name"] = str(data.get("name", page.game_state["teams"][i]["name"]))
            members = data.get("members", [])
            if not isinstance(members, list):
                members = []
            page.game_state["teams"][i]["members"] = [(str(members[j]) if j < len(members) else "") for j in range(4)]

    def load_first_db_round():
        r = get_db_round(game_idx=0, question_idx=0)
        if r is None:
            QMessageBox.warning(page, "No Games", "No game found in database/games.json")
            return
        try:
            games = db.load_games()
            questions = games[0].get("questions", []) if games and len(games) > 0 else []
            page.game_state["total_rounds"] = max(1, len(questions))
        except Exception:
            page.game_state["total_rounds"] = 1
        page.game_state["game_idx"] = 0
        page.game_state["question_idx"] = 0
        try:
            apply_teams(get_db_teams(game_idx=0))
        except Exception:
            pass
        load_round(r, from_db=True)

    def award_to_team_dialog(points: int):
        """Award points to the currently selected answering team. No dialog shown."""
        # Fast money: use fast_money_team (already set when round started)
        if page.game_state.get("fast_money", False):
            team_idx = page.game_state.get("fast_money_team")
            if team_idx not in (0, 1):
                team_idx = page.game_state.get("current_control_team", 0)
            page.game_state["teams"][team_idx]["score"] += points
            page.game_state["round_points"][team_idx] += points
            page.game_state["current_control_team"] = team_idx
            _update_answering_buttons()
            update_team_panels()
            sync_audience_display()
            return

        # Locked-out: opposing team auto-receives
        locked_out_team = page.game_state.get("locked_out_team")
        if locked_out_team in (0, 1):
            team_idx = 1 - locked_out_team
            page.game_state["teams"][team_idx]["score"] += points
            page.game_state["round_points"][team_idx] += points
            page.game_state["current_control_team"] = team_idx
            _update_answering_buttons()
            update_team_panels()
            sync_audience_display()
            return

        # Normal: use whichever team is selected in the answering bar
        team_idx = page.game_state.get("current_control_team")
        if team_idx not in (0, 1):
            return  # No team selected — reveal was already blocked in mousePressEvent
        page.game_state["teams"][team_idx]["score"] += points
        page.game_state["round_points"][team_idx] += points
        _update_answering_buttons()
        update_team_panels()
        sync_audience_display()

    def show_info_modal(window_title: str, message: str, button_text: str = "OK"):
        dlg = QDialog(page)
        dlg.setModal(True)
        dlg.setWindowTitle(window_title)
        dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        dlg.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
        dlg.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        dlg.setWindowFlag(Qt.WindowCloseButtonHint, False)
        dlg.setWindowFlag(Qt.FramelessWindowHint, True)
        dlg.setStyleSheet(game_modal.STYLE)

        dlg_layout = QVBoxLayout(dlg)
        dlg_layout.setContentsMargins(12, 12, 12, 12)
        dlg_layout.setSpacing(10)

        title_label = QLabel(window_title)
        title_label.setObjectName("headerTitle")
        title_label.setStyleSheet("background: none;")
        dlg_layout.addWidget(title_label)

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("background: none;")
        dlg_layout.addWidget(message_label)

        btn_row = QHBoxLayout()
        ok_btn = QPushButton(button_text)
        ok_btn.setObjectName("okBtn")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.clicked.connect(dlg.accept)
        btn_row.addStretch()
        btn_row.addWidget(ok_btn)
        dlg_layout.addLayout(btn_row)

        dlg.setMinimumWidth(450)
        dlg.adjustSize()
        return dlg.exec() == QDialog.Accepted

    def prompt_single_check_modal(window_title: str, message: str, options):
        dlg = QDialog(page)
        dlg.setModal(True)
        dlg.setWindowTitle(window_title)
        dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        dlg.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
        dlg.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        dlg.setWindowFlag(Qt.WindowCloseButtonHint, False)
        dlg.setWindowFlag(Qt.FramelessWindowHint, True)
        dlg.setStyleSheet(game_modal.STYLE)

        dlg_layout = QVBoxLayout(dlg)
        dlg_layout.setContentsMargins(12, 12, 12, 12)
        dlg_layout.setSpacing(10)

        title_label = QLabel(window_title)
        title_label.setObjectName("headerTitle")
        title_label.setStyleSheet("background: none;")
        dlg_layout.addWidget(title_label)

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("background: none;")
        dlg_layout.addWidget(message_label)

        selected = {"text": ""}
        btn_group = QButtonGroup(dlg)
        btn_group.setExclusive(True)

        for idx, option_text in enumerate(options):
            check = QCheckBox(str(option_text))
            check.setCursor(Qt.PointingHandCursor)
            check.setStyleSheet("background: none;")
            btn_group.addButton(check, idx)
            dlg_layout.addWidget(check)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        submit_btn = QPushButton("Submit")
        cancel_btn.setObjectName("cancelBtn")
        submit_btn.setObjectName("createBtn")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.setEnabled(False)

        def _on_choice_change():
            checked = btn_group.checkedButton()
            submit_btn.setEnabled(checked is not None)
            if checked is not None:
                selected["text"] = checked.text().strip()

        btn_group.buttonToggled.connect(lambda _btn, _checked: _on_choice_change())
        cancel_btn.clicked.connect(dlg.reject)
        submit_btn.clicked.connect(dlg.accept)

        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(submit_btn)
        dlg_layout.addLayout(btn_row)

        dlg.setMinimumWidth(500)
        dlg.adjustSize()

        ok = dlg.exec() == QDialog.Accepted
        return selected["text"], ok

    def update_team_panels():
        team_a_panel._score_lbl.setText(str(page.game_state["teams"][0]["score"]))
        team_b_panel._score_lbl.setText(str(page.game_state["teams"][1]["score"]))
        team_a_panel._name_btn.setText(page.game_state["teams"][0]["name"])
        team_b_panel._name_btn.setText(page.game_state["teams"][1]["name"])

        team_a_members = page.game_state["teams"][0].get("members", [])
        team_b_members = page.game_state["teams"][1].get("members", [])
        for i, ml in enumerate(team_a_panel._member_labels):
            value = team_a_members[i] if i < len(team_a_members) else ""
            ml.setText(value if str(value).strip() else "-")
        for i, ml in enumerate(team_b_panel._member_labels):
            value = team_b_members[i] if i < len(team_b_members) else ""
            ml.setText(value if str(value).strip() else "-")

        for i, sx in enumerate(team_a_panel._strike_labels):
            sx.setVisible(i < page.game_state["teams"][0]["strikes"])
        for i, sx in enumerate(team_b_panel._strike_labels):
            sx.setVisible(i < page.game_state["teams"][1]["strikes"])
        try:
            _update_answering_buttons()
        except Exception:
            pass

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
        if page.game_state.get("locked_out_team") in (0, 1):
            return

        page.game_state["teams"][idx]["strikes"] += 1
        if page.game_state["teams"][idx]["strikes"] > 3:
            page.game_state["teams"][idx]["strikes"] = 3
        update_team_panels()
        sync_audience_display()

        if page.game_state["teams"][idx]["strikes"] >= 3:
            page.game_state["locked_out_team"] = idx
            page.game_state["steal_pending"] = 1 - idx
            page.game_state["current_control_team"] = 1 - idx
            stealing_team = page.game_state["teams"][1 - idx]["name"]
            start_steal_clicked = show_info_modal(
                "Team Locked Out",
                f"{page.game_state['teams'][idx]['name']} reached 3 strikes and is locked out for the rest of this round.\n\n"
                f"Only {stealing_team} can score until the next round.",
                button_text="Start Steal"
            )
            try:
                _update_answering_buttons()
            except Exception:
                pass
            if start_steal_clicked:
                try:
                    steal_attempt(1 - idx)
                except Exception:
                    pass
            sync_audience_display()

    def steal_attempt(team_idx):
        if page.game_state.get("steal_used", False):
            show_info_modal("Steal", "Steal was already used in this round.")
            return

        locked_out_team = page.game_state.get("locked_out_team")
        if locked_out_team not in (0, 1):
            show_info_modal("Steal", "No team is locked out in this round.")
            return

        if team_idx != (1 - locked_out_team):
            show_info_modal("Steal", "Only the opposing team may attempt a steal.")
            return

        unrevealed = []
        for card in page.game_state["answers_widgets"]:
            try:
                if not getattr(card, "_revealed", True) and getattr(card, "_active", True):
                    unrevealed.append(card)
            except Exception:
                pass

        if not unrevealed:
            show_info_modal("Steal", "No unrevealed answers left to steal.")
            return

        choices = [card._answer_text.strip() for card in unrevealed if card._answer_text.strip()]
        if not choices:
            show_info_modal("Steal", "No valid steal choices are available.")
            return

        text, ok = prompt_single_check_modal(
            "Steal Attempt",
            f"{page.game_state['teams'][team_idx]['name']}, choose one steal answer:",
            choices
        )
        if not ok or not text:
            return

        matched = None
        for card in unrevealed:
            if card._answer_text.strip().lower() == text.strip().lower():
                matched = card
                break

        if matched:
            opponent_idx = locked_out_team
            transferred = page.game_state["round_points"][opponent_idx]
            try:
                matched_points = int(getattr(matched, "_answer_pts", 0) or 0)
            except Exception:
                matched_points = 0

            page.game_state["teams"][team_idx]["score"] += transferred + matched_points
            page.game_state["round_points"][team_idx] += transferred + matched_points
            page.game_state["teams"][opponent_idx]["score"] -= transferred
            if page.game_state["teams"][opponent_idx]["score"] < 0:
                page.game_state["teams"][opponent_idx]["score"] = 0
            page.game_state["round_points"][opponent_idx] = 0
            page.game_state["steal_used"] = True
            page.game_state["current_control_team"] = team_idx

            for c in unrevealed:
                try:
                    c.reveal(award=False, animate=False)
                except Exception:
                    pass

            update_team_panels()
            try:
                _update_answering_buttons()
            except Exception:
                pass
            sync_audience_display()
            show_info_modal(
                "Steal Success",
                f"Correct! {page.game_state['teams'][team_idx]['name']} steals all points earned this round by "
                f"{page.game_state['teams'][opponent_idx]['name']} ({transferred} points) and also earns "
                f"{matched_points} points for the stolen answer.",
                button_text="Nice"
            )
        else:
            page.game_state["steal_used"] = True
            try:
                _update_answering_buttons()
            except Exception:
                pass
            sync_audience_display()
            show_info_modal(
                "Steal Miss",
                f"Incorrect steal attempt. Points remain with {page.game_state['teams'][locked_out_team]['name']}."
            )

    team_a_panel._name_btn.clicked.connect(lambda: rename_team(0))
    team_b_panel._name_btn.clicked.connect(lambda: rename_team(1))
    team_a_panel._strike_btn.clicked.connect(lambda: increment_strike(0))
    team_b_panel._strike_btn.clicked.connect(lambda: increment_strike(1))

    t_layout.addWidget(board, stretch=4)
    t_layout.addWidget(team_b_panel, stretch=1)

    control_buttons = {}

    next_btn = QPushButton("Next Round")
    next_btn.setCursor(Qt.PointingHandCursor)
    next_btn.setToolTip("Load the next question")
    next_btn.setStyleSheet("""
        QPushButton {
            background: none;
            color: #E2E8F0;
            border: 1px solid rgba(125, 211, 252, 0.35);
            border-radius: 18px;
            padding: 14px 28px;
            font-size: 14px;
            font-weight: 800;
        }
        QPushButton:hover {
            background: rgba(125, 211, 252, 0.10);
            border: 1px solid rgba(125, 211, 252, 0.55);
        }
        QPushButton:disabled {
            background: none;
            color: #94A3B8;
            border: 1px solid rgba(148, 163, 184, 0.25);
        }
    """)
    make_shadow(next_btn, blur=18, color=QColor(14, 165, 233, 120), y=6)
    control_buttons["Next Round"] = next_btn

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

    def mark_game_finished():
        page.game_state["game_finished"] = True
        sync_audience_display()

    def next_round_action():
        if page.game_state.get("from_db"):
            gi = page.game_state.get("game_idx", 0)
            qi = page.game_state.get("question_idx", 0) + 1
            r = get_db_round(game_idx=gi, question_idx=qi)
            if r is None:
                control_buttons["Next Round"].setEnabled(False)
                mark_game_finished()
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
                mark_game_finished()

    control_buttons["Next Round"].clicked.connect(next_round_action)

    # ----------------------------
    # Navigation row
    # ----------------------------
    back_btn = QPushButton("Back to Board")
    back_btn.setCursor(Qt.PointingHandCursor)
    back_btn.setToolTip("Return to the home board")
    back_btn.setStyleSheet("""
        QPushButton {
            background: none;
            color: #E2E8F0;
            border: 1px solid rgba(125, 211, 252, 0.35);
            border-radius: 16px;
            padding: 12px 22px;
            font-size: 13px;
            font-weight: 800;
        }
        QPushButton:hover {
            background: rgba(125, 211, 252, 0.10);
            border: 1px solid rgba(125, 211, 252, 0.55);
        }
    """)

    display_btn = QPushButton("Display Game")
    display_btn.setCursor(Qt.PointingHandCursor)
    display_btn.setToolTip("Open the presentation display")
    display_btn.setStyleSheet("""
        QPushButton {
            background: none;
            color: #E2E8F0;
            border: 1px solid rgba(125, 211, 252, 0.35);
            border-radius: 16px;
            padding: 12px 22px;
            font-size: 13px;
            font-weight: 900;
        }
        QPushButton:hover {
            background: rgba(125, 211, 252, 0.10);
            border: 1px solid rgba(125, 211, 252, 0.55);
        }
    """)

    def back_to_board_action():
        try:
            if modify_game and hasattr(modify_game, "open_modify_game"):
                modify_game.open_modify_game(app, title or "Family Feud", description or "")
                return
        except Exception:
            pass
        app.show_home()

    back_btn.clicked.connect(back_to_board_action)
    display_btn.clicked.connect(lambda t=title, d=description: display_game.open_display_game(app, t or "", d or ""))

    top_actions.addWidget(back_btn)
    top_actions.addWidget(display_btn)
    top_actions.addWidget(next_btn)
    layout.addWidget(top)
    layout.addWidget(answering_bar)

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