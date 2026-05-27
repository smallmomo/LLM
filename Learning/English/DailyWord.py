import html as html_mod
import json
import random
import re
import threading
import tkinter as tk
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path


class DailyWordWidget:
    BG = "#1e1e2e"
    CARD_BG = "#2a2a3c"
    TEXT_EN = "#cdd6f4"
    TEXT_ZH = "#a6adc8"
    TEXT_SRC = "#7f849c"
    ACCENT = "#89b4fa"
    ACCENT2 = "#a6e3a1"
    ACCENT3 = "#f9e2af"
    BTN_BG = "#3a3a4e"
    BTN_HOVER = "#4a4a5e"

    MAX_EXAMPLES = 3

    def __init__(self):
        self.vocab_dir = Path(__file__).parent / "vocabulary"
        self.units = self._load_vocabulary()
        if not self.units:
            raise SystemExit("vocabulary 目录下没有找到 unit*.json 文件")

        self.unit_names = sorted(self.units.keys())
        self.current_unit_idx = 0
        self._last_word_idx = -1
        self._drag_x = self._drag_y = 0

        self.root = tk.Tk()
        self.root.title("Daily Word")
        self.root.configure(bg=self.BG)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        self._build_ui()
        self._show_daily_word()
        self._position_window()

    # ── data ──────────────────────────────────────────────────

    def _load_vocabulary(self):
        units = {}
        for f in sorted(self.vocab_dir.glob("unit*.json")):
            with open(f, "r", encoding="utf-8") as fh:
                units[f.stem] = json.load(fh)
        return units

    def _fetch_from_api(self, word):
        """从在线 API 获取例句和词源"""
        examples, etymology = [], ""
        encoded = urllib.parse.quote(word)

        # Free Dictionary API → 例句
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{encoded}"
            req = urllib.request.Request(url, headers={"User-Agent": "DailyWord/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list) and data:
                for meaning in data[0].get("meanings", []):
                    for defn in meaning.get("definitions", []):
                        ex = defn.get("example")
                        if ex and len(examples) < self.MAX_EXAMPLES:
                            examples.append({"en": ex, "zh": ""})
        except Exception:
            pass

        # Wiktionary MediaWiki API → 词源
        try:
            # 先查页面有哪些 section，找到 Etymology
            url = (
                f"https://en.wiktionary.org/w/api.php"
                f"?action=parse&page={encoded}&prop=sections&format=json"
            )
            req = urllib.request.Request(url, headers={"User-Agent": "DailyWord/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            ety_idx = None
            for sec in data.get("parse", {}).get("sections", []):
                if sec.get("line", "").lower().startswith("ety"):
                    ety_idx = sec["index"]
                    break
            if ety_idx:
                url2 = (
                    f"https://en.wiktionary.org/w/api.php"
                    f"?action=parse&page={encoded}&prop=text"
                    f"&section={ety_idx}&format=json"
                )
                req2 = urllib.request.Request(url2, headers={"User-Agent": "DailyWord/1.0"})
                with urllib.request.urlopen(req2, timeout=8) as resp2:
                    data2 = json.loads(resp2.read().decode("utf-8"))
                html_text = data2.get("parse", {}).get("text", {}).get("*", "")
                text = re.sub(r"<style[^>]*>.*?</style>", "", html_text, flags=re.S)
                text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.S)
                text = re.sub(r"<[^>]+>", " ", text)
                text = html_mod.unescape(text)
                text = re.sub(r"\[\s*edit\s*\]", "", text)
                text = re.sub(r"\s+", " ", text).strip()
                text = re.sub(r"^Etymology\s*(tree\s*)?", "", text, flags=re.I)
                # Skip if it's just a tree of proto-language names
                if text and not re.match(r"^Proto-", text):
                    etymology = text[:300]
                elif "from " in text:
                    # Extract from the "From ..." part
                    m = re.search(r"\bFrom\s+", text)
                    if m:
                        etymology = text[m.start():][:300]
        except Exception:
            pass

        return examples, etymology

    def _save_back(self, unit_name, word_idx, examples, etymology):
        """将联网获取的数据回写到 JSON 文件"""
        words = self.units[unit_name]
        if word_idx >= len(words):
            return
        w = words[word_idx]
        updated = False
        if examples and not w.get("examples"):
            w["examples"] = examples
            updated = True
        if etymology and not w.get("etymology"):
            w["etymology"] = etymology
            updated = True
        if updated:
            filepath = self.vocab_dir / f"{unit_name}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(words, f, ensure_ascii=False, indent=2)

    # ── selection ─────────────────────────────────────────────

    def _show_daily_word(self):
        """基于日期选取今日单词（同一天同一个 unit 显示同一个词）"""
        seed = date.today().toordinal() + self.current_unit_idx
        words = self.units[self.unit_names[self.current_unit_idx]]
        idx = random.Random(seed).randint(0, len(words) - 1)
        self._last_word_idx = idx
        self._display_word(idx)

    def _refresh_word(self, event=None):
        words = self.units[self.unit_names[self.current_unit_idx]]
        if not words:
            return
        idx = random.randint(0, len(words) - 1)
        while idx == self._last_word_idx and len(words) > 1:
            idx = random.randint(0, len(words) - 1)
        self._last_word_idx = idx
        self._display_word(idx)

    # ── display ───────────────────────────────────────────────

    def _display_word(self, idx):
        unit_name = self.unit_names[self.current_unit_idx]
        w = self.units[unit_name][idx]

        meanings = w.get("meanings", [])
        meanings_text = "\n".join(
            f"[{m['pos']}] {m['definition']}" for m in meanings
        )

        self.lbl_word.configure(text=w["word"])
        self.lbl_phonetic.configure(text=w.get("phonetic", ""))
        self.lbl_meanings.configure(text=meanings_text)
        self.lbl_count.configure(
            text=f"{idx + 1} / {len(self.units[unit_name])}  ·  {unit_name}"
        )

        examples = w.get("examples") or []
        etymology = w.get("etymology") or ""

        self.lbl_examples.configure(
            text="\n".join(
                f"{i}. {e['en']}" for i, e in enumerate(examples[:self.MAX_EXAMPLES], 1)
            )
            if examples else "查询中…"
        )
        self.lbl_etymology.configure(text=etymology if etymology else "暂无词源信息")
        self.canvas.yview_moveto(0)

        # 缺少例句或词源时联网查询
        if not examples and not etymology:
            def _bg():
                ex, et = self._fetch_from_api(w["word"])
                self._save_back(unit_name, idx, ex, et)
                self.root.after(0, lambda: self._on_fetched(ex, et))

            threading.Thread(target=_bg, daemon=True).start()

    def _on_fetched(self, examples, etymology):
        if examples:
            self.lbl_examples.configure(
                text="\n".join(
                    f"{i}. {e['en']}"
                    for i, e in enumerate(examples[:self.MAX_EXAMPLES], 1)
                )
            )
        else:
            self.lbl_examples.configure(text="暂无例句")
        if etymology:
            self.lbl_etymology.configure(text=etymology)

    # ── unit navigation ───────────────────────────────────────

    def _prev_unit(self, event=None):
        self.current_unit_idx = (self.current_unit_idx - 1) % len(self.unit_names)
        self._last_word_idx = -1
        self._show_daily_word()

    def _next_unit(self, event=None):
        self.current_unit_idx = (self.current_unit_idx + 1) % len(self.unit_names)
        self._last_word_idx = -1
        self._show_daily_word()

    # ── UI construction ───────────────────────────────────────

    def _build_ui(self):
        # top bar
        top = tk.Frame(self.root, bg=self.BG, cursor="fleur")
        top.pack(fill="x")
        top.bind("<ButtonPress-1>", self._start_drag)
        top.bind("<B1-Motion>", self._on_drag)

        tk.Label(
            top, text="  ✦ Daily Word", bg=self.BG, fg=self.ACCENT,
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left", pady=(6, 0))

        nav = tk.Frame(top, bg=self.BG)
        nav.pack(side="right", pady=(6, 0))
        for sym, cmd in (("◀", self._prev_unit), ("▶", self._next_unit)):
            b = tk.Label(
                nav, text=sym, bg=self.BG, fg=self.TEXT_SRC,
                font=("Segoe UI", 9), cursor="hand2",
            )
            b.pack(side="left", padx=2)
            b.bind("<Button-1>", cmd)
            b.bind("<Enter>", lambda e, b=b: b.configure(fg=self.ACCENT))
            b.bind("<Leave>", lambda e, b=b: b.configure(fg=self.TEXT_SRC))

        close = tk.Label(
            nav, text="✕ ", bg=self.BG, fg=self.TEXT_SRC,
            font=("Segoe UI", 10), cursor="hand2",
        )
        close.pack(side="left", padx=(6, 0))
        close.bind("<Enter>", lambda e: close.configure(fg="#f38ba8"))
        close.bind("<Leave>", lambda e: close.configure(fg=self.TEXT_SRC))
        close.bind("<Button-1>", lambda e: self.root.destroy())

        # scrollable card
        wrapper = tk.Frame(self.root, bg=self.BG)
        wrapper.pack(padx=10, pady=(4, 0))

        self.canvas = tk.Canvas(
            wrapper, bg=self.CARD_BG, highlightthickness=0, width=360, height=340,
        )
        self.canvas.pack()

        self.card = tk.Frame(self.canvas, bg=self.CARD_BG, padx=20, pady=16)
        self.canvas.create_window((0, 0), window=self.card, anchor="nw", width=360)
        self.card.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.root.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )

        # word + phonetic
        self.lbl_word = tk.Label(
            self.card, bg=self.CARD_BG, fg=self.ACCENT,
            font=("Segoe UI", 20, "bold"),
        )
        self.lbl_word.pack(pady=(0, 2))

        self.lbl_phonetic = tk.Label(
            self.card, bg=self.CARD_BG, fg=self.TEXT_SRC,
            font=("Segoe UI", 10),
        )
        self.lbl_phonetic.pack(pady=(0, 10))

        # meanings
        self._section_label("释义", self.ACCENT)
        self.lbl_meanings = tk.Label(
            self.card, bg=self.CARD_BG, fg=self.TEXT_ZH,
            font=("Microsoft YaHei UI", 10), wraplength=320, justify="left",
        )
        self.lbl_meanings.pack(pady=(0, 10))

        # examples
        self._section_label("例句", self.ACCENT2)
        self.lbl_examples = tk.Label(
            self.card, bg=self.CARD_BG, fg=self.TEXT_EN,
            font=("Segoe UI", 10), wraplength=320, justify="left",
        )
        self.lbl_examples.pack(pady=(0, 10))

        # etymology
        self._section_label("词源", self.ACCENT3)
        self.lbl_etymology = tk.Label(
            self.card, bg=self.CARD_BG, fg=self.TEXT_ZH,
            font=("Microsoft YaHei UI", 9), wraplength=320, justify="left",
        )
        self.lbl_etymology.pack(pady=(0, 4))

        # counter
        self.lbl_count = tk.Label(
            self.root, bg=self.BG, fg=self.TEXT_SRC, font=("Segoe UI", 8),
        )
        self.lbl_count.pack(pady=(4, 0))

        # refresh button
        self.btn = tk.Label(
            self.root, text="⟳  换一个", bg=self.BTN_BG, fg=self.TEXT_EN,
            font=("Segoe UI", 10), cursor="hand2", padx=14, pady=4,
        )
        self.btn.pack(pady=(2, 12))
        self.btn.bind("<Enter>", lambda e: self.btn.configure(bg=self.BTN_HOVER))
        self.btn.bind("<Leave>", lambda e: self.btn.configure(bg=self.BTN_BG))
        self.btn.bind("<Button-1>", self._refresh_word)

    def _section_label(self, title, color):
        tk.Label(
            self.card, text=f"───── {title} ─────", bg=self.CARD_BG, fg=color,
            font=("Segoe UI", 8),
        ).pack(pady=(0, 4))

    # ── window helpers ────────────────────────────────────────

    def _position_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        x = self.root.winfo_screenwidth() - w - 40
        self.root.geometry(f"+{x}+40")

    def _start_drag(self, event):
        self._drag_x, self._drag_y = event.x, event.y

    def _on_drag(self, event):
        x = self.root.winfo_x() + event.x - self._drag_x
        y = self.root.winfo_y() + event.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    DailyWordWidget().run()
