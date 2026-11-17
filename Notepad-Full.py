"""
================================================================
פנקס רשימות - גרסה מלאה FULL
פותח ע"י יוסף שלום בן שטרית
CustomTkinter + RTL + סמל + כל הפיצ'רים מהמקורי
================================================================
התקנה:
    pip install customtkinter
הרצה:
    python notepad_full.py
בילד EXE:
    pyinstaller --onefile --noconsole --icon=notepad-icon.ico --name "Notepad" notepad_full.py
================================================================
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os, datetime, colorsys, sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_TITLE = 'פנקס רשימות פותח ע"י יוסף שלום בן שטרית'

class UltimateNotepadFull(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1000x650+400+150")
        # --- סמל ---
        try:
            _icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notepad-icon.ico")
            if os.path.exists(_icon):
                self.iconbitmap(_icon)
        except Exception:
            pass
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.97)

        # --- מצב ---
        self.file_path = None
        self.font_family = "Segoe UI"
        self.font_size = 15
        self.rtl_mode = True
        self.wrap_mode = True
        self.show_statusbar = True
        self.hue = 0
        self.find_last = ""

        # --- מסגרת RGB ---
        self.rgb_frame = ctk.CTkFrame(self, fg_color="#ff0000", corner_radius=12)
        self.rgb_frame.pack(fill="both", expand=True)
        self.main = ctk.CTkFrame(self.rgb_frame, fg_color="#1e1e1e", corner_radius=10)
        self.main.pack(fill="both", expand=True, padx=2, pady=2)

        # --- כותרת ---
        self.title_bar = ctk.CTkFrame(self.main, fg_color="#2d2d2d", height=40, corner_radius=8)
        self.title_bar.pack(fill="x", padx=4, pady=4)
        self.title_bar.pack_propagate(False)
        self.close_btn = ctk.CTkButton(self.title_bar, text="✕", width=34, height=30, fg_color="transparent", text_color="#ff5555", hover_color="#cc0000", font=("Arial", 12, "bold"), command=self.exit_app)
        self.min_btn = ctk.CTkButton(self.title_bar, text="―", width=34, height=30, fg_color="transparent", font=("Arial", 12, "bold"), command=self.minimize_app)
        self.rtl_btn = ctk.CTkButton(self.title_bar, text="⇄ RTL: ON  •  עברית", width=165, height=30, fg_color="#1f6aa5", hover_color="#2a8ad4", font=("Segoe UI", 11, "bold"), command=self.toggle_rtl)
        self.menu_btn = ctk.CTkButton(self.title_bar, text="☰", width=34, height=30, fg_color="transparent", font=("Arial", 12), command=self.show_menu)
        self.title_label = ctk.CTkLabel(self.title_bar, text=APP_TITLE, font=("Segoe UI", 12, "bold"), text_color="white")

        # --- סרגל כלים מלא ---
        self.toolbar = ctk.CTkFrame(self.main, fg_color="#2d2d2d", corner_radius=8)
        self.toolbar.pack(fill="x", padx=4, pady=(0,4))
        tools = [
            ("חדש", self.new_file), ("חלון חדש", self.new_window), ("פתח", self.open_file),
            ("שמור", self.save_file), ("שמור בשם", self.save_as), ("הדפס", self.print_file),
            ("בטל", self.undo), ("בצע שוב", self.redo),
            ("חפש", self.find_text), ("החלף", self.replace_text), ("שורה", self.go_to_line),
            ("בחר הכל", self.select_all), ("תאריך", self.insert_datetime),
            ("גופן", self.choose_font), ("+ זום", lambda: self.zoom(2)), ("- זום", lambda: self.zoom(-2)),
            ("גלישה", self.toggle_wrap), ("שורת מצב", self.toggle_statusbar), ("Bing", self.search_bing),
        ]
        for txt, cmd in tools:
            b = ctk.CTkButton(self.toolbar, text=txt, width=72, height=28, fg_color="#3a3a3a", hover_color="#264f78", font=("Segoe UI", 11), command=cmd)
            b.pack(side="right", padx=2, pady=4)

        # --- אזור כתיבה ---
        self.textbox = ctk.CTkTextbox(self.main, fg_color="#1e1e1e", text_color="#d4d4d4",
                                      font=(self.font_family, self.font_size), wrap="word",
                                      border_width=0, corner_radius=8, undo=True)
        self.textbox.pack(fill="both", expand=True, padx=6, pady=2)
        self._tk = self.textbox._textbox

        # --- שורת מצב + גריפ ---
        self.status = ctk.CTkLabel(self.main, text="Ln 1, Col 1  |  100%  •  RTL: ON  •  0 תווים", font=("Segoe UI", 11), text_color="gray", anchor="w")
        self.status.pack(fill="x", padx=8, pady=2)
        self.grip = ctk.CTkLabel(self.main, text="◢ גרור לשינוי גודל", font=("Arial", 10), text_color="gray", anchor="e")
        self.grip.pack(fill="x", padx=6, pady=(0,2))

        # --- אירועים ---
        self.title_bar.bind("<Button-1>", self.start_move); self.title_bar.bind("<B1-Motion>", self.do_move)
        self.title_label.bind("<Button-1>", self.start_move); self.title_label.bind("<B1-Motion>", self.do_move)
        self.grip.bind("<B1-Motion>", self.resize_window)
        self._tk.bind("<KeyRelease>", lambda e: self.update_status())
        self._tk.bind("<ButtonRelease-1>", lambda e: self.update_status())
        self._tk.bind("<Control-MouseWheel>", self.do_zoom)
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-S>", lambda e: self.save_as())
        self.bind("<Control-p>", lambda e: self.print_file())
        self.bind("<Control-f>", lambda e: self.find_text())
        self.bind("<Control-h>", lambda e: self.replace_text())
        self.bind("<Control-g>", lambda e: self.go_to_line())
        self.bind("<Control-a>", lambda e: self.select_all())
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-y>", lambda e: self.redo())
        self.bind("<F5>", lambda e: self.insert_datetime())
        self.bind("<Control-plus>", lambda e: self.zoom(2))
        self.bind("<Control-minus>", lambda e: self.zoom(-2))
        self.bind("<Control-0>", lambda e: self.reset_zoom())
        self.bind("<Control-Shift-R>", lambda e: self.toggle_rtl())

        self.apply_rtl()
        self.animate_rgb()
        self.update_status()

    # ================= RTL =================
    def apply_rtl(self):
        t = self._tk
        if self.rtl_mode:
            t.tag_configure("rtl", justify="right"); t.tag_add("rtl", "1.0", "end")
            self._layout_rtl(); self.rtl_btn.configure(text="⇄ RTL: ON  •  עברית", fg_color="#1f6aa5")
        else:
            t.tag_configure("rtl", justify="left"); t.tag_add("rtl", "1.0", "end")
            self._layout_ltr(); self.rtl_btn.configure(text="⇄ RTL: OFF  •  English", fg_color="#555555")
        self.update_status()
    def _layout_rtl(self):
        for w in [self.close_btn, self.min_btn, self.rtl_btn, self.menu_btn, self.title_label]: w.pack_forget()
        self.close_btn.pack(side="right", padx=2); self.min_btn.pack(side="right", padx=2)
        self.title_label.pack(side="right", padx=6, expand=True)
        self.rtl_btn.pack(side="left", padx=4); self.menu_btn.pack(side="left", padx=2)
    def _layout_ltr(self):
        for w in [self.close_btn, self.min_btn, self.rtl_btn, self.menu_btn, self.title_label]: w.pack_forget()
        self.close_btn.pack(side="left", padx=2); self.min_btn.pack(side="left", padx=2)
        self.title_label.pack(side="left", padx=6, expand=True)
        self.rtl_btn.pack(side="right", padx=4); self.menu_btn.pack(side="right", padx=2)
    def toggle_rtl(self):
        self.rtl_mode = not self.rtl_mode; self.apply_rtl()

    # ================= RGB =================
    def animate_rgb(self):
        rgb = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
        color = "#{:02x}{:02x}{:02x}".format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        self.rgb_frame.configure(fg_color=color)
        self.hue += 0.002
        if self.hue > 1: self.hue = 0
        self.after(10, self.animate_rgb)

    # ================= תפריט =================
    def show_menu(self):
        m = tk.Menu(self, tearoff=0)
        f = tk.Menu(m, tearoff=0); m.add_cascade(label="קובץ", menu=f)
        f.add_command(label="חדש  Ctrl+N", command=self.new_file)
        f.add_command(label="חלון חדש", command=self.new_window)
        f.add_command(label="פתח...  Ctrl+O", command=self.open_file)
        f.add_command(label="שמור  Ctrl+S", command=self.save_file)
        f.add_command(label="שמור בשם...  Ctrl+Shift+S", command=self.save_as)
        f.add_separator(); f.add_command(label="הדפס...  Ctrl+P", command=self.print_file)
        f.add_separator(); f.add_command(label="יציאה", command=self.exit_app)
        e = tk.Menu(m, tearoff=0); m.add_cascade(label="עריכה", menu=e)
        e.add_command(label="בטל  Ctrl+Z", command=self.undo)
        e.add_command(label="בצע שוב  Ctrl+Y", command=self.redo)
        e.add_command(label="חפש  Ctrl+F", command=self.find_text)
        e.add_command(label="החלף  Ctrl+H", command=self.replace_text)
        e.add_command(label="עבור לשורה  Ctrl+G", command=self.go_to_line)
        e.add_command(label="בחר הכל  Ctrl+A", command=self.select_all)
        e.add_command(label="תאריך  F5", command=self.insert_datetime)
        v = tk.Menu(m, tearoff=0); m.add_cascade(label="תצוגה", menu=v)
        v.add_command(label="RTL: הפעל/כבה  Ctrl+Shift+R", command=self.toggle_rtl)
        v.add_command(label="גלישת שורות", command=self.toggle_wrap)
        v.add_command(label="שורת מצב", command=self.toggle_statusbar)
        v.add_command(label="גופן...", command=self.choose_font)
        v.add_command(label="זום +", command=lambda: self.zoom(2))
        v.add_command(label="זום -", command=lambda: self.zoom(-2))
        v.add_command(label="איפוס זום  Ctrl+0", command=self.reset_zoom)
        m.add_command(label="חפש ב-Bing", command=self.search_bing)
        m.tk_popup(self.winfo_pointerx(), self.winfo_pointery())

    # ================= קובץ =================
    def new_file(self):
        if self.textbox.get("1.0", "end").strip() and not messagebox.askyesno("חדש", "למחוק את הטקסט הנוכחי?"):
            return
        self.textbox.delete("1.0", "end"); self.file_path = None
        self.title_label.configure(text=APP_TITLE); self.update_status()
    def new_window(self):
        try: os.system(f'start "" python "{os.path.abspath(__file__)}"')
        except: messagebox.showinfo("חלון חדש", "פתח את הקובץ שוב ידנית")
    def open_file(self):
        f = filedialog.askopenfilename(filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if f:
            self.file_path = f
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", open(f, encoding="utf-8", errors="ignore").read())
            self.title_label.configure(text=f"{os.path.basename(f)} - {APP_TITLE}")
            self.apply_rtl(); self.update_status()
    def save_file(self):
        if not self.file_path: return self.save_as()
        open(self.file_path, "w", encoding="utf-8").write(self.textbox.get("1.0", "end-1c"))
        messagebox.showinfo("נשמר", "נשמר בהצלחה ✓")
    def save_as(self):
        f = filedialog.asksaveasfilename(initialfile="Untitled.txt", defaultextension=".txt", filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if f: self.file_path = f; self.save_file(); self.title_label.configure(text=f"{os.path.basename(f)} - {APP_TITLE}")
    def print_file(self):
        if not self.file_path:
            messagebox.showwarning("הדפסה", "אנא שמור את הקובץ לפני ההדפסה"); return
        try: os.startfile(self.file_path, "print")
        except: messagebox.showerror("שגיאה", "שגיאה בשליחה למדפסת")

    # ================= עריכה =================
    def undo(self):
        try: self.textbox.edit_undo()
        except: pass
    def redo(self):
        try: self.textbox.edit_redo()
        except: pass
    def find_text(self):
        q = simpledialog.askstring("חיפוש", "חפש את:")
        if not q: return
        self.find_last = q
        idx = self.textbox.search(q, "insert", stopindex="end")
        if not idx: idx = self.textbox.search(q, "1.0", stopindex="end")
        if idx:
            end = f"{idx}+{len(q)}c"
            self.textbox.tag_add("sel", idx, end); self.textbox.mark_set("insert", end); self.textbox.see(end)
        else: messagebox.showinfo("תוצאה", f"'{q}' לא נמצא")
    def replace_text(self):
        q = simpledialog.askstring("החלפה", "חפש את:")
        if not q: return
        r = simpledialog.askstring("החלפה", "החלף ב:")
        if r is None: return
        txt = self.textbox.get("1.0", "end")
        self.textbox.delete("1.0", "end"); self.textbox.insert("1.0", txt.replace(q, r)); self.apply_rtl()
    def go_to_line(self):
        n = simpledialog.askinteger("עבור לשורה", "מספר שורה:")
        if n: self.textbox.mark_set("insert", f"{n}.0"); self.textbox.see(f"{n}.0")
    def select_all(self): self.textbox.tag_add("sel", "1.0", "end")
    def insert_datetime(self):
        now = datetime.datetime.now().strftime("%H:%M %d/%m/%Y")
        self.textbox.insert("insert", now)
    def search_bing(self):
        try:
            term = self.textbox.get("sel.first", "sel.last")
            os.system(f'start https://www.bing.com/search?q={term}')
        except: messagebox.showinfo("חיפוש", "אנא סמן טקסט לחיפוש")

    # ================= תצוגה =================
    def choose_font(self):
        win = ctk.CTkToplevel(self); win.title("גופן"); win.geometry("320x180"); win.attributes("-topmost", True)
        ctk.CTkLabel(win, text="גודל גופן:").pack(pady=8)
        slider = ctk.CTkSlider(win, from_=8, to=72, number_of_steps=64, command=lambda v: lbl.configure(text=f"גודל: {int(v)}"))
        slider.set(self.font_size); slider.pack(pady=8, padx=20, fill="x")
        lbl = ctk.CTkLabel(win, text=f"גודל: {self.font_size}"); lbl.pack()
        def apply():
            self.font_size = int(slider.get())
            self.textbox.configure(font=(self.font_family, self.font_size))
            win.destroy(); self.update_status()
        ctk.CTkButton(win, text="אישור", command=apply).pack(pady=10)
    def toggle_wrap(self):
        self.wrap_mode = not self.wrap_mode
        self.textbox.configure(wrap="word" if self.wrap_mode else "none")
    def toggle_statusbar(self):
        self.show_statusbar = not self.show_statusbar
        if self.show_statusbar: self.status.pack(fill="x", padx=8, pady=2)
        else: self.status.pack_forget()
    def zoom(self, d):
        self.font_size = max(6, self.font_size + d)
        self.textbox.configure(font=(self.font_family, self.font_size)); self.update_status()
    def reset_zoom(self):
        self.font_size = 15; self.textbox.configure(font=(self.font_family, self.font_size)); self.update_status()
    def do_zoom(self, e): self.zoom(2 if e.delta > 0 else -2)
    def update_status(self):
        try:
            row, col = self.textbox.index("insert").split(".")
            txt = self.textbox.get("1.0", "end-1c")
            words = len(txt.split()) if txt.strip() else 0
            rtl_txt = "RTL: ON" if self.rtl_mode else "RTL: OFF"
            self.status.configure(text=f"Ln {row}, Col {int(col)+1}  |  {int(self.font_size/15*100)}%  •  {rtl_txt}  •  {len(txt)} תווים • {words} מילים")
            self._tk.tag_add("rtl", "1.0", "end")
        except: pass

    # ================= חלון =================
    def start_move(self, e): self.x, self.y = e.x, e.y
    def do_move(self, e): self.geometry(f"+{self.winfo_x()+e.x-self.x}+{self.winfo_y()+e.y-self.y}")
    def resize_window(self, e):
        x1, y1 = self.winfo_pointerx(), self.winfo_pointery()
        w = max(300, x1 - self.winfo_rootx()); h = max(200, y1 - self.winfo_rooty())
        self.geometry(f"{w}x{h}")
    def minimize_app(self):
        self.overrideredirect(False); self.iconify()
        self.bind("<FocusIn>", lambda e: (self.overrideredirect(True), self.unbind("<FocusIn>")))
    def exit_app(self):
        if self.textbox.get("1.0", "end").strip():
            if not messagebox.askyesno("יציאה", "יש טקסט שלא נשמר. לצאת בכל זאת?"):
                return
        self.destroy()

if __name__ == "__main__":
    app = UltimateNotepadFull()
    app.mainloop()
