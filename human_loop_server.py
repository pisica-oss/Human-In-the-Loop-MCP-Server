#!/usr/bin/env python3
"""Minimal Human-in-the-Loop MCP Server — multiline input only."""

import concurrent.futures
import os
import platform
import secrets
import threading
import tkinter as tk
from typing import Any, Dict

os.environ.setdefault("FASTMCP_LOG_LEVEL", "WARNING")
from fastmcp import FastMCP

PLATFORM = platform.system().lower()
IS_WINDOWS = PLATFORM == "windows"
IS_MACOS = PLATFORM == "darwin"

mcp = FastMCP("HITL")

_gui_init = False
_gui_lock = threading.Lock()


def _ensure_gui():
    global _gui_init
    with _gui_lock:
        if not _gui_init:
            try:
                r = tk.Tk()
                r.withdraw()
                r.destroy()
                _gui_init = True
            except Exception:
                _gui_init = False
    return _gui_init


def _show_dialog(title: str, prompt: str, default: str) -> str | None:
    root = tk.Tk()
    root.withdraw()
    dlg = _MultilineDialog(root, title, prompt, default)
    result = dlg.result
    root.destroy()
    return result


class _MultilineDialog:
    def __init__(self, parent, title, prompt, default=""):
        self.result = None

        self.win = tk.Toplevel(parent)
        self.win.title(title)
        self.win.grab_set()
        self.win.resizable(True, True)
        self.win.geometry("600x420")
        self.win.configure(bg="#FFFFFF")

        if IS_WINDOWS:
            self.win.attributes("-topmost", True)
        elif IS_MACOS:
            self.win.call("wm", "attributes", ".", "-topmost", "1")

        self.win.lift()
        self.win.focus_force()
        self._center()

        frame = tk.Frame(self.win, bg="#FFFFFF")
        frame.pack(fill="both", expand=True, padx=20, pady=16)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        tk.Label(
            frame, text=prompt, bg="#FFFFFF", fg="#202124",
            font=("Segoe UI" if IS_WINDOWS else "Ubuntu", 11),
            wraplength=540, justify="left", anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 12))

        self.text = tk.Text(
            frame, font=("Consolas" if IS_WINDOWS else "Ubuntu Mono", 11),
            wrap="word", relief="solid", borderwidth=1,
            highlightthickness=1, highlightcolor="#0078D4",
            highlightbackground="#E8EAED", padx=8, pady=6,
        )
        self.text.grid(row=1, column=0, sticky="nsew", pady=(0, 12))

        sb = tk.Scrollbar(frame, orient="vertical", command=self.text.yview)
        sb.grid(row=1, column=1, sticky="ns", pady=(0, 12))
        self.text.configure(yscrollcommand=sb.set)

        if default:
            self.text.insert("1.0", default)

        btn_frame = tk.Frame(frame, bg="#FFFFFF")
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="e")

        tk.Button(
            btn_frame, text="Submit", command=self._submit,
            bg="#0078D4", fg="#FFFFFF", font=("Segoe UI" if IS_WINDOWS else "Ubuntu", 10),
            relief="flat", padx=16, pady=6, cursor="hand2",
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            btn_frame, text="Cancel", command=self._cancel,
            bg="#F8F9FA", fg="#202124", font=("Segoe UI" if IS_WINDOWS else "Ubuntu", 10),
            relief="flat", padx=16, pady=6, cursor="hand2",
        ).pack(side="right")

        self.win.protocol("WM_DELETE_WINDOW", self._cancel)
        self.win.bind("<Control-Return>", lambda e: self._submit())
        self.win.bind("<Escape>", lambda e: self._cancel())
        self.text.focus_set()
        self.win.wait_window()

    def _center(self):
        self.win.update_idletasks()
        w, h = self.win.winfo_width(), self.win.winfo_height()
        x = (self.win.winfo_screenwidth() - w) // 2
        y = (self.win.winfo_screenheight() - h) // 2
        self.win.geometry(f"{w}x{h}+{x}+{y}")

    def _submit(self):
        self.result = self.text.get("1.0", tk.END).strip()
        self.win.destroy()

    def _cancel(self):
        self.result = None
        self.win.destroy()


@mcp.tool()
async def get_multiline_input() -> Dict[str, Any]:
    """Ask the user for multi-line text input via a GUI dialog. Use this to get the next task or feedback."""
    if not _ensure_gui():
        return {"success": False, "error": "GUI not available"}

    tag = secrets.token_hex(2).upper()
    title = f"[#{tag}] Input Needed"
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = pool.submit(_show_dialog, title, "What would you like me to do next?", "").result(timeout=600)

    if result is not None:
        return {"success": True, "tag": tag, "user_input": result}
    return {"success": False, "tag": tag, "cancelled": True}


def main():
    mcp.run()


if __name__ == "__main__":
    main()
