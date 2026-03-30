from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor


def make_shadow(w, blur=20, color=QColor(255, 200, 50, 140), y=6):
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
    central.setStyleSheet("""
        QWidget {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #020617,
                stop:0.45 #071a3a,
                stop:1 #031525);
            color: #E2E8F0;
            font-family: Segoe UI, Arial, sans-serif;
        }
    """)

    win.setMinimumSize(1100, 680)
    win.resize(1280, 760)

    layout = QVBoxLayout(central)
    layout.setContentsMargins(18, 16, 18, 14)
    layout.setSpacing(12)

    # -------------------------------------------------
    # TOP SCORE AREA
    # -------------------------------------------------
    top = QWidget()
    top.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    tlay = QHBoxLayout(top)
    tlay.setContentsMargins(0, 0, 0, 0)
    tlay.setSpacing(20)

    def score_block(team_name="TEAM", val="0"):
        wrap = QWidget()
        wrap.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(10)

        team_lbl = QLabel(team_name)
        team_lbl.setAlignment(Qt.AlignCenter)
        team_lbl.setStyleSheet("""
            color: #93C5FD;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 1px;
        """)

        f = QFrame()
        f.setFixedSize(160, 160)
        f.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #7C3AED, stop:1 #0EA5E9);
                border-radius: 24px;
                border: none;
            }
        """)
        make_shadow(f, blur=26, color=QColor(59, 130, 246, 120), y=7)

        frame_layout = QVBoxLayout(f)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        lbl = QLabel(val)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("""
            color: white;
            font-weight: 900;
            font-size: 42px;
            background: transparent;
        """)

        frame_layout.addStretch()
        frame_layout.addWidget(lbl)
        frame_layout.addStretch()

        strikes_wrap = QWidget()
        strikes_layout = QHBoxLayout(strikes_wrap)
        strikes_layout.setContentsMargins(0, 0, 0, 0)
        strikes_layout.setSpacing(6)

        strike_labels = []
        for _ in range(3):
            sx = QLabel("X")
            sx.setFixedSize(24, 24)
            sx.setAlignment(Qt.AlignCenter)
            sx.setStyleSheet("""
                color: #F87171;
                border: 1px solid #EF4444;
                border-radius: 12px;
                background: rgba(239,68,68,0.08);
                font-weight: 800;
                font-size: 12px;
            """)
            sx.setVisible(False)
            strike_labels.append(sx)
            strikes_layout.addWidget(sx)

        wl.addWidget(team_lbl)
        wl.addWidget(f, alignment=Qt.AlignCenter)
        wl.addWidget(strikes_wrap, alignment=Qt.AlignCenter)

        wrap._team_label = team_lbl
        wrap._score_label = lbl
        wrap._strike_labels = strike_labels
        return wrap

    left_score = score_block("TEAM A", "0")
    right_score = score_block("TEAM B", "0")

    center_small = QFrame()
    center_small.setFixedSize(170, 96)
    center_small.setStyleSheet("""
        QFrame {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #2563EB, stop:1 #7C3AED);
            border: 4px solid #F59E0B;
            border-radius: 22px;
        }
    """)
    make_shadow(center_small, blur=24, color=QColor(245, 158, 11, 110), y=6)

    cs_layout = QVBoxLayout(center_small)
    cs_layout.setContentsMargins(8, 6, 8, 6)
    cs_layout.setSpacing(0)

    cs_title = QLabel("ROUND TOTAL")
    cs_title.setAlignment(Qt.AlignCenter)
    cs_title.setStyleSheet("""
        color: #DBEAFE;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1px;
        background: transparent;
    """)

    cs_lbl = QLabel("0")
    cs_lbl.setAlignment(Qt.AlignCenter)
    cs_lbl.setStyleSheet("""
        color: white;
        font-weight: 900;
        font-size: 32px;
        background: transparent;
    """)

    cs_layout.addWidget(cs_title)
    cs_layout.addWidget(cs_lbl)

    tlay.addWidget(left_score, alignment=Qt.AlignLeft | Qt.AlignTop)
    tlay.addStretch()
    tlay.addWidget(center_small, alignment=Qt.AlignHCenter | Qt.AlignTop)
    tlay.addStretch()
    tlay.addWidget(right_score, alignment=Qt.AlignRight | Qt.AlignTop)

    layout.addWidget(top, 0)

    # -------------------------------------------------
    # MAIN BOARD
    # -------------------------------------------------
    board_container = QFrame()
    board_container.setStyleSheet("""
        QFrame {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #071B3A, stop:1 #0B2A5A);
            border-radius: 30px;
            border: 5px solid #F59E0B;
        }
    """)
    board_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    make_shadow(board_container, blur=34, color=QColor(245, 158, 11, 105), y=7)

    b_layout = QVBoxLayout(board_container)
    b_layout.setContentsMargins(16, 16, 16, 16)
    b_layout.setSpacing(14)

    header = QFrame()
    header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    header.setStyleSheet("""
        QFrame {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #0F2A57, stop:1 #162E63);
            border-radius: 16px;
            border: none;
        }
    """)
    make_shadow(header, blur=16, color=QColor(0, 0, 0, 70), y=4)

    header_layout = QVBoxLayout(header)
    header_layout.setContentsMargins(16, 10, 16, 10)

    header_label = QLabel("")
    header_label.setStyleSheet("""
        color: white;
        font-weight: 900;
        font-size: 22px;
        background: transparent;
    """)
    header_label.setAlignment(Qt.AlignCenter)
    header_label.setWordWrap(True)

    header_layout.addWidget(header_label)
    b_layout.addWidget(header, 0)

    fast_badge = QLabel("FAST MONEY")
    fast_badge.setAlignment(Qt.AlignCenter)
    fast_badge.setFixedHeight(30)
    fast_badge.setStyleSheet("""
        QLabel {
            color: #F8FAFC;
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #F59E0B, stop:1 #FBBF24);
            border-radius: 15px;
            font-weight: 800;
            padding: 0 14px;
        }
    """)
    fast_badge.setVisible(False)
    b_layout.addWidget(fast_badge, 0, Qt.AlignHCenter)

    grid = QWidget()
    grid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    gl = QHBoxLayout(grid)
    gl.setContentsMargins(2, 2, 2, 2)
    gl.setSpacing(14)

    answer_widgets = []

    def grid_column():
        w = QWidget()
        w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        col = QVBoxLayout(w)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(12)

        for _ in range(4):
            item = QFrame()
            item.setMinimumHeight(74)
            item.setMaximumHeight(86)
            item.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            item.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 #0B3B8C, stop:1 #09245A);
                    border-radius: 16px;
                }
            """)
            make_shadow(item, blur=14, color=QColor(245, 158, 11, 80), y=3)

            il = QHBoxLayout(item)
            il.setContentsMargins(14, 8, 14, 8)
            il.setSpacing(10)

            txt = QLabel("")
            txt.setStyleSheet("""
                color: white;
                font-weight: 900;
                font-size: 17px;
                padding-left: 4px;
                background: transparent;
            """)
            txt.setWordWrap(True)
            txt.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            score_badge = QLabel("")
            score_badge.setAlignment(Qt.AlignCenter)
            score_badge.setFixedSize(58, 40)
            score_badge.setStyleSheet("""
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #0EA5E9, stop:1 #2563EB);
                color: white;
                border-radius: 12px;
                font-weight: 900;
                font-size: 16px;
                padding: 2px;
            """)

            il.addWidget(txt)
            il.addStretch()
            il.addWidget(score_badge)

            col.addWidget(item)
            answer_widgets.append((txt, score_badge, item))

        return w

    left = grid_column()
    right = grid_column()

    gl.addWidget(left)
    gl.addWidget(right)

    b_layout.addWidget(grid, 1)
    layout.addWidget(board_container, 1)

    # -------------------------------------------------
    # BOTTOM AREA
    # -------------------------------------------------
    bottom = QWidget()
    bottom.setFixedHeight(54)
    bottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    bl = QHBoxLayout(bottom)
    bl.setContentsMargins(4, 0, 4, 0)
    bl.setSpacing(14)

    add_edit = QLabel("Audience Display")
    add_edit.setStyleSheet("""
        color: #F8FAFC;
        font-size: 14px;
        font-weight: 700;
    """)
    add_edit.setAlignment(Qt.AlignCenter)

    bl.addStretch()
    bl.addWidget(add_edit, alignment=Qt.AlignCenter)
    bl.addStretch()

    layout.addWidget(bottom, 0)

    # -------------------------------------------------
    # REFRESH DATA FROM PLAY SCREEN
    # -------------------------------------------------
    def _refresh_display():
        pw = getattr(app, "play_widget", None)

        # defaults
        team_a_name = "TEAM A"
        team_b_name = "TEAM B"
        team_a_score = "0"
        team_b_score = "0"
        question_text = title or ""

        # reset board first
        for t_lbl, s_lbl, _fr in answer_widgets:
            t_lbl.setText("")
            s_lbl.setText("")

        if not pw:
            header_label.setText(question_text)
            left_score._team_label.setText(team_a_name)
            right_score._team_label.setText(team_b_name)
            left_score._score_label.setText(team_a_score)
            right_score._score_label.setText(team_b_score)
            cs_lbl.setText("0")
            return

        # team names and scores
        try:
            if hasattr(pw, "game_state"):
                teams = pw.game_state.get("teams", [])
                if len(teams) >= 2:
                    team_a_name = str(teams[0].get("name", "TEAM A")).upper()
                    team_b_name = str(teams[1].get("name", "TEAM B")).upper()
                    team_a_score = str(teams[0].get("score", 0))
                    team_b_score = str(teams[1].get("score", 0))
                else:
                    pass
        except Exception:
            pass

        # current question
        try:
            if hasattr(pw, "get_current_round_data"):
                rd = pw.get_current_round_data()
                if rd:
                    question_text = rd.get("question", question_text)
            elif hasattr(pw, "game_state"):
                rd = pw.game_state.get("current_round")
                if rd:
                    question_text = rd.get("question", question_text)
        except Exception:
            pass

        # LIVE revealed answers from admin play board
        try:
            live_cards = []
            if hasattr(pw, "game_state"):
                live_cards = pw.game_state.get("answers_widgets", [])

            for i in range(min(len(answer_widgets), len(live_cards))):
                t_lbl, s_lbl, _fr = answer_widgets[i]
                card = live_cards[i]

                is_revealed = bool(getattr(card, "_revealed", False))
                is_active = bool(getattr(card, "_active", True))
                answer_text = str(getattr(card, "_answer_text", "") or "")
                answer_pts = getattr(card, "_answer_pts", 0)

                if not is_active:
                    t_lbl.setText("")
                    s_lbl.setText("")
                elif is_revealed:
                    t_lbl.setText(answer_text)
                    s_lbl.setText(str(answer_pts or 0))
                else:
                    t_lbl.setText("")
                    s_lbl.setText("")
        except Exception:
            pass

        left_score._team_label.setText(team_a_name)
        right_score._team_label.setText(team_b_name)
        left_score._score_label.setText(team_a_score)
        right_score._score_label.setText(team_b_score)
        header_label.setText(question_text)

        strike_a = 0
        strike_b = 0
        try:
            if hasattr(pw, "game_state"):
                teams = pw.game_state.get("teams", [])
                if len(teams) >= 2:
                    strike_a = int(teams[0].get("strikes", 0))
                    strike_b = int(teams[1].get("strikes", 0))
        except Exception:
            pass

        for i, sx in enumerate(getattr(left_score, "_strike_labels", [])):
            sx.setVisible(i < strike_a)
        for i, sx in enumerate(getattr(right_score, "_strike_labels", [])):
            sx.setVisible(i < strike_b)

        fast_mode = False
        try:
            if hasattr(pw, "get_current_round_data"):
                rd = pw.get_current_round_data()
            elif hasattr(pw, "game_state"):
                rd = pw.game_state.get("current_round")
            else:
                rd = None
            if rd:
                fast_mode = bool(rd.get("fast_money", False))
        except Exception:
            fast_mode = False
        fast_badge.setVisible(fast_mode)

        try:
            cs_lbl.setText(str(int(team_a_score) + int(team_b_score)))
        except Exception:
            cs_lbl.setText("0")

    win._refresh_display = _refresh_display

    # auto-refresh so the display updates when admin reveals answers
    refresh_timer = QTimer(win)
    refresh_timer.timeout.connect(_refresh_display)
    refresh_timer.start(150)
    win._refresh_timer = refresh_timer

    app.display_window = win
    _refresh_display()
    win.show()
    return win