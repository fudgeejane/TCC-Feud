from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QScrollArea, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from typing import Optional

try:
    import database.db as db
except Exception:
    db = None


def create_leaderboard_section(parent: QWidget, app) -> QWidget:
    """Create and return the leaderboard section widget"""

    # ========== LEADERBOARD SECTION ==========
    leaderboard_widget = QWidget()
    leaderboard_widget.setStyleSheet("background: transparent;")
    leaderboard_layout = QVBoxLayout(leaderboard_widget)
    leaderboard_layout.setContentsMargins(20, 20, 20, 20)
    leaderboard_layout.setSpacing(12)
    leaderboard_layout.setAlignment(Qt.AlignTop)

    leaderboard_title = QLabel("🏆 Leaderboard")
    leaderboard_title.setStyleSheet("""
        font-size: 18px;
        font-weight: 800;
        color: #F8FAFC;
    """)
    leaderboard_layout.addWidget(leaderboard_title)

    # Leaderboard container
    leaderboard_scroll = QScrollArea()
    leaderboard_scroll.setWidgetResizable(True)
    leaderboard_scroll.setStyleSheet("""
        QScrollArea {
            border: 1px solid rgba(125, 211, 252, 0.18);
            background: rgba(6, 17, 40, 0.8);
            border-radius: 12px;
        }
        QScrollBar:vertical {
            background: rgba(15, 23, 42, 0.45);
            width: 8px;
            border-radius: 4px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #0ea5e9;
            border-radius: 4px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background: #38bdf8;
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
            background: none;
        }
    """)

    leaderboard_container = QWidget()
    leaderboard_container.setStyleSheet("background: transparent;")
    leaderboard_items_layout = QVBoxLayout(leaderboard_container)
    leaderboard_items_layout.setSpacing(8)
    leaderboard_items_layout.setContentsMargins(4, 4, 4, 4)
    leaderboard_items_layout.setAlignment(Qt.AlignTop)

    leaderboard_scroll.setWidget(leaderboard_container)
    leaderboard_layout.addWidget(leaderboard_scroll)

    def render_leaderboard():
        """Render the leaderboard with all teams sorted by score"""
        while leaderboard_items_layout.count():
            item = leaderboard_items_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        if not hasattr(app, "teams") or not app.teams:
            empty_lbl = QLabel("No teams yet\nAdd a team to see scores!")
            empty_lbl.setAlignment(Qt.AlignCenter)
            empty_lbl.setWordWrap(True)
            empty_lbl.setStyleSheet("""
                color: #a5b4c7;
                font-size: 11pt;
                padding: 20px 10px;
            """)
            leaderboard_items_layout.addWidget(empty_lbl)
            leaderboard_items_layout.addStretch()
            return

        # Sort teams by score (highest first)
        sorted_teams = sorted(enumerate(app.teams), key=lambda x: x[1].get("score", 0), reverse=True)

        for rank, (idx, team) in enumerate(sorted_teams, 1):
            team_item = QWidget()
            team_item.setFixedHeight(70)
            team_item.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 rgba(15,23,42,0.7), stop:1 rgba(10,24,52,0.7));
                    border: 1px solid rgba(125, 211, 252, 0.16);
                    border-radius: 10px;
                }
                QWidget:hover {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 rgba(14,165,233,0.1), stop:1 rgba(15,23,42,0.8));
                    border: 1px solid rgba(125, 211, 252, 0.28);
                }
            """)

            team_layout = QVBoxLayout(team_item)
            team_layout.setContentsMargins(12, 8, 12, 8)
            team_layout.setSpacing(6)

            # Top: Rank and Team Name
            top_layout = QHBoxLayout()
            rank_lbl = QLabel(f"#{rank}")
            rank_lbl.setFixedWidth(32)
            rank_lbl.setStyleSheet(f"""
                color: {"#FFD700" if rank == 1 else "#C0C0C0" if rank == 2 else "#CD7F32" if rank == 3 else "#7DD3FC"};
                font-weight: 800;
                font-size: 14px;
            """)
            top_layout.addWidget(rank_lbl)

            name_lbl = QLabel(team.get("name", "Unknown"))
            name_lbl.setStyleSheet("color: #f8fafc; font-weight: 600; font-size: 12px;")
            name_lbl.setWordWrap(True)
            top_layout.addWidget(name_lbl)
            top_layout.addStretch()

            team_layout.addLayout(top_layout)

            # Bottom: Score
            score_lbl = QLabel(f"Score: {team.get('score', 0)}")
            score_lbl.setStyleSheet("color: #86efac; font-weight: 700; font-size: 13px;")
            team_layout.addWidget(score_lbl)

            leaderboard_items_layout.addWidget(team_item)

        leaderboard_items_layout.addStretch()

    # Store the render function on the app
    try:
        app.render_leaderboard = render_leaderboard
    except Exception:
        pass

    # Initial render
    render_leaderboard()

    return leaderboard_widget