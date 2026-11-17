"""
פנקס רשימות - גרסת CustomTkinter + RTL אמיתי
פותח ע"י יוסף שלום בן שטרית

התקנה (פעם אחת בלבד):
    pip install customtkinter

הרצה:
    python notepad_ctk.py

בניית EXE:
    pip install pyinstaller
    pyinstaller --onefile --noconsole --name "Notepad" notepad_ctk.py

למה CustomTkinter?
- מראה מודרני, כהה, עגול - בלי שתצטרך לעצב ידנית
- RTL אמיתי דרך היפוך ה-Layout כולו + יישור טקסט, בלי python-bidi
- בלי python-bidi בכלל - רק customtkinter
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os, datetime, colorsys, sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class NotepadCTK(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("פנקס רשימות פותח ע\"י יוסף שלום בן שטרית")
        self.geometry("900x600+500+200")
        # --- סמל לאפליקציה ---
        try:
            # כשמריצים כ-Python - טוען את ה-ICO מהתיקייה
            # כשמריצים כ-EXE - PyInstaller כבר מטמיע אותו
            import os as _os
            _icon = _os.path.join(_os.path.dirname(__file__), "notepad-icon.ico")
            if _os.path.exists(_icon):
                self.iconbitmap(_icon)
        except Exception:
            pass  # אם אין סמל, ממשיכים בלי - לא קורס
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.97)

        self.file_path = None
        self.font_size = 15
        self.rtl_mode = True  # RTL מופעל כברירת מחדל
        self.wrap_mode = True
        self.hue = 0

        # --- מסגרת RGB ---
        self.rgb_frame = ctk.CTkFrame(self, fg_color="#ff0000", corner_radius=12)
        self.rgb_frame.pack(fill="both", expand=True)

        self.main = ctk.CTkFrame(self.rgb_frame, fg_color="#1e1e1e", corner_radius=10)
        self.main.pack(fill="both", expand=True, padx=2, pady=2)

        # --- כותרת ---
        self.title_bar = ctk.CTkFrame(self.main, fg_color="#2d2d2d", height=38, corner_radius=8)
        self.title_bar.pack(fill="x", padx=4, pady=4)
        self.title_bar.pack_propagate(False)

        self.close_btn = ctk.CTkButton(self.title_bar, text="✕", width=32, height=28, fg_color="transparent", text_color="#ff5555", hover_color="#cc0000", command=self.destroy)
        self.min_btn = ctk.CTkButton(self.title_bar, text="―", width=32, height=28, fg_color="transparent", command=self.minimize_app)
        # כפתור RTL - כפתור אחד בלבד!
        self.rtl_btn = ctk.CTkButton(self.title_bar, text="⇄ RTL: ON  •  עברית", width=150, height=28, fg_color="#1f6aa5", hover_color="#2a8ad4", command=self.toggle_rtl)
        self.menu_btn = ctk.CTkButton(self.title_bar, text="☰", width=32, height=28, fg_color="transparent", command=self.show_menu)

        self.title_label = ctk.CTkLabel(self.title_bar, text="פנקס רשימות פותח ע\"י יוסף שלום בן שטרית", font=("Segoe UI", 12, "bold"), text_color="white")

        # --- סרגל כלים ---
        self.toolbar = ctk.CTkFrame(self.main, fg_color="#2d2d2d", corner_radius=8)
        self.toolbar.pack(fill="x", padx=4, pady=(0,4))

        tools = [
            ("חדש", self.new_file), ("פתח", self.open_file), ("שמור", self.save_file),
            ("שמור בשם", self.save_as), ("הדפס", self.print_file),
            ("חפש", self.find_text), ("החלף", self.replace_text),
            ("שורה", self.go_to_line), ("בחר הכל", self.select_all),
            ("תאריך", self.insert_datetime), ("+ זום", lambda: self.zoom(2)),
            ("- זום", lambda: self.zoom(-2)), ("גלישה", self.toggle_wrap),
            ("Bing", self.search_bing),
        ]
        self.tool_btns = []
        for txt, cmd in tools:
            b = ctk.CTkButton(self.toolbar, text=txt, width=68, height=28, fg_color="#3a3a3a", hover_color="#264f78", command=cmd)
            b.pack(side="right", padx=2, pady=4)
            self.tool_btns.append(b)

        # --- אזור כתיבה ---
        # CTkTextbox עוטף Text של tkinter - אנחנו ניגשים אליו בשביל RTL
        self.textbox = ctk.CTkTextbox(self.main, fg_color="#1e1e1e", text_color="#d4d4d4",
                                      font=("Segoe UI", self.font_size), wrap="word",
                                      border_width=0, corner_radius=8)
        self.textbox.pack(fill="both", expand=True, padx=6, pady=2)
        self._tk_text = self.textbox._textbox  # ה-Text האמיתי של tkinter

        # --- שורת מצב ---
        self.status = ctk.CTkLabel(self.main, text="Ln 1, Col 1  |  100%  •  RTL: ON", font=("Segoe UI", 11), text_color="gray", anchor="w")
        self.status.pack(fill="x", padx=8, pady=2)

        # --- גרירה / שינוי גודל ---
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        self.title_label.bind("<Button-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)
        self._tk_text.bind("<KeyRelease>", lambda e: self.update_status())
        self._tk_text.bind("<ButtonRelease-1>", lambda e: self.update_status())
        self._tk_text.bind("<Control-MouseWheel>", self.do_zoom)

        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-p>", lambda e: self.print_file())
        self.bind("<Control-f>", lambda e: self.find_text())
        self.bind("<Control-h>", lambda e: self.replace_text())
        self.bind("<Control-g>", lambda e: self.go_to_line())
        self.bind("<Control-a>", lambda e: self.select_all())
        self.bind("<F5>", lambda e: self.insert_datetime())
        self.bind("<Control-Shift-R>", lambda e: self.toggle_rtl())  # Ctrl+Shift+R = RTL

        self.apply_rtl()  # מפעיל RTL בהתחלה
        self.animate_rgb()

    # ============ RTL - הלב של הגרסה הזו ============
    def apply_rtl(self):
        """RTL אמיתי: הופך את כל ה-Layout + יישור הטקסט, בלי python-bidi"""
        t = self._tk_text
        if self.rtl_mode:
            # 1. יישור טקסט לימין - זה מה ש-Windows עושה ב-RTL
            t.tag_configure("rtl", justify="right")
            t.tag_add("rtl", "1.0", "end")
            # 2. תגיות יישור לכל שורה חדשה
            t.configure(insertbackground="white")
            # 3. הופך את סדר הכפתורים: ב-RTL הכפתורים מימין לשמאל
            self._layout_rtl()
            self.rtl_btn.configure(text="⇄ RTL: ON  •  עברית", fg_color="#1f6aa5")
            self.status.configure(text=self.status.cget("text").replace("RTL: OFF", "RTL: ON"))
        else:
            t.tag_configure("rtl", justify="left")
            t.tag_add("rtl", "1.0", "end")
            self._layout_ltr()
            self.rtl_btn.configure(text="⇄ RTL: OFF  •  English", fg_color="#555555")
        self.update_status()

    def _layout_rtl(self):
        # ב-RTL: סגור בצד ימין (כמו ווינדוס בעברית), כותרת באמצע
        for w in [self.close_btn, self.min_btn, self.rtl_btn, self.menu_btn, self.title_label]:
            w.pack_forget()
        self.close_btn.pack(side="right", padx=2)
        self.min_btn.pack(side="right", padx=2)
        self.title_label.pack(side="right", padx=6, expand=True)
        self.rtl_btn.pack(side="left", padx=4)
        self.menu_btn.pack(side="left", padx=2)

    def _layout_ltr(self):
        for w in [self.close_btn, self.min_btn, self.rtl_btn, self.menu_btn, self.title_label]:
            w.pack_forget()
        self.close_btn.pack(side="left", padx=2)
        self.min_btn.pack(side="left", padx=2)
        self.title_label.pack(side="left", padx=6, expand=True)
        self.rtl_btn.pack(side="right", padx=4)
        self.menu_btn.pack(side="right", padx=2)

    def toggle_rtl(self):
        self.rtl_mode = not self.rtl_mode
        self.apply_rtl()

    # ============ שאר הפונקציות - כמו במקורי ============
    def animate_rgb(self):
        rgb = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
        color = "#{:02x}{:02x}{:02x}".format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        self.rgb_frame.configure(fg_color=color)
        self.hue += 0.002
        if self.hue > 1: self.hue = 0
        self.after(10, self.animate_rgb)

    def show_menu(self):
        m = tk.Menu(self, tearoff=0)
        m.add_command(label="חדש", command=self.new_file)
        m.add_command(label="פתח", command=self.open_file)
        m.add_command(label="שמור", command=self.save_file)
        m.add_separator()
        m.add_command(label="RTL: הפעל/כבה  (Ctrl+Shift+R)", command=self.toggle_rtl)
        m.add_separator()
        m.add_command(label="יציאה", command=self.destroy)
        m.tk_popup(self.winfo_pointerx(), self.winfo_pointery())

    def new_file(self):
        if self.textbox.get("1.0", "end").strip() and not messagebox.askyesno("חדש", "למחוק את הטקסט הנוכחי?"):
            return
        self.textbox.delete("1.0", "end"); self.file_path = None; self.update_status()

    def open_file(self):
        f = filedialog.askopenfilename(filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if f:
            self.file_path = f
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", open(f, encoding="utf-8", errors="ignore").read())
            self.apply_rtl(); self.update_status()

    def save_file(self):
        if not self.file_path: return self.save_as()
        open(self.file_path, "w", encoding="utf-8").write(self.textbox.get("1.0", "end-1c"))
        messagebox.showinfo("נשמר", "נשמר בהצלחה ✓")

    def save_as(self):
        f = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if f: self.file_path = f; self.save_file()

    def print_file(self):
        if not self.file_path:
            messagebox.showwarning("הדפסה", "שמור קודם את הקובץ"); return
        try: os.startfile(self.file_path, "print")
        except: messagebox.showerror("שגיאה", "שגיאה בהדפסה")

    def find_text(self):
        q = simpledialog.askstring("חיפוש", "חפש את:")
        if q:
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
        self.textbox.delete("1.0", "end"); self.textbox.insert("1.0", txt.replace(q, r))
        self.apply_rtl()

    def go_to_line(self):
        n = simpledialog.askinteger("עבור לשורה", "מספר שורה:")
        if n: self.textbox.mark_set("insert", f"{n}.0"); self.textbox.see(f"{n}.0")

    def select_all(self): self.textbox.tag_add("sel", "1.0", "end")
    def insert_datetime(self):
        now = datetime.datetime.now().strftime("%H:%M %d/%m/%Y")
        self.textbox.insert("insert", now)
    def zoom(self, d):
        self.font_size = max(8, self.font_size + d)
        self.textbox.configure(font=("Segoe UI", self.font_size)); self.update_status()
    def do_zoom(self, e): self.zoom(2 if e.delta > 0 else -2)
    def toggle_wrap(self):
        self.wrap_mode = not self.wrap_mode
        self.textbox.configure(wrap="word" if self.wrap_mode else "none")
    def search_bing(self):
        try:
            term = self.textbox.get("sel.first", "sel.last")
            os.system(f'start https://www.bing.com/search?q={term}')
        except: messagebox.showinfo("חיפוש", "סמן טקסט לחיפוש")
    def update_status(self):
        try:
            row, col = self.textbox.index("insert").split(".")
            rtl_txt = "RTL: ON" if self.rtl_mode else "RTL: OFF"
            self.status.configure(text=f"Ln {row}, Col {int(col)+1}  |  {int(self.font_size/12*100)}%  •  {rtl_txt}")
            # שומר יישור RTL גם לשורות חדשות
            self._tk_text.tag_add("rtl", "1.0", "end")
        except: pass
    def start_move(self, e): self.x, self.y = e.x, e.y
    def do_move(self, e):
        self.geometry(f"+{self.winfo_x()+e.x-self.x}+{self.winfo_y()+e.y-self.y}")
    def minimize_app(self):
        self.overrideredirect(False); self.iconify()
        self.bind("<FocusIn>", lambda e: (self.overrideredirect(True), self.unbind("<FocusIn>")))

if __name__ == "__main__":
    app = NotepadCTK()
    app.mainloop()
