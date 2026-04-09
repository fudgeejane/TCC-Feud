from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QScrollArea, QGraphicsDropShadowEffect, QDialog, QTextEdit, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor
from pathlib import Path
from typing import Callable, Optional

try:
    import utils.game_modal as game_modal
except Exception:
    game_modal = None

try:
    import modules.modify_game as modify_game
except Exception:
    modify_game = None

try:
    import database.db as db
except Exception:
    db = None

def open_edit_modal(parent, title: str, description: str, on_save: Optional[Callable[[dict], None]] = None):
    dlg = QDialog(parent)
    dlg.setWindowTitle("Edit Game")
    dlg.setModal(True)

    dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
    dlg.setWindowFlag(Qt.FramelessWindowHint, True)

    dlg.setStyleSheet("""
    QDialog {
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 8px;
        background: #071033;
    }
    QLabel {
        color: #e6eef8;
        font-size: 11pt;
    }
    QLabel#headerTitle {
        font-weight: 700;
        font-size: 12pt;
    }
    QLineEdit, QTextEdit {
        padding: 8px;
        border-radius: 8px;
        background: #ffffff;
        color: #071033;
        border: none;
    }
    QLineEdit:focus, QTextEdit:focus {
        border: 2px solid #0a84ff;
    }
    QPushButton {
        border-radius: 6px;
        padding: 6px 12px;
    }
    QPushButton#createBtn {
        background: #0b7d2a;
        color: white;
        font-weight: 600;
    }
    QPushButton#createBtn:hover {
        background: #0a6d24;
    }
    QPushButton#cancelBtn {
        background: #eef2f7;
        color: #0f172a;
    }
    QPushButton#dangerBtn {
        background: #b91c1c;
        color: white;
    }
    """)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(12, 12, 12, 12)

    header = QHBoxLayout()
    title_lbl = QLabel("Edit Game")
    title_lbl.setObjectName("headerTitle")
    header.addWidget(title_lbl)
    header.addStretch()
    layout.addLayout(header)

    layout.addWidget(QLabel("Title"))
    title_entry = QLineEdit()
    title_entry.setText(title)
    layout.addWidget(title_entry)

    layout.addWidget(QLabel("Description (optional)"))
    desc = QTextEdit()
    desc.setPlainText(description or "")
    desc.setFixedHeight(120)
    layout.addWidget(desc)

    btns = QHBoxLayout()
    cancel_btn = QPushButton("Cancel")
    save_btn = QPushButton("Save")
    save_btn.setObjectName("createBtn")
    cancel_btn.setObjectName("cancelBtn")
    cancel_btn.setFixedHeight(30)
    save_btn.setFixedHeight(30)
    btns.addWidget(cancel_btn)
    btns.addWidget(save_btn)
    layout.addLayout(btns)

    def on_save_click():
        t = title_entry.text().strip()
        d = desc.toPlainText().strip()
        if not t:
            err = QDialog(dlg)
            err.setWindowTitle("Validation")
            l = QVBoxLayout(err)
            l.addWidget(QLabel("Please enter a title."))
            okb = QPushButton("OK")
            okb.setObjectName("okBtn")
            okb.clicked.connect(err.accept)
            l.addWidget(okb)
            err.exec()
            return
        payload = {"title": t, "description": d}
        dlg.accept()
        if on_save:
            on_save(payload)

    save_btn.clicked.connect(on_save_click)
    cancel_btn.clicked.connect(dlg.reject)

    dlg.setMinimumWidth(460)
    dlg.adjustSize()
    dlg.exec()

def open_delete_confirm(parent, on_confirm: Optional[Callable[[], None]] = None):
    dlg = QDialog(parent)
    dlg.setWindowTitle("Delete Confirmation")
    dlg.setModal(True)
    dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
    dlg.setWindowFlag(Qt.FramelessWindowHint, True)

    dlg.setStyleSheet("""
    QDialog {
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 8px;
        background: #071033;
    }
    QLabel {
        color: #e6eef8;
        font-size: 11pt;
    }
    QLabel#headerTitle {
        font-weight: 700;
        font-size: 12pt;
    }
    QPushButton {
        border-radius: 6px;
        padding: 6px 12px;
    }
    QPushButton#createBtn {
        background: #0b7d2a;
        color: white;
        font-weight: 600;
    }
    QPushButton#cancelBtn {
        background: #eef2f7;
        color: #0f172a;
    }
    QPushButton#dangerBtn {
        background: #b91c1c;
        color: white;
    }
    """)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(16, 12, 16, 12)
    msg = QLabel("Are you sure you want to delete this game?")
    msg.setAlignment(Qt.AlignCenter)
    msg.setWordWrap(True)
    msg.setStyleSheet("color: #e6eef8; font-weight:600; padding:6px 12px;")
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

def build_home(parent: QWidget, app):
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
                stop:0 #02050E,
                stop:0.45 #08213D,
                stop:1 #0B1220);
            color: #E2E8F0;
            font-family: Segoe UI, Arial, sans-serif;
        }
    """)

    layout = QVBoxLayout(parent)
    layout.setContentsMargins(60, 30, 60, 30)
    layout.setSpacing(22)
    layout.setAlignment(Qt.AlignTop)

    # Header
    header = QWidget()
    header.setStyleSheet("""
        QWidget {
            background: transparent;
            border: none;
        }
    """)
    header_layout = QHBoxLayout(header)
    header_layout.setContentsMargins(0, 0, 0, 0)
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
                background: transparent;
            """)
        header_layout.addWidget(logo_lbl, alignment=Qt.AlignLeft | Qt.AlignVCenter)
    else:
        title = QLabel("TCC Feud")
        title.setStyleSheet("""
            font-size: 34px;
            font-weight: 800;
            color: #F8FAFC;
            background: transparent;
            letter-spacing: 1px;
        """)
        header_layout.addWidget(title, alignment=Qt.AlignLeft | Qt.AlignVCenter)

    header_layout.addStretch()

    



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
        if game_modal:
            create_btn.clicked.connect(lambda: game_modal.open_game_modal(app, on_create=on_game_created))
    except Exception:
        pass

    header_layout.addWidget(create_btn, alignment=Qt.AlignRight | Qt.AlignVCenter)
    layout.addWidget(header)

    # Section heading
    section_wrap = QWidget()
    section_wrap.setStyleSheet("""
        QWidget {
            background: transparent;
        }
    """)
    section_layout = QVBoxLayout(section_wrap)
    section_layout.setContentsMargins(0, 0, 0, 0)
    section_layout.setSpacing(0)

    layout.addWidget(section_wrap)

    # Scrollable cards area
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
            background: rgba(15, 23, 42, 0.45);
            height: 10px;
            margin: 0px 24px 0px 24px;
            border-radius: 5px;
        }
        QScrollBar::handle:horizontal {
            background: #0ea5e9;
            border-radius: 5px;
            min-width: 30px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #38bdf8;
        }
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            width: 0px;
            background: none;
        }
    """)

    cards_container = QWidget()
    cards_container.setStyleSheet("background: transparent;")
    cards_layout = QHBoxLayout(cards_container)
    cards_layout.setSpacing(20)
    cards_layout.setContentsMargins(6, 2, 6, 20)
    cards_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

    scroll.setWidget(cards_container)
    layout.addWidget(scroll)

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
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 rgba(15,23,42,0.96), stop:1 rgba(6,17,40,0.96));
                    border: 1px solid rgba(125, 211, 252, 0.18);
                    border-radius: 18px;
                }
            """)
            create_shadow(empty_card)

            ec_layout = QVBoxLayout(empty_card)
            ec_layout.setContentsMargins(24, 24, 24, 24)
            ec_layout.setSpacing(10)

            empty_title = QLabel("No games yet")
            empty_title.setAlignment(Qt.AlignCenter)
            empty_title.setStyleSheet("""
                font-size: 22px;
                font-weight: 800;
                color: #F0F9FF;
            """)

            empty_desc = QLabel("Create your first game to start building your Family Feud experience.")
            empty_desc.setWordWrap(True)
            empty_desc.setAlignment(Qt.AlignCenter)
            empty_desc.setStyleSheet("""
                font-size: 14px;
                color: #A5B4C7;
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
            tip_desc = desc_text.strip() if isinstance(desc_text, str) else ""
            if not tip_desc:
                tip_desc = "No description provided."
            tooltip_text = f"Game {idx + 1}\nName: {title_text}\nDescription: {tip_desc}"

            card = QWidget()
            card.setObjectName("gameCard")
            card.setFixedSize(336, 236)
            card.setCursor(Qt.PointingHandCursor)
            card.setToolTip(tooltip_text)
            card.setStyleSheet("""
                QWidget#gameCard {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 rgba(15,23,42,0.95), stop:1 rgba(10,24,52,0.96));
                    border: 1px solid rgba(125, 211, 252, 0.16);
                    border-radius: 20px;
                }
                QWidget#gameCard:hover {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 rgba(14,165,233,0.14), stop:1 rgba(15,23,42,0.96));
                    border: 1px solid rgba(125, 211, 252, 0.38);
                }
            """)
            create_shadow(card)

            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(18, 16, 18, 16)
            c_layout.setSpacing(10)

            # Top row
            top = QWidget()
            top.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            top_l = QHBoxLayout(top)
            top_l.setContentsMargins(0, 0, 0, 0)
            top_l.setSpacing(10)

            badge = QLabel("GAME")
            badge.setFixedHeight(24)
            badge.setAlignment(Qt.AlignCenter)
            badge.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            badge.setToolTip(tooltip_text)
            badge.setStyleSheet("""
                background-color: rgba(14,165,233,0.18);
                color: #7DD3FC;
                border-radius: 10px;
                padding: 0 10px;
                font-size: 11px;
                font-weight: 700;
            """)

            top_l.addWidget(badge, alignment=Qt.AlignLeft)

            top_l.addStretch()

            # Edit and Delete buttons
            edit_btn = QPushButton("Edit")
            edit_btn.setFixedSize(60, 28)
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setToolTip(f"Edit {title_text}")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(14,165,233,0.2);
                    color: #BAE6FD;
                    border: none;
                    border-radius: 10px;
                    font-size: 11px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background: rgba(14,165,233,0.34);
                }
                QPushButton:pressed {
                    background: rgba(14,165,233,0.45);
                }
            """)

            delete_btn = QPushButton("Delete")
            delete_btn.setFixedSize(60, 28)
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setToolTip(f"Delete {title_text}")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(244,63,94,0.18);
                    color: #fda4af;
                    border: none;
                    border-radius: 10px;
                    font-size: 11px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background: rgba(244,63,94,0.28);
                }
                QPushButton:pressed {
                    background: rgba(244,63,94,0.38);
                }
            """)

            top_l.addWidget(edit_btn)
            top_l.addWidget(delete_btn)

            c_layout.addWidget(top)

            # Title
            title_lbl = QLabel(title_text)
            title_lbl.setWordWrap(True)
            title_lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            title_lbl.setToolTip(tooltip_text)
            title_lbl.setStyleSheet("""
                font-weight: 800;
                font-size: 19px;
                color: #F8FAFC;
            """)
            c_layout.addWidget(title_lbl)

            # Description
            desc = QLabel(desc_text if desc_text.strip() else "No description provided.")
            desc.setWordWrap(True)
            desc.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            desc.setToolTip(tooltip_text)
            desc.setStyleSheet("""
                color: #B8C4D6;
                font-size: 13px;
                line-height: 1.4;
            """)
            c_layout.addWidget(desc)

            c_layout.addStretch()

            # Footer
            footer = QLabel("Click card to open game details")
            footer.setAlignment(Qt.AlignCenter)
            footer.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            footer.setToolTip(tooltip_text)
            footer.setStyleSheet("""
                color: #7DD3FC;
                font-size: 12px;
                font-weight: 600;
                padding-top: 6px;
            """)
            c_layout.addWidget(footer)

            def on_edit_click(i=idx):
                try:
                    if hasattr(app, "games") and i < len(app.games):
                        def _on_save(payload):
                            app.games[i]["title"] = payload.get("title", app.games[i]["title"])
                            app.games[i]["description"] = payload.get("description", app.games[i].get("description", ""))
                            try:
                                if db:
                                    db.save_games(app.games)
                            except Exception:
                                pass
                            render_cards()

                        if game_modal and hasattr(game_modal, "open_edit_modal"):
                            game_modal.open_edit_modal(
                                parent,
                                app.games[i].get("title", ""),
                                app.games[i].get("description", ""),
                                on_save=_on_save
                            )
                        else:
                            open_edit_modal(
                                parent,
                                app.games[i].get("title", ""),
                                app.games[i].get("description", ""),
                                on_save=_on_save
                            )
                except Exception as e:
                    print(f"Error opening edit modal: {e}")

            def on_delete_click(i=idx):
                try:
                    if hasattr(app, "games") and i < len(app.games):
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

                        if game_modal and hasattr(game_modal, "open_delete_confirm"):
                            game_modal.open_delete_confirm(parent, on_confirm=_on_confirm)
                        else:
                            open_delete_confirm(parent, on_confirm=_on_confirm)
                except Exception as e:
                    print(f"Error opening delete confirm: {e}")

            edit_btn.clicked.connect(on_edit_click)
            delete_btn.clicked.connect(on_delete_click)

            def _on_card_click(event, i=idx):
                try:
                    if modify_game and hasattr(modify_game, "open_modify_game"):
                        modify_game.open_modify_game(
                            app,
                            app.games[i].get("title", ""),
                            app.games[i].get("description", "")
                        )
                        return
                except Exception as exc:
                    print(f"Failed to open modify UI: {exc}")

                try:
                    app.show_static_modal(
                        f"Modify {app.games[i].get('title', '')}",
                        "Static modify UI not available. Check console output for details."
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