"""
Main.py — Tkinter GUI for the Real-Time Currency Converter.

Requires:
    pip install requests
"""

import threading
import tkinter as tk
from tkinter import font as tk_font
from tkinter import ttk, messagebox

from converter import RealTimeCurrencyConverter

# ---------------------------------------------------------------------------
# Colour palette & style constants
# ---------------------------------------------------------------------------
BG_DARK   = "#0f0f1a"
BG_PANEL  = "#1a1a2e"
BG_CARD   = "#16213e"
ACCENT    = "#e94560"
ACCENT2   = "#0f3460"
TEXT_PRI  = "#eaeaea"
TEXT_SEC  = "#a0a0b8"
TEXT_DIM  = "#5a5a7a"
ENTRY_BG  = "#252540"
BTN_HOVER = "#ff5a75"
RADIUS    = 12           # used via padding trick (not real border-radius for tk)

FONT_FAMILY  = "Segoe UI"
FONT_TITLE   = (FONT_FAMILY, 22, "bold")
FONT_LABEL   = (FONT_FAMILY, 10)
FONT_COMBO   = (FONT_FAMILY, 11)
FONT_AMOUNT  = (FONT_FAMILY, 14, "bold")
FONT_RESULT  = (FONT_FAMILY, 20, "bold")
FONT_SMALL   = (FONT_FAMILY, 9)
FONT_STATUS  = (FONT_FAMILY, 9, "italic")

# Fallback font if Segoe UI is unavailable
import sys
if sys.platform != "win32":
    FONT_FAMILY = "DejaVu Sans"
    FONT_TITLE  = (FONT_FAMILY, 22, "bold")
    FONT_LABEL  = (FONT_FAMILY, 10)
    FONT_COMBO  = (FONT_FAMILY, 11)
    FONT_AMOUNT = (FONT_FAMILY, 14, "bold")
    FONT_RESULT = (FONT_FAMILY, 20, "bold")
    FONT_SMALL  = (FONT_FAMILY, 9)
    FONT_STATUS = (FONT_FAMILY, 9, "italic")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class CurrencyConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("💱 Real-Time Currency Converter")
        self.geometry("560x640")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)

        # State
        self.converter: RealTimeCurrencyConverter | None = None
        self.loading = False

        # Build UI (converter loaded async)
        self._build_ui()
        self._load_converter()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        """Assemble all widgets."""
        # ── Header ──────────────────────────────────────────────────
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill="x", padx=30, pady=(30, 10))

        tk.Label(
            header,
            text="💱 Currency Converter",
            font=FONT_TITLE,
            bg=BG_DARK,
            fg=TEXT_PRI,
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Live exchange rates · powered by exchangerate-api.com",
            font=FONT_SMALL,
            bg=BG_DARK,
            fg=TEXT_DIM,
        ).pack(anchor="w", pady=(2, 0))

        self._separator(BG_DARK, pady=8)

        # ── Main card ───────────────────────────────────────────────
        card = tk.Frame(self, bg=BG_CARD, padx=28, pady=28)
        card.pack(fill="both", padx=30, pady=6)

        # FROM row
        tk.Label(card, text="FROM CURRENCY", font=FONT_LABEL, bg=BG_CARD, fg=TEXT_SEC).grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        self.from_var = tk.StringVar(value="USD")
        self.from_combo = self._styled_combo(card, self.from_var)
        self.from_combo.grid(row=1, column=0, sticky="ew", pady=(0, 18))

        # ↔ swap button (centre column)
        card.columnconfigure(1, minsize=54)
        self.swap_btn = tk.Button(
            card,
            text="⇄",
            font=(FONT_FAMILY, 18, "bold"),
            bg=ACCENT2,
            fg=TEXT_PRI,
            activebackground=ACCENT,
            activeforeground=TEXT_PRI,
            bd=0,
            cursor="hand2",
            command=self._swap_currencies,
        )
        self.swap_btn.grid(row=1, column=1, padx=10, pady=(0, 18))
        self._add_hover(self.swap_btn, ACCENT, ACCENT2)

        # TO row (share row=0/1 in column 2)
        tk.Label(card, text="TO CURRENCY", font=FONT_LABEL, bg=BG_CARD, fg=TEXT_SEC).grid(
            row=0, column=2, sticky="w", pady=(0, 4)
        )
        self.to_var = tk.StringVar(value="INR")
        self.to_combo = self._styled_combo(card, self.to_var)
        self.to_combo.grid(row=1, column=2, sticky="ew", pady=(0, 18))

        card.columnconfigure(0, weight=1)
        card.columnconfigure(2, weight=1)

        # Amount
        tk.Label(card, text="AMOUNT", font=FONT_LABEL, bg=BG_CARD, fg=TEXT_SEC).grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(0, 4)
        )
        self.amount_var = tk.StringVar(value="1")
        amount_entry = tk.Entry(
            card,
            textvariable=self.amount_var,
            font=FONT_AMOUNT,
            bg=ENTRY_BG,
            fg=TEXT_PRI,
            insertbackground=ACCENT,
            relief="flat",
            bd=0,
        )
        amount_entry.grid(row=3, column=0, columnspan=3, sticky="ew", ipady=10, pady=(0, 22))

        # Convert button
        self.convert_btn = tk.Button(
            card,
            text="Convert",
            font=(FONT_FAMILY, 13, "bold"),
            bg=ACCENT,
            fg="white",
            activebackground=BTN_HOVER,
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            height=2,
            command=self._do_convert,
        )
        self.convert_btn.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0, 22))
        self._add_hover(self.convert_btn, BTN_HOVER, ACCENT)

        # Result box
        result_frame = tk.Frame(card, bg=ACCENT2, padx=2, pady=2)
        result_frame.grid(row=5, column=0, columnspan=3, sticky="ew")

        result_inner = tk.Frame(result_frame, bg=ENTRY_BG)
        result_inner.pack(fill="both", expand=True)

        self.result_var = tk.StringVar(value="—")
        tk.Label(
            result_inner,
            textvariable=self.result_var,
            font=FONT_RESULT,
            bg=ENTRY_BG,
            fg=ACCENT,
            pady=18,
        ).pack()

        # ── Status bar ──────────────────────────────────────────────
        self._separator(BG_DARK, pady=4)
        self.status_var = tk.StringVar(value="⏳  Loading exchange rates…")
        tk.Label(
            self,
            textvariable=self.status_var,
            font=FONT_STATUS,
            bg=BG_DARK,
            fg=TEXT_DIM,
        ).pack(anchor="w", padx=30, pady=(0, 16))

    def _separator(self, bg: str, pady: int = 4):
        tk.Frame(self, bg=TEXT_DIM, height=1).pack(fill="x", padx=30, pady=pady)

    def _styled_combo(self, parent, textvariable: tk.StringVar) -> ttk.Combobox:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dark.TCombobox",
            fieldbackground=ENTRY_BG,
            background=ENTRY_BG,
            foreground=TEXT_PRI,
            arrowcolor=ACCENT,
            selectbackground=ACCENT2,
            selectforeground=TEXT_PRI,
            bordercolor=ACCENT2,
            lightcolor=ACCENT2,
            darkcolor=ACCENT2,
        )
        combo = ttk.Combobox(
            parent,
            textvariable=textvariable,
            font=FONT_COMBO,
            state="readonly",
            style="Dark.TCombobox",
        )
        return combo

    @staticmethod
    def _add_hover(widget: tk.Button, hover_color: str, normal_color: str):
        widget.bind("<Enter>", lambda _: widget.configure(bg=hover_color))
        widget.bind("<Leave>", lambda _: widget.configure(bg=normal_color))

    # ------------------------------------------------------------------
    # Async converter loading
    # ------------------------------------------------------------------

    def _load_converter(self):
        self.loading = True
        self.convert_btn.configure(state="disabled", text="Loading…")
        t = threading.Thread(target=self._fetch_rates_thread, daemon=True)
        t.start()

    def _fetch_rates_thread(self):
        try:
            conv = RealTimeCurrencyConverter(base="USD")
            self.after(0, self._on_rates_loaded, conv)
        except Exception as exc:
            self.after(0, self._on_rates_error, str(exc))

    def _on_rates_loaded(self, conv: RealTimeCurrencyConverter):
        self.converter = conv
        currencies = conv.get_currencies()
        self.from_combo["values"] = currencies
        self.to_combo["values"]   = currencies
        if "USD" in currencies:
            self.from_var.set("USD")
        if "INR" in currencies:
            self.to_var.set("INR")
        self.convert_btn.configure(state="normal", text="Convert")
        self.status_var.set(f"✅  Rates loaded — {len(currencies)} currencies available")
        self.loading = False

    def _on_rates_error(self, error: str):
        self.status_var.set(f"❌  Failed to load rates: {error}")
        self.convert_btn.configure(state="disabled", text="Offline")
        self.loading = False
        messagebox.showerror(
            "Connection Error",
            f"Could not fetch exchange rates:\n\n{error}\n\n"
            "Please check your internet connection and restart the app.",
        )

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _swap_currencies(self):
        src = self.from_var.get()
        tgt = self.to_var.get()
        self.from_var.set(tgt)
        self.to_var.set(src)

    def _do_convert(self):
        if not self.converter or self.loading:
            return

        from_curr = self.from_var.get().strip()
        to_curr   = self.to_var.get().strip()
        amount_s  = self.amount_var.get().strip()

        # Validate amount
        try:
            amount = float(amount_s)
            if amount < 0:
                raise ValueError("negative")
        except ValueError:
            messagebox.showwarning("Invalid Amount", "Please enter a valid positive number.")
            return

        # Convert
        try:
            result = self.converter.convert(from_curr, to_curr, amount)
            self.result_var.set(f"{amount:,g} {from_curr}  =  {result:,.4f} {to_curr}")
            self.status_var.set(f"✅  1 {from_curr} = {self.converter.convert(from_curr, to_curr, 1):,.6f} {to_curr}")
        except Exception as exc:
            messagebox.showerror("Conversion Error", str(exc))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = CurrencyConverterApp()
    app.mainloop()
