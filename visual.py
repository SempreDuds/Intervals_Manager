"""Tema escuro acessível, em Tkinter/ttk sem dependências visuais extras."""
from tkinter import ttk

BG = '#0B1220'
PANEL = '#111D30'
SURFACE = '#192840'
INPUT = '#1B2A43'
TEXT = '#F1F5FC'
MUTED = '#A8BAD0'
ACCENT = '#42D7C5'
ACCENT_DARK = '#062623'
BORDER = '#2C3B53'
ERROR = '#FF9090'


def activate(root):
    root.configure(bg=BG)
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', font=('Segoe UI', 10), background=BG, foreground=TEXT)
    style.configure('TFrame', background=BG)
    style.configure('Surface.TFrame', background=PANEL)
    style.configure('Header.TFrame', background=PANEL)
    style.configure('TLabel', background=BG, foreground=TEXT)
    style.configure('Muted.TLabel', background=BG, foreground=MUTED)
    style.configure('Header.TLabel', background=PANEL, foreground=TEXT)
    style.configure('Title.TLabel', font=('Segoe UI Semibold', 18), foreground=TEXT)
    style.configure('Subtitle.TLabel', foreground=MUTED, font=('Segoe UI', 10))
    style.configure('TEntry', fieldbackground=INPUT, background=INPUT, foreground=TEXT,
                    insertcolor=TEXT, bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
                    padding=(9, 7))
    style.map('TEntry', fieldbackground=[('disabled', SURFACE)], foreground=[('disabled', MUTED)])
    style.configure('TCombobox', fieldbackground=INPUT, background=INPUT, foreground=TEXT,
                    arrowcolor=ACCENT, bordercolor=BORDER, padding=(9, 6))
    style.map('TCombobox', fieldbackground=[('readonly', INPUT)], foreground=[('readonly', TEXT)],
              selectbackground=[('readonly', INPUT)], selectforeground=[('readonly', TEXT)])
    style.configure('TButton', background=SURFACE, foreground=TEXT,
                    bordercolor=BORDER, font=('Segoe UI Semibold', 10), padding=(15, 10))
    style.map('TButton', background=[('active', '#253A58'), ('pressed', '#1A314C')],
              foreground=[('active', '#FFFFFF')])
    style.configure('Accent.TButton', background=ACCENT, foreground=ACCENT_DARK,
                    bordercolor=ACCENT, font=('Segoe UI Semibold', 10), padding=(16, 10))
    style.map('Accent.TButton', background=[('active', '#7AEADC'), ('pressed', '#29BAA8')],
              foreground=[('active', ACCENT_DARK)])
    style.configure('Danger.TButton', background='#562936', foreground='#FFE5E9',
                    bordercolor='#7C394B', padding=(15, 10))
    style.map('Danger.TButton', background=[('active', '#763445')])
    style.configure('TCheckbutton', background=BG, foreground=TEXT)
    style.map('TCheckbutton', background=[('active', BG)], foreground=[('active', TEXT)])
    style.configure('TNotebook', background=BG, borderwidth=0, tabmargins=(0, 0, 0, 10))
    style.configure('TNotebook.Tab', background=PANEL, foreground=MUTED,
                    borderwidth=0, padding=(16, 13), font=('Segoe UI Semibold', 10))
    style.map('TNotebook.Tab', background=[('selected', SURFACE), ('active', '#203350')],
              foreground=[('selected', ACCENT), ('active', TEXT)])
    style.configure('Treeview', background=PANEL, fieldbackground=PANEL, foreground=TEXT,
                    bordercolor=BORDER, rowheight=32, font=('Segoe UI', 10))
    style.configure('Treeview.Heading', background=SURFACE, foreground=MUTED,
                    relief='flat', font=('Segoe UI Semibold', 10), padding=(8, 9))
    style.map('Treeview', background=[('selected', '#246B77')], foreground=[('selected', '#FFFFFF')])
    style.configure('TPanedwindow', background=BORDER)
    style.configure('Vertical.TScrollbar', background=SURFACE, troughcolor=BG, bordercolor=BG)
    style.configure('Horizontal.TScrollbar', background=SURFACE, troughcolor=BG, bordercolor=BG)
    style.configure('TSeparator', background=BORDER)
    return style


def text_box(widget):
    widget.configure(background=PANEL, foreground=TEXT, insertbackground=TEXT,
                     selectbackground='#246B77', relief='flat', borderwidth=0,
                     padx=14, pady=12, highlightthickness=1, highlightbackground=BORDER)
