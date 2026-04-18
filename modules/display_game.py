from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
    QStackedLayout,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
from PySide6.QtGui import QColor, QPixmap
from pathlib import Path


USE_DISPLAY_SHADOW_EFFECTS = False


def make_shadow(w, blur=20, color=QColor(255, 200, 50, 140), y=6):
    if not USE_DISPLAY_SHADOW_EFFECTS:
        return None
    sh = QGraphicsDropShadowEffect(w)
    sh.setBlurRadius(blur)
    sh.setOffset(0, y)
    sh.setColor(color)
    w.setGraphicsEffect(sh)
    return sh


def open_display_game(app, title: str = "", description: str = ""):
    """Create a top-level QMainWindow for the audience display.
    The display mirrors only the answers that the admin has revealed
    on the play/admin screen.
    """

    try:
        if hasattr(app, "display_window") and app.display_window is not None:
            try:
                if hasattr(app.display_window, "_refresh_display"):
                    app.display_window._refresh_display()
            except Exception:
                pass
            app.display_window.show()
            app.display_window.raise_()
            app.display_window.activateWindow()
            return
    except Exception:
        pass

    win = QMainWindow()
    win.setWindowTitle("Display Game")
    win.setWindowFlag(Qt.Window, True)
    win.setWindowModality(Qt.NonModal)

    central = QWidget()
    win.setCentralWidget(central)
    central.setStyleSheet(
        """
        QWidget {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #020617,
                stop:0.45 #072653,
                stop:1 #031525);
            color: #E2E8F0;
            font-family: Bahnschrift, Segoe UI, Arial, sans-serif;
        }
    """
    )

    win.setMinimumSize(1120, 700)
    win.resize(1366, 820)

    layout = QVBoxLayout(central)
    layout.setContentsMargins(18, 16, 18, 14)
    layout.setSpacing(12)

    # -------------------------------------------------
    # TOP HEADER + SCORE AREA
    # -------------------------------------------------
    round_badge = QLabel("")
    status_badge = QLabel("")
    round_badge.setVisible(False)
    status_badge.setVisible(False)

    top = QWidget()
    top.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    tlay = QHBoxLayout(top)
    tlay.setContentsMargins(0, 0, 0, 0)
    tlay.setSpacing(20)

    def score_block(team_name="TEAM", val="0", accent="#38BDF8"):
        wrap = QWidget()
        wrap.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(8)

        card = QFrame()
        card.setMinimumHeight(210)
        card.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #071832, stop:1 #0B274D);
                border-radius: 24px;
                border: 2px solid rgba(245, 158, 11, 0.70);
            }}
        """
        )
        make_shadow(card, blur=20, color=QColor(245, 158, 11, 100), y=6)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(8)

        team_lbl = QLabel(team_name)
        team_lbl.setAlignment(Qt.AlignCenter)
        team_lbl.setStyleSheet(
            """
            color: #F8FAFC;
            font-size: 16px;
            font-weight: 900;
            letter-spacing: 1px;
            background: transparent;
        """
        )

        control_badge = QLabel("PLAYING")
        control_badge.setAlignment(Qt.AlignCenter)
        control_badge.setFixedHeight(26)
        control_badge.setStyleSheet(
            """
            QLabel {
                color: #111827;
                background: #FACC15;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 900;
                padding: 0 10px;
            }
        """
        )
        control_badge.setVisible(False)

        lead_badge = QLabel("LEADING")
        lead_badge.setAlignment(Qt.AlignCenter)
        lead_badge.setFixedHeight(22)
        lead_badge.setStyleSheet(
            """
            QLabel {
                color: #0F172A;
                background: #7CFC8A;
                border-radius: 9px;
                font-size: 10px;
                font-weight: 900;
                padding: 0 10px;
            }
        """
        )
        lead_badge.setVisible(False)

        score_card = QFrame()
        score_card.setMinimumHeight(120)
        score_card.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {accent}, stop:1 #2563EB);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.18);
            }}
        """
        )
        make_shadow(score_card, blur=18, color=QColor(255, 255, 255, 100), y=4)

        score_layout = QVBoxLayout(score_card)
        score_layout.setContentsMargins(0, 0, 0, 0)

        score_lbl = QLabel(val)
        score_lbl.setAlignment(Qt.AlignCenter)
        score_lbl.setStyleSheet(
            """
            color: white;
            font-weight: 900;
            font-size: 62px;
            background: transparent;
        """
        )
        score_layout.addWidget(score_lbl)

        strikes_wrap = QWidget()
        strikes_layout = QHBoxLayout(strikes_wrap)
        strikes_layout.setContentsMargins(0, 0, 0, 0)
        strikes_layout.setSpacing(8)

        strike_labels = []
        for _ in range(3):
            sx = QLabel("X")
            sx.setFixedSize(28, 28)
            sx.setAlignment(Qt.AlignCenter)
            sx.setStyleSheet(
                """
                color: #FCA5A5;
                border: 2px solid #EF4444;
                border-radius: 12px;
                background: rgba(239,68,68,0.10);
                font-weight: 900;
                font-size: 13px;
            """
            )
            sx.setVisible(False)
            strike_labels.append(sx)
            strikes_layout.addWidget(sx)

        card_layout.addWidget(team_lbl)
        card_layout.addWidget(control_badge, alignment=Qt.AlignHCenter)
        card_layout.addWidget(lead_badge, alignment=Qt.AlignHCenter)
        card_layout.addWidget(score_card)
        card_layout.addWidget(strikes_wrap, alignment=Qt.AlignHCenter)

        wl.addWidget(card)

        member_labels = []

        wrap._accent = accent
        wrap._card = card
        wrap._team_label = team_lbl
        wrap._member_labels = member_labels
        wrap._score_label = score_lbl
        wrap._strike_labels = strike_labels
        wrap._control_badge = control_badge
        wrap._lead_badge = lead_badge
        return wrap

    left_score = score_block("TEAM A", "0", accent="#06B6D4")
    right_score = score_block("TEAM B", "0", accent="#F97316")

    center_small = QFrame()
    center_small.setMinimumWidth(240)
    center_small.setMaximumWidth(280)
    center_small.setMinimumHeight(180)
    center_small.setStyleSheet(
        """
        QFrame {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #1D3B92, stop:1 #3B1A8F);
            border: 4px solid #FBBF24;
            border-radius: 28px;
        }
    """
    )
    make_shadow(center_small, blur=26, color=QColor(245, 158, 11, 120), y=6)

    cs_layout = QVBoxLayout(center_small)
    cs_layout.setContentsMargins(10, 8, 10, 8)
    cs_layout.setSpacing(4)

    cs_title = QLabel("TOTAL")
    cs_title.setAlignment(Qt.AlignCenter)
    cs_title.setStyleSheet(
        """
        color: #DBEAFE;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 1px;
        background: transparent;
    """
    )

    cs_lbl = QLabel("0")
    cs_lbl.setAlignment(Qt.AlignCenter)
    cs_lbl.setStyleSheet(
        """
        color: white;
        font-weight: 900;
        font-size: 56px;
        background: transparent;
    """
    )

    control_label = QLabel("PLAYING: -")
    control_label.setAlignment(Qt.AlignCenter)
    control_label.setStyleSheet(
        """
        color: #E2E8F0;
        font-size: 12px;
        font-weight: 900;
        letter-spacing: 1px;
        background: transparent;
    """
    )

    cs_layout.addWidget(cs_title)
    cs_layout.addWidget(cs_lbl)
    cs_layout.addWidget(control_label)

    tlay.addWidget(left_score, 2)
    tlay.addWidget(center_small, 1, Qt.AlignTop)
    tlay.addWidget(right_score, 2)
    layout.addWidget(top, 0)

    # -------------------------------------------------
    # MAIN BOARD
    # -------------------------------------------------
    board_container = QFrame()
    board_container.setStyleSheet(
        """
        QFrame {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #061328, stop:0.45 #091f3c, stop:1 #081a34);
            border-radius: 34px;
            border: 6px solid #FBBF24;
        }
    """
    )
    board_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    b_layout = QVBoxLayout(board_container)
    b_layout.setContentsMargins(16, 16, 16, 16)
    b_layout.setSpacing(14)

    header = QFrame()
    header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    header.setStyleSheet(
        """
        QFrame {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 22px;
            border: 1px solid rgba(255, 255, 255, 0.12);
        }
    """
    )
    make_shadow(header, blur=16, color=QColor(0, 0, 0, 70), y=4)

    header_layout = QVBoxLayout(header)
    header_layout.setContentsMargins(16, 10, 16, 10)

    header_label = QLabel("")
    header_label.setStyleSheet(
        """
        color: #F8FAFC;
        font-weight: 900;
        font-size: 34px;
        letter-spacing: 0.8px;
        background: transparent;
    """
    )
    header_label.setAlignment(Qt.AlignCenter)
    header_label.setWordWrap(True)

    header_layout.addWidget(header_label)
    b_layout.addWidget(header, 0)

    fast_badge = QLabel("FAST MONEY")
    fast_badge.setAlignment(Qt.AlignCenter)
    fast_badge.setFixedHeight(32)
    fast_badge.setStyleSheet(
        """
        QLabel {
            color: #111827;
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #FCD34D, stop:1 #F59E0B);
            border-radius: 16px;
            font-size: 12px;
            font-weight: 900;
            letter-spacing: 1px;
            padding: 0 14px;
        }
    """
    )
    fast_badge.setVisible(False)
    b_layout.addWidget(fast_badge, 0, Qt.AlignHCenter)

    grid = QWidget()
    grid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    gl = QHBoxLayout(grid)
    gl.setContentsMargins(2, 2, 2, 2)
    gl.setSpacing(14)

    answer_widgets = []

    class AudienceAnswerCard(QFrame):
        def __init__(self, rank: int):
            super().__init__()
            self._rank = rank
            self._active = True
            self._revealed = False
            self._reveal_anim = None
            self._state_key = None

            self.setMinimumHeight(78)
            self.setMaximumHeight(108)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            self._set_active_style(True)

            il = QHBoxLayout(self)
            il.setContentsMargins(14, 8, 14, 8)
            il.setSpacing(10)

            self._rank_lbl = QLabel(str(rank))
            self._rank_lbl.setAlignment(Qt.AlignCenter)
            self._rank_lbl.setFixedSize(30, 30)
            self._rank_lbl.setStyleSheet(
                """
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(251, 191, 36, 0.45);
                border-radius: 10px;
                color: #F8FAFC;
                font-size: 13px;
                font-weight: 900;
            """
            )

            self._content = QWidget()
            self._content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self._stack = QStackedLayout(self._content)
            self._stack.setContentsMargins(0, 0, 0, 0)

            self._front = QLabel("CLICK TO REVEAL")
            self._front.setAlignment(Qt.AlignCenter)
            self._front.setStyleSheet(
                """
                background: transparent;
                border: none;
                color: #BAE6FD;
                font-weight: 900;
                font-size: 14px;
                letter-spacing: 1px;
            """
            )

            self._back = QLabel("")
            self._back.setAlignment(Qt.AlignCenter)
            self._back.setWordWrap(True)
            self._back.setStyleSheet(
                """
                background: transparent;
                border: none;
                color: white;
                font-weight: 900;
                font-size: 17px;
            """
            )

            self._stack.addWidget(self._front)
            self._stack.addWidget(self._back)
            self._stack.setCurrentWidget(self._front)

            self._pts_lbl = QLabel("")
            self._pts_lbl.setAlignment(Qt.AlignCenter)
            self._pts_lbl.setFixedSize(66, 42)
            self._pts_lbl.setStyleSheet(
                """
                background: qradialgradient(cx:0.3, cy:0.3, radius:1,
                    fx:0.3, fy:0.3, stop:0 #FDE68A, stop:1 #F97316);
                border-radius: 16px;
                color: #111827;
                font-size: 18px;
                font-weight: 900;
            """
            )
            self._pts_lbl.setVisible(False)

            il.addWidget(self._rank_lbl)
            il.addWidget(self._content, stretch=1)
            il.addWidget(self._pts_lbl)

        def _set_active_style(self, active: bool):
            if active:
                self.setStyleSheet(
                    """
                    QFrame {
                        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                            stop:0 #071B3D, stop:1 #091A42);
                        border-radius: 18px;
                        border: 2px solid rgba(251, 191, 36, 0.90);
                    }
                """
                )
            else:
                self.setStyleSheet(
                    """
                    QFrame {
                        background: #112744;
                        border: 2px dashed #3B5A7D;
                        border-radius: 16px;
                    }
                """
                )

        def _animate_reveal(self):
            try:
                if self._reveal_anim is not None:
                    self._reveal_anim.stop()
            except Exception:
                pass

            full_w = max(self._content.width(), self._content.sizeHint().width(), 1)
            self._content.setMaximumWidth(full_w)

            shrink = QPropertyAnimation(self._content, b"maximumWidth", self)
            shrink.setDuration(130)
            shrink.setStartValue(full_w)
            shrink.setEndValue(0)
            shrink.setEasingCurve(QEasingCurve.InOutCubic)

            expand = QPropertyAnimation(self._content, b"maximumWidth", self)
            expand.setDuration(160)
            expand.setStartValue(0)
            expand.setEndValue(full_w)
            expand.setEasingCurve(QEasingCurve.InOutCubic)

            group = QSequentialAnimationGroup(self)
            group.addAnimation(shrink)

            def _swap():
                self._stack.setCurrentWidget(self._back)
                self._pts_lbl.setVisible(True)

            shrink.finished.connect(_swap)
            group.addAnimation(expand)

            def _finish():
                self._content.setMaximumWidth(16777215)
                self._reveal_anim = None

            group.finished.connect(_finish)
            self._reveal_anim = group
            group.start()

        def apply_state(self, is_active: bool, is_revealed: bool, answer_text: str, answer_pts: int):
            key = (bool(is_active), bool(is_revealed), str(answer_text), int(answer_pts or 0))
            if self._state_key == key:
                return
            self._state_key = key

            self._set_active_style(bool(is_active))
            self._active = bool(is_active)
            self._back.setText(str(answer_text or ""))
            self._pts_lbl.setText(str(int(answer_pts or 0)))

            if not self._active:
                self._front.setText("—")
                self._front.setStyleSheet(
                    """
                    background: transparent;
                    border: none;
                    color: #8BA4BF;
                    font-weight: 800;
                    font-size: 22px;
                    letter-spacing: 0px;
                """
                )
                self._stack.setCurrentWidget(self._front)
                self._pts_lbl.setVisible(False)
                self._revealed = False
                return

            self._front.setText("CLICK TO REVEAL")
            self._front.setStyleSheet(
                """
                background: transparent;
                border: none;
                color: #BAE6FD;
                font-weight: 900;
                font-size: 14px;
                letter-spacing: 1px;
            """
            )

            should_animate = bool(is_revealed and (not self._revealed))
            if is_revealed:
                if should_animate:
                    self._animate_reveal()
                else:
                    self._stack.setCurrentWidget(self._back)
                    self._pts_lbl.setVisible(True)
                    self._content.setMaximumWidth(16777215)
                self._revealed = True
            else:
                self._stack.setCurrentWidget(self._front)
                self._pts_lbl.setVisible(False)
                self._revealed = False

    def grid_column():
        w = QWidget()
        w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        col = QVBoxLayout(w)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(12)

        for idx in range(4):
            card = AudienceAnswerCard(rank=idx + 1)
            col.addWidget(card)
            answer_widgets.append(card)

        return w

    left = grid_column()
    right = grid_column()

    gl.addWidget(left)
    gl.addWidget(right)

    b_layout.addWidget(grid, 1)

    # Winner overlay card shown after final round.
    winner_panel = QFrame()
    winner_panel.setVisible(False)
    winner_panel.setStyleSheet(
        """
        QFrame {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #0C1D39, stop:1 #122E56);
            border: 3px solid #FBBF24;
            border-radius: 24px;
        }
    """
    )

    winner_layout = QVBoxLayout(winner_panel)
    winner_layout.setContentsMargins(18, 18, 18, 18)
    winner_layout.setSpacing(14)

    winner_title = QLabel("WINNER")
    winner_title.setAlignment(Qt.AlignCenter)
    winner_title.setStyleSheet(
        """
        color: #FDE68A;
        font-size: 46px;
        font-weight: 900;
        letter-spacing: 2px;
        background: transparent;
    """
    )

    winner_team = QLabel("TEAM A")
    winner_team.setAlignment(Qt.AlignCenter)
    winner_team.setStyleSheet(
        """
        color: #F8FAFC;
        font-size: 52px;
        font-weight: 900;
        background: transparent;
    """
    )

    final_scores = QLabel("TEAM A: 0  |  TEAM B: 0")
    final_scores.setAlignment(Qt.AlignCenter)
    final_scores.setStyleSheet(
        """
        color: #DBEAFE;
        font-size: 26px;
        font-weight: 800;
        background: transparent;
    """
    )

    winner_layout.addStretch(1)
    winner_layout.addWidget(winner_title)
    winner_layout.addWidget(winner_team)
    winner_layout.addWidget(final_scores)
    winner_layout.addStretch(1)

    layout.addWidget(board_container, 1)
    layout.addWidget(winner_panel, 1)

    # Bottom helper text removed per request.

    # Animation plumbing for round/winner transitions.
    board_opacity_effect = QGraphicsOpacityEffect(board_container)
    board_opacity_effect.setOpacity(1.0)
    board_container.setGraphicsEffect(board_opacity_effect)

    winner_opacity_effect = QGraphicsOpacityEffect(winner_panel)
    winner_opacity_effect.setOpacity(1.0)
    winner_panel.setGraphicsEffect(winner_opacity_effect)

    win._round_anim = None
    win._winner_anim = None
    win._last_round_key = None
    win._winner_visible = False

    def _play_round_transition():
        try:
            if win._round_anim is not None:
                win._round_anim.stop()
        except Exception:
            pass

        anim = QPropertyAnimation(board_opacity_effect, b"opacity", win)
        anim.setDuration(360)
        anim.setStartValue(0.35)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.InOutCubic)
        win._round_anim = anim
        anim.start()

    def _play_winner_transition(show: bool):
        try:
            if win._winner_anim is not None:
                win._winner_anim.stop()
        except Exception:
            pass

        if show:
            winner_panel.setVisible(True)
            winner_opacity_effect.setOpacity(0.0)
            anim = QPropertyAnimation(winner_opacity_effect, b"opacity", win)
            anim.setDuration(420)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.InOutCubic)
            win._winner_anim = anim
            anim.start()
        else:
            winner_panel.setVisible(False)

    def _apply_team_accent(team_block, is_control=False, is_leading=False):
        state_key = (bool(is_control), bool(is_leading))
        if getattr(team_block, "_last_accent_state", None) == state_key:
            return
        team_block._last_accent_state = state_key

        border = "rgba(125, 211, 252, 0.26)"
        glow = QColor(0, 0, 0, 90)
        if is_control:
            border = "#FACC15"
            glow = QColor(250, 204, 21, 130)
        elif is_leading:
            border = "#4ADE80"
            glow = QColor(74, 222, 128, 120)

        team_block._card.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #0B1F3E, stop:1 #0C2D58);
                border-radius: 20px;
                border: 3px solid {border};
            }}
        """
        )

        shadow = team_block._card.graphicsEffect()
        if isinstance(shadow, QGraphicsDropShadowEffect):
            shadow.setColor(glow)

        team_block._control_badge.setVisible(bool(is_control))
        team_block._lead_badge.setVisible(bool(is_leading and not is_control))

    # -------------------------------------------------
    # REFRESH DATA FROM PLAY SCREEN
    # -------------------------------------------------
    def _refresh_display():
        pw = getattr(app, "play_widget", None)

        # defaults
        team_a_name = "TEAM A"
        team_b_name = "TEAM B"
        team_a_members = ["", "", "", ""]
        team_b_members = ["", "", "", ""]
        team_a_score = 0
        team_b_score = 0
        strike_a = 0
        strike_b = 0
        question_text = title or ""
        round_number = 1
        total_rounds = None
        fast_mode = False
        control_idx = None
        game_finished = False

        rd = None

        if pw and hasattr(pw, "game_state"):
            try:
                teams = pw.game_state.get("teams", [])
                if len(teams) >= 2:
                    team_a_name = str(teams[0].get("name", "TEAM A")).upper()
                    team_b_name = str(teams[1].get("name", "TEAM B")).upper()

                    a_members = teams[0].get("members", [])
                    b_members = teams[1].get("members", [])
                    if isinstance(a_members, list):
                        team_a_members = [
                            (str(a_members[i]) if i < len(a_members) else "") for i in range(4)
                        ]
                    if isinstance(b_members, list):
                        team_b_members = [
                            (str(b_members[i]) if i < len(b_members) else "") for i in range(4)
                        ]

                    try:
                        team_a_score = int(teams[0].get("score", 0) or 0)
                    except Exception:
                        team_a_score = 0
                    try:
                        team_b_score = int(teams[1].get("score", 0) or 0)
                    except Exception:
                        team_b_score = 0

                    try:
                        strike_a = int(teams[0].get("strikes", 0) or 0)
                    except Exception:
                        strike_a = 0
                    try:
                        strike_b = int(teams[1].get("strikes", 0) or 0)
                    except Exception:
                        strike_b = 0

                rd = pw.game_state.get("current_round")
                if rd and isinstance(rd, dict):
                    question_text = str(rd.get("question", question_text) or question_text)
                    fast_mode = bool(rd.get("fast_money", False))

                control_idx_raw = pw.game_state.get("current_control_team")
                if control_idx_raw in (0, 1):
                    control_idx = int(control_idx_raw)

                revealed_answer_indices = pw.game_state.get("revealed_answer_indices", [])
                if not isinstance(revealed_answer_indices, list):
                    revealed_answer_indices = []
                revealed_set = set()
                for idx in revealed_answer_indices:
                    try:
                        revealed_set.add(int(idx))
                    except Exception:
                        pass

                rn = pw.game_state.get("current_round_number")
                tr = pw.game_state.get("total_rounds")
                if rn is None:
                    rn = pw.game_state.get("question_idx", 0) + 1
                try:
                    round_number = max(1, int(rn or 1))
                except Exception:
                    round_number = 1

                if tr is not None:
                    try:
                        total_rounds = max(1, int(tr))
                    except Exception:
                        total_rounds = None

                game_finished = bool(pw.game_state.get("game_finished", False))

                # LIVE revealed answers from admin play board
                if rd and isinstance(rd, dict):
                    # Primary rendering path from stable game_state data.
                    answers_data = rd.get("answers", [])
                    for i in range(len(answer_widgets)):
                        card = answer_widgets[i]
                        if i < len(answers_data):
                            raw_text, raw_pts = answers_data[i]
                            text_clean = str(raw_text or "")
                            try:
                                pts_clean = int(raw_pts or 0)
                            except Exception:
                                pts_clean = 0
                            is_active = bool(text_clean.strip()) or bool(pts_clean)
                            card.apply_state(is_active, (i in revealed_set), text_clean, pts_clean)
                        else:
                            card.apply_state(False, False, "", 0)
                else:
                    # Fallback rendering from live card widgets.
                    live_cards = pw.game_state.get("answers_widgets", [])
                    for i in range(min(len(answer_widgets), len(live_cards))):
                        card = answer_widgets[i]
                        card = live_cards[i]
                        is_revealed = bool(getattr(card, "_revealed", False))
                        is_active = bool(getattr(card, "_active", True))
                        answer_text = str(getattr(card, "_answer_text", "") or "")
                        answer_pts = getattr(card, "_answer_pts", 0)
                        answer_widgets[i].apply_state(is_active, is_revealed, answer_text, answer_pts)
            except Exception:
                pass

        left_score._team_label.setText(team_a_name)
        right_score._team_label.setText(team_b_name)
        for i, ml in enumerate(getattr(left_score, "_member_labels", [])):
            value = team_a_members[i] if i < len(team_a_members) else ""
            ml.setText(value if value.strip() else "-")
        for i, ml in enumerate(getattr(right_score, "_member_labels", [])):
            value = team_b_members[i] if i < len(team_b_members) else ""
            ml.setText(value if value.strip() else "-")

        left_score._score_label.setText(str(team_a_score))
        right_score._score_label.setText(str(team_b_score))
        header_label.setText(question_text)

        for i, sx in enumerate(getattr(left_score, "_strike_labels", [])):
            sx.setVisible(i < strike_a)
        for i, sx in enumerate(getattr(right_score, "_strike_labels", [])):
            sx.setVisible(i < strike_b)

        fast_badge.setVisible(fast_mode)
        cs_lbl.setText(str(max(0, team_a_score + team_b_score)))

        if total_rounds:
            round_badge.setText(f"ROUND {round_number} / {total_rounds}")
        else:
            round_badge.setText(f"ROUND {round_number}")

        if fast_mode:
            status_badge.setText("FAST MONEY")
            status_badge.setStyleSheet(
                """
                QLabel {
                    color: #111827;
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 #FDE047, stop:1 #F59E0B);
                    border-radius: 14px;
                    font-size: 12px;
                    font-weight: 900;
                    letter-spacing: 1px;
                    padding: 0 14px;
                }
            """
            )
        else:
            status_badge.setText("LIVE")
            status_badge.setStyleSheet(
                """
                QLabel {
                    color: #111827;
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 #86EFAC, stop:1 #22C55E);
                    border-radius: 14px;
                    font-size: 12px;
                    font-weight: 900;
                    letter-spacing: 1px;
                    padding: 0 14px;
                }
            """
            )

        if control_idx == 0:
            control_label.setText(f"PLAYING: {team_a_name}")
        elif control_idx == 1:
            control_label.setText(f"PLAYING: {team_b_name}")
        else:
            control_label.setText("PLAYING: -")

        lead_a = team_a_score > team_b_score
        lead_b = team_b_score > team_a_score

        _apply_team_accent(left_score, is_control=(control_idx == 0), is_leading=lead_a)
        _apply_team_accent(right_score, is_control=(control_idx == 1), is_leading=lead_b)

        round_key = f"{round_number}|{question_text}"
        if win._last_round_key != round_key:
            win._last_round_key = round_key
            _play_round_transition()

        should_show_winner = bool(game_finished)
        if should_show_winner:
            if team_a_score > team_b_score:
                winner_name = team_a_name
            elif team_b_score > team_a_score:
                winner_name = team_b_name
            else:
                winner_name = "TIE"

            winner_team.setText(winner_name)
            final_scores.setText(
                f"{team_a_name}: {team_a_score}    |    {team_b_name}: {team_b_score}"
            )

        if win._winner_visible != should_show_winner:
            win._winner_visible = should_show_winner
            board_container.setVisible(not should_show_winner)
            _play_winner_transition(should_show_winner)

    win._refresh_display = _refresh_display

    # auto-refresh so the display updates when admin reveals answers
    refresh_timer = QTimer(win)
    refresh_timer.timeout.connect(_refresh_display)
    refresh_timer.start(250)
    win._refresh_timer = refresh_timer

    app.display_window = win
    _refresh_display()
    win.show()
    return win