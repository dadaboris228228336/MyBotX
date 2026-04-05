#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 UI/pattern_editor.py
Редактор паттернов — показывает скриншот, позволяет выделить область и сохранить как паттерн.
"""

import tkinter as tk
from tkinter import simpledialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk
import numpy as np

from .theme import THEME

PATTERNS_DIR = Path(__file__).parent.parent / "processes" / "BOT" / "patterns"


class PatternEditor:
    """Виджет для просмотра скриншота и вырезания паттернов"""

    def __init__(self, parent, log_callback=None):
        self.parent = parent
        self.log = log_callback or print
        self.screenshot_arr = None   # numpy BGR array
        self.tk_image = None         # PhotoImage для canvas
        self.scale = 1.0             # масштаб отображения

        # Координаты выделения
        self.sel_start = None
        self.sel_rect = None

        self._build(parent)

    def _build(self, parent):
        # Кнопки сверху
        btn_row = tk.Frame(parent, bg=THEME["bg_main"])
        btn_row.pack(fill=tk.X, pady=(0, 6))

        tk.Button(
            btn_row, text="📸  Обновить скриншот",
            bg=THEME["bg_panel"], fg=THEME["accent_blue"],
            font=THEME["font_normal"], relief=tk.FLAT, cursor="hand2",
            padx=12, pady=6,
            command=self.refresh_screenshot
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_row, text="✂️  Сохранить выделение",
            bg=THEME["bg_panel"], fg=THEME["accent_green"],
            font=THEME["font_normal"], relief=tk.FLAT, cursor="hand2",
            padx=12, pady=6,
            command=self.save_selection
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_row, text="🗂  Открыть папку паттернов",
            bg=THEME["bg_panel"], fg=THEME["text_secondary"],
            font=THEME["font_normal"], relief=tk.FLAT, cursor="hand2",
            padx=12, pady=6,
            command=self.open_patterns_folder
        ).pack(side=tk.LEFT)

        self.hint_label = tk.Label(
            btn_row,
            text="Зажмите ЛКМ чтобы выделить область",
            bg=THEME["bg_main"], fg=THEME["text_secondary"],
            font=THEME["font_small"]
        )
        self.hint_label.pack(side=tk.RIGHT, padx=8)

        # Canvas для скриншота
        canvas_frame = tk.Frame(parent, bg=THEME["bg_input"])
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg=THEME["bg_input"],
            cursor="crosshair",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Привязка мыши
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)

        # Список паттернов справа
        list_frame = tk.Frame(parent, bg=THEME["bg_panel"], width=180)
        list_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(6, 0))
        list_frame.pack_propagate(False)

        tk.Label(
            list_frame, text="📁 Паттерны",
            bg=THEME["bg_panel"], fg=THEME["accent_blue"],
            font=THEME["font_header"]
        ).pack(pady=8)

        self.pattern_listbox = tk.Listbox(
            list_frame,
            bg=THEME["bg_input"], fg=THEME["text_primary"],
            font=THEME["font_small"],
            selectbackground=THEME["accent_blue"],
            relief=tk.FLAT, bd=0,
            activestyle="none"
        )
        self.pattern_listbox.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

        tk.Button(
            list_frame, text="🗑 Удалить",
            bg=THEME["bg_panel"], fg=THEME["accent_red"],
            font=THEME["font_small"], relief=tk.FLAT, cursor="hand2",
            command=self.delete_selected_pattern
        ).pack(pady=4)

        self.refresh_pattern_list()

    # ─────────────────────────────────────────────
    # СКРИНШОТ
    # ─────────────────────────────────────────────

    def load_screenshot(self, arr: np.ndarray):
        """Загрузить скриншот (numpy BGR array) в canvas"""
        self.screenshot_arr = arr

        # BGR → RGB → PIL → PhotoImage
        rgb = arr[:, :, ::-1]
        img = Image.fromarray(rgb)

        # Масштабируем под размер canvas
        cw = self.canvas.winfo_width() or 760
        ch = self.canvas.winfo_height() or 420
        self.scale = min(cw / img.width, ch / img.height, 1.0)

        new_w = int(img.width * self.scale)
        new_h = int(img.height * self.scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)

        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.img_offset = (0, 0)
        self.log("✅ Скриншот загружен в редактор")

    def refresh_screenshot(self):
        """Запрашивает новый скриншот через callback"""
        if hasattr(self, "_refresh_callback") and self._refresh_callback:
            self._refresh_callback()
        else:
            self.log("⚠️ Сначала подключитесь к устройству (нажмите СТАРТ)")

    def set_refresh_callback(self, callback):
        """Устанавливает функцию для получения нового скриншота"""
        self._refresh_callback = callback

    # ─────────────────────────────────────────────
    # ВЫДЕЛЕНИЕ МЫШЬЮ
    # ─────────────────────────────────────────────

    def _on_mouse_down(self, event):
        self.sel_start = (event.x, event.y)
        if self.sel_rect:
            self.canvas.delete(self.sel_rect)

    def _on_mouse_drag(self, event):
        if self.sel_start is None:
            return
        if self.sel_rect:
            self.canvas.delete(self.sel_rect)
        self.sel_rect = self.canvas.create_rectangle(
            self.sel_start[0], self.sel_start[1], event.x, event.y,
            outline=THEME["accent_green"], width=2, dash=(4, 2)
        )
        # Показываем размер
        w = abs(event.x - self.sel_start[0])
        h = abs(event.y - self.sel_start[1])
        self.hint_label.config(text=f"Выделено: {w}×{h} px")

    def _on_mouse_up(self, event):
        self.sel_end = (event.x, event.y)

    # ─────────────────────────────────────────────
    # СОХРАНЕНИЕ ПАТТЕРНА
    # ─────────────────────────────────────────────

    def save_selection(self):
        """Вырезает выделенную область и сохраняет как паттерн"""
        if self.screenshot_arr is None:
            messagebox.showwarning("Нет скриншота", "Сначала сделайте скриншот!")
            return

        if not hasattr(self, "sel_end") or self.sel_start is None:
            messagebox.showwarning("Нет выделения", "Выделите область на скриншоте!")
            return

        # Координаты в пикселях оригинала
        x1 = int(min(self.sel_start[0], self.sel_end[0]) / self.scale)
        y1 = int(min(self.sel_start[1], self.sel_end[1]) / self.scale)
        x2 = int(max(self.sel_start[0], self.sel_end[0]) / self.scale)
        y2 = int(max(self.sel_start[1], self.sel_end[1]) / self.scale)

        if x2 - x1 < 5 or y2 - y1 < 5:
            messagebox.showwarning("Слишком мало", "Выделите большую область!")
            return

        # Спрашиваем имя
        name = simpledialog.askstring(
            "Имя паттерна",
            "Введите имя паттерна (без .png):\nНапример: btn_attack",
            parent=self.parent
        )
        if not name:
            return

        # Вырезаем и сохраняем
        crop = self.screenshot_arr[y1:y2, x1:x2]
        rgb = crop[:, :, ::-1]
        img = Image.fromarray(rgb)

        PATTERNS_DIR.mkdir(exist_ok=True)
        save_path = PATTERNS_DIR / f"{name}.png"
        img.save(save_path)

        self.log(f"✅ Паттерн сохранён: {name}.png ({x2-x1}×{y2-y1} px)")
        self.refresh_pattern_list()

        # Рисуем зелёный прямоугольник на canvas
        if self.sel_rect:
            self.canvas.delete(self.sel_rect)
        self.sel_rect = self.canvas.create_rectangle(
            self.sel_start[0], self.sel_start[1],
            self.sel_end[0], self.sel_end[1],
            outline=THEME["accent_green"], width=2
        )

    # ─────────────────────────────────────────────
    # СПИСОК ПАТТЕРНОВ
    # ─────────────────────────────────────────────

    def refresh_pattern_list(self):
        """Обновить список паттернов"""
        self.pattern_listbox.delete(0, tk.END)
        PATTERNS_DIR.mkdir(exist_ok=True)
        for f in sorted(PATTERNS_DIR.glob("*.png")):
            self.pattern_listbox.insert(tk.END, f.stem)

    def delete_selected_pattern(self):
        sel = self.pattern_listbox.curselection()
        if not sel:
            return
        name = self.pattern_listbox.get(sel[0])
        path = PATTERNS_DIR / f"{name}.png"
        if messagebox.askyesno("Удалить", f"Удалить паттерн '{name}'?"):
            path.unlink(missing_ok=True)
            self.log(f"🗑 Паттерн удалён: {name}")
            self.refresh_pattern_list()

    def open_patterns_folder(self):
        import subprocess
        subprocess.Popen(f'explorer "{PATTERNS_DIR}"')
