import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, font
import os
import datetime
import colorsys
import sys

class UltimateNotepad:
    def __init__(self, root):
        self.root = root
        self.root_title = "פנקס רשימות פותח ע\"י יוסף שלום בן שטרית"
        self.root.title(self.root_title)
        self.root.geometry("300x150+500+300")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.97)

        self.bg_color = "#1e1e1e"
        self.fg_color = "#d4d4d4"
        self.menu_bg = "#2d2d2d"
        self.select_bg = "#264f78"
        self.hue = 0
        self.font_family = "Segoe UI"
        self.font_size = 11
        self.file_path = None
        self.show_statusbar = False 
        self.word_wrap = False

        self.rgb_frame = tk.Frame(root, bg="#ff0000")
        self.rgb_frame.pack(fill=tk.BOTH, expand=True)

        self.inner_frame = tk.Frame(self.rgb_frame, bg=self.bg_color)
        self.inner_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.title_bar = tk.Frame(self.inner_frame, bg=self.menu_bg, height=25)
        self.title_bar.pack(fill=tk.X, side=tk.TOP)
        self.title_bar.pack_propagate(False)

        self.close_btn = tk.Button(self.title_bar, text="✕", bg=self.menu_bg, fg="#ff5555",
                                   bd=0, font=("Arial", 10, "bold"), activebackground="#cc0000",
                                   activeforeground="white", cursor="hand2", command=self.exit_app)
        self.close_btn.pack(side=tk.LEFT, padx=2, ipadx=5, fill=tk.Y)

        self.min_btn = tk.Button(self.title_bar, text="―", bg=self.menu_bg, fg=self.fg_color,
                                 bd=0, font=("Arial", 10, "bold"), activebackground=self.select_bg,
                                 activeforeground="white", cursor="hand2", command=self.minimize_app)
        self.min_btn.pack(side=tk.LEFT, padx=0, ipadx=5, fill=tk.Y)

        self.icon_btn = tk.Button(self.title_bar, text="☰", bg=self.menu_bg, fg=self.fg_color,
                                  bd=0, font=("Arial", 10), activebackground=self.select_bg,
                                  activeforeground="white", cursor="hand2", command=self.show_menu)
        self.icon_btn.pack(side=tk.RIGHT, padx=5, pady=2)

        self.title_label = tk.Label(self.title_bar, text=self.root_title, bg=self.menu_bg, 
                                    fg="white", font=("Segoe UI", 9, "bold"))
        self.title_label.pack(side=tk.RIGHT, padx=5)

        self.text_area = tk.Text(self.inner_frame, bg=self.bg_color, fg=self.fg_color,
                                 font=(self.font_family, self.font_size), bd=0, undo=True,
                                 insertbackground="white", selectbackground=self.select_bg)
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=5, pady=0)
        self.text_area.tag_configure("dir", justify='right')

        self.status_bar = tk.Label(self.inner_frame, text="", bg=self.menu_bg, fg="gray", font=("Segoe UI", 7), anchor="w")
        
        self.grip = tk.Label(self.inner_frame, text="◢", bg=self.bg_color, fg="gray", font=("Arial", 8), cursor="sizing")
        self.grip.place(relx=1.0, rely=1.0, x=0, y=0, anchor="se")

        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        self.title_label.bind("<Button-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)
        self.grip.bind("<B1-Motion>", self.resize_window)
        self.text_area.bind('<KeyRelease>', self.update_status)
        self.text_area.bind('<ButtonRelease-1>', self.update_status)
        self.text_area.bind('<Control-MouseWheel>', self.do_zoom)
        
        self.bind_shortcuts()
        self.animate_rgb()

    def bind_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-S>', lambda e: self.save_as_file())
        self.root.bind('<Control-p>', lambda e: self.print_file())
        self.root.bind('<Control-f>', lambda e: self.find_text())
        self.root.bind('<Control-h>', lambda e: self.replace_text())
        self.root.bind('<Control-g>', lambda e: self.go_to_line())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<F5>', lambda e: self.insert_datetime())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.reset_zoom())

    def animate_rgb(self):
        rgb = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
        color = "#{:02x}{:02x}{:02x}".format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        self.rgb_frame.config(bg=color)
        self.grip.config(fg=color)
        self.hue += 0.002
        if self.hue > 1: self.hue = 0
        self.root.after(10, self.animate_rgb)

    def show_menu(self):
        menu = tk.Menu(self.root, tearoff=0, bg=self.menu_bg, fg=self.fg_color, 
                       activebackground=self.select_bg, activeforeground="white", bd=1)
        
        file_menu = tk.Menu(menu, tearoff=0, bg=self.menu_bg, fg=self.fg_color, activebackground=self.select_bg)
        menu.add_cascade(label="קובץ", menu=file_menu)
        file_menu.add_command(label="חדש", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="חלון חדש", accelerator="Ctrl+Shift+N", command=lambda: os.system(f'python "{sys.argv[0]}"'))
        file_menu.add_command(label="פתח...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="שמור", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="שמור בשם...", accelerator="Ctrl+Shift+S", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="הדפס...", accelerator="Ctrl+P", command=self.print_file)
        file_menu.add_separator()
        file_menu.add_command(label="יציאה", command=self.exit_app)

        edit_menu = tk.Menu(menu, tearoff=0, bg=self.menu_bg, fg=self.fg_color, activebackground=self.select_bg)
        menu.add_cascade(label="עריכה", menu=edit_menu)
        edit_menu.add_command(label="בטל", accelerator="Ctrl+Z", command=self.text_area.edit_undo)
        edit_menu.add_command(label="בצע שוב", accelerator="Ctrl+Y", command=self.text_area.edit_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="גזור", accelerator="Ctrl+X", command=lambda: self.text_area.event_generate("<<Cut>>"))
        edit_menu.add_command(label="העתק", accelerator="Ctrl+C", command=lambda: self.text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="הדבק", accelerator="Ctrl+V", command=lambda: self.text_area.event_generate("<<Paste>>"))
        edit_menu.add_command(label="מחק", accelerator="Del", command=lambda: self.text_area.event_generate("<Delete>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="חיפוש באינטרנט...", accelerator="Ctrl+E", command=self.search_bing)
        edit_menu.add_command(label="חיפוש...", accelerator="Ctrl+F", command=self.find_text)
        edit_menu.add_command(label="החלפה...", accelerator="Ctrl+H", command=self.replace_text)
        edit_menu.add_command(label="עבור אל...", accelerator="Ctrl+G", command=self.go_to_line)
        edit_menu.add_separator()
        edit_menu.add_command(label="בחר הכל", accelerator="Ctrl+A", command=self.select_all)
        edit_menu.add_command(label="שעה/תאריך", accelerator="F5", command=self.insert_datetime)

        format_menu = tk.Menu(menu, tearoff=0, bg=self.menu_bg, fg=self.fg_color, activebackground=self.select_bg)
        menu.add_cascade(label="עיצוב", menu=format_menu)
        format_menu.add_checkbutton(label="גלישת שורות", command=self.toggle_word_wrap)
        format_menu.add_command(label="גופן...", command=self.choose_font)

        view_menu = tk.Menu(menu, tearoff=0, bg=self.menu_bg, fg=self.fg_color, activebackground=self.select_bg)
        menu.add_cascade(label="תצוגה", menu=view_menu)
        view_menu.add_command(label="התקרב", accelerator="Ctrl+Plus", command=self.zoom_in)
        view_menu.add_command(label="התרחק", accelerator="Ctrl+Minus", command=self.zoom_out)
        view_menu.add_command(label="שחזר ברירת מחדל", accelerator="Ctrl+0", command=self.reset_zoom)
        view_menu.add_checkbutton(label="שורת מצב", command=self.toggle_statusbar)

        help_menu = tk.Menu(menu, tearoff=0, bg=self.menu_bg, fg=self.fg_color, activebackground=self.select_bg)
        menu.add_cascade(label="עזרה", menu=help_menu)
        help_menu.add_command(label="אודות", command=lambda: messagebox.showinfo("אודות", f"{self.root_title}"))

        x = self.icon_btn.winfo_rootx()
        y = self.icon_btn.winfo_rooty() + self.icon_btn.winfo_height()
        menu.tk_popup(x, y)

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.file_path = None
        self.title_label.config(text=self.root_title)

    def open_file(self):
        file = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if file:
            self.file_path = file
            self.title_label.config(text=f"{os.path.basename(file)} - {self.root_title}")
            self.text_area.delete(1.0, tk.END)
            try:
                with open(file, "r", encoding="utf-8") as f:
                    self.text_area.insert(1.0, f.read())
            except:
                with open(file, "r") as f:
                    self.text_area.insert(1.0, f.read())

    def save_file(self):
        if self.file_path:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(self.text_area.get(1.0, tk.END))
        else:
            self.save_as_file()

    def save_as_file(self):
        file = filedialog.asksaveasfilename(initialfile="Untitled.txt", defaultextension=".txt", filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if file:
            self.file_path = file
            self.save_file()
            self.title_label.config(text=f"{os.path.basename(file)} - {self.root_title}")

    def print_file(self):
        if not self.file_path:
            messagebox.showwarning("הדפסה", "אנא שמור את הקובץ לפני ההדפסה")
            return
        try:
            os.startfile(self.file_path, "print")
        except:
            messagebox.showerror("שגיאה", "שגיאה בשליחה למדפסת")

    def find_text(self):
        self.search_dialog(replace=False)

    def replace_text(self):
        self.search_dialog(replace=True)

    def search_dialog(self, replace=False):
        dialog = tk.Toplevel(self.root)
        dialog.title("החלפה" if replace else "חיפוש")
        dialog.geometry("350x160")
        dialog.attributes('-topmost', True)
        dialog.resizable(False, False)
        tk.Label(dialog, text="חפש את:").grid(row=0, column=0, padx=10, pady=10)
        find_entry = tk.Entry(dialog, width=30)
        find_entry.grid(row=0, column=1, padx=10, pady=10)
        find_entry.focus_set()

        if replace:
            tk.Label(dialog, text="החלף ב:").grid(row=1, column=0, padx=10, pady=10)
            replace_entry = tk.Entry(dialog, width=30)
            replace_entry.grid(row=1, column=1, padx=10, pady=10)

        def execute():
            target = find_entry.get()
            if not target: return
            content = self.text_area.get(1.0, tk.END)
            if replace:
                replacement = replace_entry.get()
                new_content = content.replace(target, replacement)
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, new_content)
            else:
                start = self.text_area.search(target, tk.INSERT, stopindex=tk.END)
                if not start:
                    start = self.text_area.search(target, "1.0", stopindex=tk.END)
                if start:
                    end = f"{start}+{len(target)}c"
                    self.text_area.tag_remove("sel", "1.0", tk.END)
                    self.text_area.tag_add("sel", start, end)
                    self.text_area.mark_set("insert", end)
                    self.text_area.see(end)
                else:
                    messagebox.showinfo("תוצאה", f"'{target}' לא נמצא")

        btn_text = "החלף הכל" if replace else "חפש הבא"
        tk.Button(dialog, text=btn_text, command=execute).grid(row=2, column=0, columnspan=2, pady=10)

    def search_bing(self):
        try:
            term = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            os.system(f"start https://www.bing.com/search?q={term}")
        except:
            messagebox.showinfo("חיפוש", "אנא סמן טקסט לחיפוש")

    def go_to_line(self):
        line = simpledialog.askinteger("עבור לשורה", "מספר שורה:")
        if line:
            self.text_area.mark_set("insert", f"{line}.0")
            self.text_area.see(f"{line}.0")

    def select_all(self):
        self.text_area.tag_add("sel", "1.0", "end")

    def insert_datetime(self):
        now = datetime.datetime.now().strftime("%H:%M %d/%m/%Y")
        self.text_area.insert(tk.INSERT, now)

    def choose_font(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("גופן")
        dialog.geometry("300x100")
        dialog.attributes('-topmost', True)
        tk.Label(dialog, text="גודל גופן:").pack(pady=5)
        size_var = tk.IntVar(value=self.font_size)
        spin = tk.Spinbox(dialog, from_=8, to=72, textvariable=size_var)
        spin.pack(pady=5)
        def apply():
            self.font_size = int(spin.get())
            self.text_area.config(font=(self.font_family, self.font_size))
            dialog.destroy()
        tk.Button(dialog, text="אישור", command=apply).pack(pady=5)

    def toggle_word_wrap(self):
        self.word_wrap = not self.word_wrap
        self.text_area.config(wrap="word" if self.word_wrap else "none")

    def zoom_in(self):
        self.font_size += 2
        self.text_area.config(font=(self.font_family, self.font_size))
        self.update_status()

    def zoom_out(self):
        self.font_size = max(6, self.font_size - 2)
        self.text_area.config(font=(self.font_family, self.font_size))
        self.update_status()

    def reset_zoom(self):
        self.font_size = 12
        self.text_area.config(font=(self.font_family, self.font_size))
        self.update_status()

    def do_zoom(self, event):
        if event.delta > 0: self.zoom_in()
        else: self.zoom_out()

    def toggle_statusbar(self):
        if self.show_statusbar:
            self.status_bar.pack_forget()
            self.show_statusbar = False
        else:
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            self.show_statusbar = True

    def update_status(self, event=None):
        try:
            row, col = self.text_area.index(tk.INSERT).split('.')
            zoom_pct = int((self.font_size / 12) * 100)
            self.status_bar.config(text=f"   Ln {row}, Col {int(col)+1}  |  {zoom_pct}%")
        except: pass

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def resize_window(self, event):
        x1 = self.root.winfo_pointerx()
        y1 = self.root.winfo_pointery()
        x0 = self.root.winfo_rootx()
        y0 = self.root.winfo_rooty()
        new_w = max(220, x1-x0)
        new_h = max(80, y1-y0)
        self.root.geometry(f"{new_w}x{new_h}")

    def minimize_app(self):
        self.root.overrideredirect(False)
        self.root.iconify()
        self.root.bind("<FocusIn>", self.restore_frame)

    def restore_frame(self, event):
        self.root.overrideredirect(True)
        self.root.unbind("<FocusIn>")

    def exit_app(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateNotepad(root)
    root.mainloop()