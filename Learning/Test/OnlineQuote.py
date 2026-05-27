import json
import random
import tkinter as tk
from pathlib import Path


class QuoteWidget:
    BG = "#1e1e2e"
    CARD_BG = "#2a2a3c"
    TEXT_EN = "#cdd6f4"
    TEXT_ZH = "#a6adc8"
    TEXT_SRC = "#7f849c"
    ACCENT = "#89b4fa"
    BTN_BG = "#3a3a4e"
    BTN_HOVER = "#4a4a5e"

    def __init__(self):
        self.quotes = self._load_quotes()
        if not self.quotes:
            raise SystemExit("quotes.json 加载失败或为空")

        self.root = tk.Tk()
        self.root.title("Daily Quote")
        self.root.configure(bg=self.BG)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        self._drag_x = 0
        self._drag_y = 0
        self._last_index = -1
        self._build_ui()
        self._refresh_quote()
        self._center_window()

    def _load_quotes(self):
        json_path = Path(__file__).parent / "quotes.json"
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_ui(self):
        # --- top bar: drag + close ---
        top = tk.Frame(self.root, bg=self.BG, cursor="fleur")
        top.pack(fill="x")
        top.bind("<ButtonPress-1>", self._start_drag)
        top.bind("<B1-Motion>", self._on_drag)

        tk.Label(top, text="  ✦ Daily Quote", bg=self.BG, fg=self.ACCENT,
                 font=("Segoe UI", 9, "bold")).pack(side="left", pady=(6, 0))

        close_btn = tk.Label(top, text="✕ ", bg=self.BG, fg=self.TEXT_SRC,
                             font=("Segoe UI", 10), cursor="hand2")
        close_btn.pack(side="right", pady=(4, 0))
        close_btn.bind("<Enter>", lambda e: close_btn.configure(fg="#f38ba8"))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(fg=self.TEXT_SRC))
        close_btn.bind("<Button-1>", lambda e: self.root.destroy())

        # --- card ---
        card = tk.Frame(self.root, bg=self.CARD_BG, padx=20, pady=16)
        card.pack(padx=10, pady=(4, 10))

        self.lbl_en = tk.Label(card, bg=self.CARD_BG, fg=self.TEXT_EN,
                               font=("Segoe UI", 11), wraplength=340,
                               justify="center")
        self.lbl_en.pack(pady=(0, 10))

        self.lbl_zh = tk.Label(card, bg=self.CARD_BG, fg=self.TEXT_ZH,
                               font=("Microsoft YaHei UI", 10), wraplength=340,
                               justify="center")
        self.lbl_zh.pack(pady=(0, 8))

        tk.Frame(card, bg=self.ACCENT, height=1).pack(fill="x", pady=(0, 8))

        self.lbl_src = tk.Label(card, bg=self.CARD_BG, fg=self.TEXT_SRC,
                                font=("Segoe UI", 9, "italic"))
        self.lbl_src.pack()

        # --- counter ---
        self.lbl_count = tk.Label(self.root, bg=self.BG, fg=self.TEXT_SRC,
                                  font=("Segoe UI", 8))
        self.lbl_count.pack(pady=(2, 0))

        # --- button ---
        self.btn = tk.Label(self.root, text="⟳  换一句", bg=self.BTN_BG,
                            fg=self.TEXT_EN, font=("Segoe UI", 10),
                            cursor="hand2", padx=14, pady=4)
        self.btn.pack(pady=(2, 12))
        self.btn.bind("<Enter>", lambda e: self.btn.configure(bg=self.BTN_HOVER))
        self.btn.bind("<Leave>", lambda e: self.btn.configure(bg=self.BTN_BG))
        self.btn.bind("<Button-1>", lambda e: self._refresh_quote())

        # --- click card to switch too ---
        for w in (card, self.lbl_en, self.lbl_zh, self.lbl_src):
            w.bind("<Button-1>", lambda e: self._refresh_quote())
            w.configure(cursor="hand2")

    def _refresh_quote(self):
        idx = random.randint(0, len(self.quotes) - 1)
        while idx == self._last_index and len(self.quotes) > 1:
            idx = random.randint(0, len(self.quotes) - 1)
        self._last_index = idx

        q = self.quotes[idx]
        self.lbl_en.configure(text=f'"{q["english"]}"')
        self.lbl_zh.configure(text=q["chinese"])
        self.lbl_src.configure(text=f'—— {q["source"]}')
        self.lbl_count.configure(text=f"{idx + 1} / {len(self.quotes)}")

    def _center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        x = sw - w - 40
        y = 40
        self.root.geometry(f"+{x}+{y}")

    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event):
        x = self.root.winfo_x() + event.x - self._drag_x
        y = self.root.winfo_y() + event.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    QuoteWidget().run()
