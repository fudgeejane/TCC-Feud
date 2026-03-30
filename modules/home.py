from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QMenu,
    QScrollArea,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPixmap, QColor
from pathlib import Path
import importlib

# optional DB persistence
try:
    import database.db as db
except Exception:
    db = None


def build_home(parent: QWidget, app):
    """Construct the home UI inside `parent` for a PySide6-based UI."""

    # Clear old layout/widgets
    try:
        old_layout = parent.layout()
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                w = item.widget()
                if w:
                    w.setParent(None)
    except Exception:
        pass

    parent.setStyleSheet("""
        QWidget {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #020617,
                stop:0.35 #07172F,
                stop:1 #040D1F);
            color: #E5E7EB;
            font-family: Segoe UI, Arial, sans-serif;
        }
    """)

    layout = QVBoxLayout(parent)
    layout.setContentsMargins(60, 30, 60, 30)
    layout.setSpacing(22)
    layout.setAlignment(Qt.AlignTop)

    # -----------------------------
    # Header
    # -----------------------------
    header = QWidget()
    header.setStyleSheet("""
        QWidget {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(96,165,250,0.18);
            border-radius: 24px;
        }
    """)
    header_layout = QHBoxLayout(header)
    header_layout.setContentsMargins(24, 18, 24, 18)
    header_layout.setSpacing(18)

    assets_logo = Path(__file__).resolve().parent.parent / "assets" / "logo.png"

    if assets_logo.exists():
        logo_lbl = QLabel()
        pix = QPixmap(str(assets_logo))
        if not pix.isNull():
            pix = pix.scaledToWidth(280, Qt.SmoothTransformation)
            logo_lbl.setPixmap(pix)
        else:
            logo_lbl.setText("TCC Feud")
            logo_lbl.setStyleSheet("""
                font-size: 34px;
                font-weight: 800;
                color: #F8FAFC;
            """)
        header_layout.addWidget(logo_lbl, alignment=Qt.AlignLeft | Qt.AlignVCenter)
    else:
        title = QLabel("TCC Feud")
        title.setStyleSheet("""
            font-size: 34px;
            font-weight: 800;
            color: #F8FAFC;
            letter-spacing: 1px;
        """)
        header_layout.addWidget(title, alignment=Qt.AlignLeft | Qt.AlignVCenter)

    header_layout.addStretch()

    subtitle = QLabel("Create, manage, and launch your Family Feud games")
    subtitle.setStyleSheet("""
        color: #CBD5E1;
        font-size: 14px;
        font-weight: 500;
    """)
    header_layout.addWidget(subtitle, alignment=Qt.AlignVCenter)

    # Try import game modal for edit/delete/create functionality
    try:
        qm = importlib.import_module("utils.game_modal")
    except Exception:
        qm = None

    def on_game_created(payload):
        try:
            if not hasattr(app, "games"):
                app.games = []

            app.games.append({
                "title": payload.get("title", "(no title)"),
                "description": payload.get("description", "")
            })

            try:
                if db:
                    db.save_games(app.games)
            except Exception:
                pass

            if hasattr(app, "render_home_cards"):
                app.render_home_cards()
            elif hasattr(app, "render_cards"):
                app.render_cards()
        except Exception:
            try:
                app.show_static_modal("Game Created", payload.get("title", "(no title)"))
            except Exception:
                pass

    create_btn = QPushButton("＋ Create Game")
    create_btn.setCursor(Qt.PointingHandCursor)
    create_btn.setFixedHeight(48)
    create_btn.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #2563EB, stop:1 #60A5FA);
            color: #F8FAFC;
            border: none;
            border-radius: 14px;
            font-size: 14px;
            font-weight: 800;
            padding: 0 22px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #3B82F6, stop:1 #93C5FD);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #1D4ED8, stop:1 #2563EB);
        }
    """)
    try:
        if qm:
            create_btn.clicked.connect(lambda: qm.open_game_modal(app, on_create=on_game_created))
    except Exception:
        pass

    header_layout.addWidget(create_btn, alignment=Qt.AlignRight | Qt.AlignVCenter)
    layout.addWidget(header)

    # -----------------------------
    # Section heading
    # -----------------------------
    section_wrap = QWidget()
    section_wrap.setStyleSheet("""
        QWidget {
            background: transparent;
        }
    """)
    section_layout = QVBoxLayout(section_wrap)
    section_layout.setContentsMargins(22, 20, 22, 20)
    section_layout.setSpacing(6)

    section_title = QLabel("Your Games")
    section_title.setStyleSheet("""
        font-size: 22px;
        font-weight: 800;
        color: #F8FAFC;
    """)

    section_desc = QLabel("Select a game card to view, modify, or play.")
    section_desc.setStyleSheet("""
        font-size: 13px;
        color: #94A3B8;
    """)

    section_layout.addWidget(section_title)
    section_layout.addWidget(section_desc)
    layout.addWidget(section_wrap)

    # -----------------------------
    # Scrollable cards area
    # -----------------------------
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setStyleSheet("""
        QScrollArea {
            border: none;
            background: transparent;
        }
        QScrollBar:horizontal {
            background: transparent;
            height: 10px;
            margin: 0px 24px 0px 24px;
        }
        QScrollBar::handle:horizontal {
            background: #334155;
            border-radius: 5px;
            min-width: 30px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #475569;
        }
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            width: 0px;
            background: none;
        }
    """)

    cards_container = QWidget()
    cards_layout = QHBoxLayout(cards_container)
    cards_layout.setSpacing(24)
    cards_layout.setContentsMargins(6, 8, 6, 18)
    cards_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

    scroll.setWidget(cards_container)
    layout.addWidget(scroll)

    # Ensure app.games exists
    if not hasattr(app, "games"):
        if db:
            try:
                loaded = db.load_games()
                app.games = loaded if isinstance(loaded, list) else []
            except Exception:
                app.games = []
        else:
            app.games = []

    def create_shadow(widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(28)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 140))
        widget.setGraphicsEffect(shadow)

    def render_cards():
        while cards_layout.count():
            item = cards_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        if not app.games:
            empty_card = QWidget()
            empty_card.setFixedSize(380, 200)
            empty_card.setStyleSheet("""
                QWidget {
                    background-color: #0F172A;
                    border: none;
                    border-radius: 18px;
                }
            """)
            create_shadow(empty_card)

            ec_layout = QVBoxLayout(empty_card)
            ec_layout.setContentsMargins(24, 24, 24, 24)
            ec_layout.setSpacing(10)

            empty_title = QLabel("🎮 No games yet")
            empty_title.setAlignment(Qt.AlignCenter)
            empty_title.setStyleSheet("""
                font-size: 22px;
                font-weight: 800;
                color: #F8FAFC;
            """)

            empty_desc = QLabel("Create your first game to start building your Family Feud experience.")
            empty_desc.setWordWrap(True)
            empty_desc.setAlignment(Qt.AlignCenter)
            empty_desc.setStyleSheet("""
                font-size: 14px;
                color: #94A3B8;
            """)

            ec_layout.addStretch()
            ec_layout.addWidget(empty_title)
            ec_layout.addWidget(empty_desc)
            ec_layout.addStretch()

            cards_layout.addWidget(empty_card)
            cards_layout.addStretch()
            return

        for idx, game in enumerate(app.games):
            title_text = game.get("title", "(no title)")
            desc_text = game.get("description", "")

            card = QWidget()
            card.setFixedSize(320, 228)
            card.setCursor(Qt.PointingHandCursor)
            card.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 rgba(15,23,42,0.95), stop:1 rgba(13,30,63,0.96));
                    border: none;
                    border-radius: 20px;
                }
                QWidget:hover {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 rgba(37,99,235,0.15), stop:1 rgba(15,23,42,0.95));
                }
            """)
            create_shadow(card)

            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(18, 18, 18, 16)
            c_layout.setSpacing(12)

            # Top row
            top = QWidget()
            top.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            top_l = QHBoxLayout(top)
            top_l.setContentsMargins(0, 0, 0, 0)
            top_l.setSpacing(10)

            badge = QLabel("GAME")
            badge.setFixedHeight(24)
            badge.setAlignment(Qt.AlignCenter)
            badge.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            badge.setStyleSheet("""
                background-color: rgba(37,99,235,0.18);
                color: #93C5FD;
                border-radius: 10px;
                padding: 0 10px;
                font-size: 11px;
                font-weight: 700;
            """)

            top_l.addWidget(badge, alignment=Qt.AlignLeft)

            top_l.addStretch()

            menu_btn = QPushButton("⋮")
            menu_btn.setFixedSize(34, 34)
            menu_btn.setCursor(Qt.PointingHandCursor)
            menu_btn.setFocusPolicy(Qt.NoFocus)
            menu_btn.setToolTip("More actions")
            menu_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #E2E8F0;
                    border: none;
                    border-radius: 10px;
                    font-size: 18px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.06);
                }
                QPushButton:pressed {
                    background: rgba(255,255,255,0.10);
                }
            """)
            top_l.addWidget(menu_btn)

            c_layout.addWidget(top)

            # Title
            title_lbl = QLabel(title_text)
            title_lbl.setWordWrap(True)
            title_lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            title_lbl.setStyleSheet("""
                font-weight: 800;
                font-size: 20px;
                color: #F8FAFC;
            """)
            c_layout.addWidget(title_lbl)

            # Description
            desc = QLabel(desc_text if desc_text.strip() else "No description provided.")
            desc.setWordWrap(True)
            desc.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            desc.setStyleSheet("""
                color: #94A3B8;
                font-size: 13px;
                line-height: 1.4;
            """)
            c_layout.addWidget(desc)

            c_layout.addStretch()

            # Footer
            footer = QLabel("Click card to open, edit, or play")
            footer.setAlignment(Qt.AlignCenter)
            footer.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            footer.setStyleSheet("""
                color: #60A5FA;
                font-size: 12px;
                font-weight: 600;
                padding-top: 6px;
            """)
            c_layout.addWidget(footer)

            # Menu
            menu = QMenu()
            menu.setWindowFlags(menu.windowFlags() | Qt.NoDropShadowWindowHint)
            menu.setStyleSheet("""
                QMenu {
                    background: #0B1220;
                    color: #E2E8F0;
                    border: none;
                    border-radius: 10px;
                    padding: 6px 0px;
                }
                QMenu::item {
                    padding: 9px 20px;
                }
                QMenu::item:selected {
                    background: rgba(59,130,246,0.16);
                }
            """)

            edit_action = menu.addAction("Edit")
            delete_action = menu.addAction("Delete")

            def on_edit_triggered(checked=False, i=idx):
                try:
                    modal_mod = importlib.import_module("utils.game_modal")
                    if hasattr(modal_mod, "open_edit_modal"):
                        def _on_save(payload):
                            app.games[i]["title"] = payload.get("title", app.games[i]["title"])
                            app.games[i]["description"] = payload.get(
                                "description",
                                app.games[i].get("description", "")
                            )
                            try:
                                if db:
                                    db.save_games(app.games)
                            except Exception:
                                pass
                            render_cards()

                        modal_mod.open_edit_modal(
                            app,
                            app.games[i].get("title", ""),
                            app.games[i].get("description", ""),
                            on_save=_on_save
                        )
                        return
                except Exception:
                    pass

                try:
                    app.show_static_modal("Edit", f"Edit {app.games[i].get('title', '')}")
                except Exception:
                    pass

            def on_delete_triggered(checked=False, i=idx):
                try:
                    modal_mod = importlib.import_module("utils.game_modal")
                    if hasattr(modal_mod, "open_delete_confirm"):
                        def _on_confirm():
                            try:
                                del app.games[i]
                            except Exception:
                                pass
                            try:
                                if db:
                                    db.save_games(app.games)
                            except Exception:
                                pass
                            render_cards()

                        modal_mod.open_delete_confirm(app, on_confirm=_on_confirm)
                        return
                except Exception:
                    pass

                try:
                    del app.games[i]
                except Exception:
                    pass
                try:
                    if db:
                        db.save_games(app.games)
                except Exception:
                    pass
                render_cards()

            edit_action.triggered.connect(on_edit_triggered)
            delete_action.triggered.connect(on_delete_triggered)

            def _open_menu(i=idx, btn=menu_btn, m=menu):
                pos = btn.mapToGlobal(QPoint(btn.width() - m.sizeHint().width(), btn.height()))
                m.exec(pos)

            menu_btn.clicked.connect(_open_menu)

            def _on_card_click(event, i=idx):
                try:
                    mg = importlib.import_module("modules.modify_game")
                    if hasattr(mg, "open_modify_game"):
                        mg.open_modify_game(
                            app,
                            app.games[i].get("title", ""),
                            app.games[i].get("description", "")
                        )
                        return
                except Exception:
                    pass

                try:
                    app.show_static_modal(
                        f"Modify {app.games[i].get('title', '')}",
                        "Static modify UI not available."
                    )
                except Exception:
                    pass

            card.mousePressEvent = _on_card_click
            cards_layout.addWidget(card)

        cards_layout.addStretch()

    try:
        app.render_home_cards = render_cards
    except Exception:
        pass

    render_cards()