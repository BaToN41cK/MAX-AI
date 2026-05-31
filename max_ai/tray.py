import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import pystray
from PIL import Image, ImageDraw, ImageFont
import sys
import os
import ctypes
from max_ai.core import AIAgent

ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


class TrayApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MAX-AI Agent")
        self.root.geometry("550x600")
        self.root.configure(bg="#1e1e2e")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        
        self.agent = None
        self.tray_icon = None
        self.tray_running = False
        
        self.setup_styles()
        self.setup_ui()
        self.create_tray_icon()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TFrame", background="#1e1e2e")
        style.configure("TLabel", background="#1e1e2e", foreground="#ffffff", font=("Segoe UI", 10))
        style.configure("TEntry", fieldbackground="#2d2d44", foreground="#ffffff", font=("Segoe UI", 11))
        style.map("TEntry", fieldbackground=[('focus', '#2d2d44')])
        style.configure("TButton", background="#4a4a6a", foreground="#ffffff", font=("Segoe UI", 10))
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header = ttk.Label(main_frame, text="MAX-AI Agent", font=("Segoe UI", 16, "bold"))
        header.pack(anchor=tk.CENTER, pady=(0, 10))
        
        ttk.Label(main_frame, text="Введите запрос:").pack(anchor=tk.W)
        
        self.entry = ttk.Entry(main_frame, font=("Segoe UI", 11))
        self.entry.pack(fill=tk.X, pady=(5, 10))
        self.entry.bind("<Return>", self.on_submit)
        self.entry.focus()
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="➤ Отправить", command=self.on_submit).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="⊡ Свернуть", command=self.hide_to_tray).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✕ Выход", command=self.quit_app).pack(side=tk.RIGHT)
        
        self.output = scrolledtext.ScrolledText(
            main_frame, wrap=tk.WORD, font=("Segoe UI", 10), 
            bg="#2d2d44", fg="#ffffff", insertbackground="#ffffff",
            relief=tk.FLAT, borderwidth=0
        )
        self.output.pack(fill=tk.BOTH, expand=True, pady=5)
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, "MAX-AI Agent готов к работе. Введите запрос...\n")
        self.output.config(state=tk.DISABLED)
        
    def on_submit(self, event=None):
        query = self.entry.get().strip()
        if not query:
            return
            
        self.entry.delete(0, tk.END)
        self.append_output(f"\n\n┌─ Вы ─────────────────────────────\n> {query}")
        self.root.config(cursor="watch")
        
        threading.Thread(target=self.process_query, args=(query,), daemon=True).start()
        
    def process_query(self, query):
        try:
            if self.agent is None:
                self.agent = AIAgent()
            response, tokens = self.agent.run(query)
            self.append_output(f"\n└─ Агент ({tokens} ток.) ─────────────────\n{response}")
        except Exception as e:
            self.append_output(f"\n└─ Ошибка ──────────────────────────\n> {str(e)}")
        finally:
            self.root.config(cursor="")
            
    def append_output(self, text):
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)
        
    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), color=(0, 120, 215))
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        draw.text((20, 20), "AI", font=font, fill=(255, 255, 255))
        
        menu = pystray.Menu(
            pystray.MenuItem('Показать', self.show_window),
            pystray.MenuItem('Выход', self.quit_app)
        )
        
        self.tray_icon = pystray.Icon("max_ai_tray", image, "MAX-AI Agent", menu)
        
    def hide_to_tray(self):
        self.root.withdraw()
        if not self.tray_running and self.tray_icon:
            self.tray_running = True
            threading.Thread(target=self.run_tray, daemon=True).start()
            
    def run_tray(self):
        self.tray_icon.run()
            
    def show_window(self, icon=None, item=None):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        if self.tray_icon:
            self.tray_icon.stop()
        self.tray_running = False
            
    def quit_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()
        sys.exit(0)
        
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = TrayApp()
    app.run()