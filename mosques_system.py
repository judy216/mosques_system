import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
import difflib
import webbrowser
import tempfile


# --- Database class ---
class MosqueDB:
    def __init__(self):
        self.con = sqlite3.connect("mosques.db")
        self.cur = self.con.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Mosques (
                ID          INTEGER PRIMARY KEY,
                name        TEXT NOT NULL,
                type        TEXT,
                address     TEXT,
                coordinates TEXT,
                imam_name   TEXT
            )
        """)
        self.con.commit()

        self.cur.execute("SELECT COUNT(*) FROM Mosques")
        if self.cur.fetchone()[0] == 0:
            rows = [
                (1, "Al-Masjid Al-Haram",  "Grand Mosque",    "Mecca, Saudi Arabia",
                 "21.4225,39.8262", "Sheikh Abdulrahman Al-Sudais"),
                (2, "Al-Masjid An-Nabawi", "Grand Mosque",    "Medina, Saudi Arabia",
                 "24.4672,39.6112", "Sheikh Ali Al-Hudhaify"),
                (3, "King Fahd Mosque",    "National Mosque", "Riyadh, Saudi Arabia",
                 "24.6877,46.7219", "Sheikh Saleh Al-Talib"),
                (4, "Al-Rajhi Mosque",     "Large Mosque",    "Riyadh, Saudi Arabia",
                 "24.7136,46.6753", "Sheikh Saud Al-Shuraim"),
                (5, "Quba Mosque",         "Historic Mosque", "Medina, Saudi Arabia",
                 "24.4399,39.6165", "Sheikh Ibrahim Al-Akhdar"),
            ]
            self.cur.executemany(
                "INSERT INTO Mosques VALUES (?,?,?,?,?,?)", rows)
            self.con.commit()

    def Display(self):
        self.cur.execute("SELECT * FROM Mosques")
        return self.cur.fetchall()

    def Search(self, name):
        self.cur.execute(
            "SELECT * FROM Mosques WHERE name LIKE ?", (f"%{name}%",))
        return self.cur.fetchall()

    def Insert(self, ID, name, tp, addr, coords, imam):
        try:
            self.cur.execute("INSERT INTO Mosques VALUES (?,?,?,?,?,?)",
                             (ID, name, tp, addr, coords, imam))
            self.con.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def Delete(self, ID):
        self.cur.execute("DELETE FROM Mosques WHERE ID=?", (ID,))
        self.con.commit()
        return self.cur.rowcount > 0

    def Update(self, ID, imam):
        self.cur.execute(
            "UPDATE Mosques SET imam_name=? WHERE ID=?", (imam, ID))
        self.con.commit()
        return self.cur.rowcount > 0

    def fuzzy_search(self, name):
        self.cur.execute("SELECT name FROM Mosques")
        all_names = [r[0] for r in self.cur.fetchall()]
        return difflib.get_close_matches(name, all_names, n=5, cutoff=0.4)

    def __del__(self):
        try:
            self.con.close()
        except:
            pass


class Mosque:
    def __init__(self, ID, name, tp, addr, coords, imam):
        self.ID = ID
        self.name = name
        self.type = tp
        self.addr = addr
        self.coords = coords
        self.imam = imam

    def __str__(self):
        return f"{self.ID} | {self.name} | {self.type} | {self.addr} | {self.coords} | {self.imam}"


class App(tk.Tk):

    BG = "#F5F0E8"
    WHITE = "#FFFFFF"
    GREEN = "#1A6B3A"
    GOLD = "#C9A84C"
    DARK = "#1C1C1C"
    GRAY = "#6B6B6B"
    BORDER = "#D8CFC0"
    RED = "#B33A3A"
    SELBG = "#D6EAE0"

    def __init__(self):
        super().__init__()
        self.db = MosqueDB()
        self.title("Mosques Management System")
        self.geometry("1050x700")
        self.minsize(900, 620)
        self.configure(bg=self.BG)
        self._fonts()
        self._build()
        self.cmd_display()

    def _fonts(self):
        self.ft = font.Font(family="Georgia",    size=17, weight="bold")
        self.fl = font.Font(family="Georgia",    size=10)
        self.fe = font.Font(family="Helvetica",  size=10)
        self.fb = font.Font(family="Helvetica",  size=9, weight="bold")
        self.fc = font.Font(family="Courier New", size=9)
        self.fs = font.Font(family="Helvetica",  size=8)
        self.fsc = font.Font(family="Georgia",    size=10, weight="bold")

    def _build(self):
        hdr = tk.Frame(self, bg=self.GREEN, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Mosques Management System",
                 bg=self.GREEN, fg="#FFFFFF", font=self.ft).pack()
        tk.Label(hdr, text="Manage mosque records with ease",
                 bg=self.GREEN, fg="#A8D5BC", font=self.fs).pack()

        body = tk.Frame(self, bg=self.BG)
        body.pack(fill="both", expand=True, padx=18, pady=14)

        left = tk.Frame(body, bg=self.BG, width=310)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        right = tk.Frame(body, bg=self.BG)
        right.pack(side="right", fill="both", expand=True, padx=(14, 0))

        self._form(left)
        self._buttons(left)
        self._list(right)

    def _form(self, p):
        card = tk.Frame(p, bg=self.WHITE,
                        highlightbackground=self.BORDER, highlightthickness=1)
        card.pack(fill="x", pady=(0, 10))

        tk.Label(card, text="Mosque Details", bg=self.WHITE,
                 fg=self.GREEN, font=self.fsc).grid(
            row=0, column=0, columnspan=2, pady=(10, 6), padx=12, sticky="w")
        tk.Frame(card, bg=self.GOLD, height=2).grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=12)

        fields = [("ID", "id"), ("Name", "name"), ("Type", "type"),
                  ("Address", "addr"), ("Coordinates", "coords"), ("Imam Name", "imam")]
        self.v = {}
        for i, (lbl, key) in enumerate(fields):
            r = i + 2
            tk.Label(card, text=lbl, bg=self.WHITE, fg=self.DARK,
                     font=self.fl, anchor="w").grid(
                row=r, column=0, sticky="w", padx=(12, 4), pady=4)
            if key == "type":
                var = tk.StringVar(value="Large Mosque")
                w = ttk.Combobox(card, textvariable=var, width=20,
                                 font=self.fe, state="readonly",
                                 values=["Grand Mosque", "National Mosque",
                                         "Large Mosque", "Historic Mosque",
                                         "Neighbourhood Mosque"])
            else:
                var = tk.StringVar()
                w = tk.Entry(card, textvariable=var, width=22,
                             font=self.fe, bg="#F9F7F3", relief="flat",
                             highlightbackground=self.BORDER, highlightthickness=1)
            w.grid(row=r, column=1, sticky="ew", padx=(0, 12), pady=4)
            self.v[key] = var
        card.columnconfigure(1, weight=1)
        tk.Frame(card, bg=self.BG, height=6).grid(
            row=len(fields)+2, column=0, columnspan=2)

    def _buttons(self, p):
        card = tk.Frame(p, bg=self.WHITE,
                        highlightbackground=self.BORDER, highlightthickness=1)
        card.pack(fill="x")

        tk.Label(card, text="Actions", bg=self.WHITE,
                 fg=self.GREEN, font=self.fsc).grid(
            row=0, column=0, columnspan=2, pady=(10, 4), padx=12, sticky="w")
        tk.Frame(card, bg=self.GOLD, height=2).grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=12)

        def btn(txt, cmd, col, r, c, cs=1):
            b = tk.Button(card, text=txt, command=cmd,
                          bg=col, fg="#FFFFFF", font=self.fb,
                          relief="flat", activebackground=col,
                          activeforeground="#FFFFFF", cursor="hand2",
                          padx=6, pady=6)
            b.grid(row=r, column=c, columnspan=cs,
                   sticky="ew", padx=6, pady=4)

        btn("Display All",    self.cmd_display,  self.GREEN,   2, 0)
        btn("Search",         self.cmd_search,   "#2E6B9E",    2, 1)
        btn("Add Entry",      self.cmd_add,      "#2E7D4F",    3, 0)
        btn("Delete Entry",   self.cmd_delete,   self.RED,     3, 1)
        btn("Update Imam",    self.cmd_update,   "#7B5EA7",    4, 0)
        btn("Display on Map", self.cmd_map,      self.GOLD,    4, 1)
        btn("Clear",          self.cmd_clear,    "#888888",    5, 0, 2)

        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)
        tk.Frame(card, bg=self.BG, height=6).grid(
            row=6, column=0, columnspan=2)

    def _list(self, p):
        top = tk.Frame(p, bg=self.BG)
        top.pack(fill="x", pady=(0, 6))
        tk.Label(top, text="Records", bg=self.BG,
                 fg=self.GREEN, font=self.fsc).pack(side="left")
        self.cnt = tk.Label(top, text="", bg=self.BG,
                            fg=self.GRAY, font=self.fs)
        self.cnt.pack(side="right")

        frm = tk.Frame(p, bg=self.BG)
        frm.pack(fill="both", expand=True)

        cols = ("ID", "Name", "Type", "Address", "Coordinates", "Imam Name")
        self.tree = ttk.Treeview(
            frm, columns=cols, show="headings", selectmode="browse")
        for col, w in zip(cols, [40, 180, 120, 180, 120, 160]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, minwidth=40)

        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Treeview", background="#FAFAF7", fieldbackground="#FAFAF7",
                    foreground=self.DARK, font=self.fc, rowheight=26)
        s.configure("Treeview.Heading", background=self.GREEN,
                    foreground="#FFFFFF", font=self.fb, relief="flat")
        s.map("Treeview",
              background=[("selected", self.SELBG)],
              foreground=[("selected", self.DARK)])

        vsb = ttk.Scrollbar(frm, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(frm, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frm.rowconfigure(0, weight=1)
        frm.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        self.stbar = tk.Label(p, text="Ready", bg=self.BG,
                              fg=self.GRAY, font=self.fs, anchor="w")
        self.stbar.pack(fill="x", pady=(6, 0))

    def _fill(self, rows):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in rows:
            self.tree.insert("", "end", values=r)
        n = len(rows)
        self.cnt.config(text=f"{n} record{'s' if n != 1 else ''}")

    def _status(self, msg, c=None):
        self.stbar.config(text=msg, fg=c or self.GRAY)

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        for k, val in zip(["id", "name", "type", "addr", "coords", "imam"], vals):
            self.v[k].set(val)

    def _get(self, k):
        return self.v[k].get().strip()

    def cmd_clear(self):
        for k in self.v:
            self.v[k].set("" if k != "type" else "Large Mosque")
        self._status("Fields cleared.")

    def cmd_display(self):
        rows = self.db.Display()
        self._fill(rows)
        self._status(f"Showing all {len(rows)} mosques.")

    def cmd_search(self):
        nm = self._get("name")
        if not nm:
            messagebox.showwarning("Search", "Please enter a name to search.")
            return
        rows = self.db.Search(nm)
        if rows:
            self._fill(rows)
            self._status(
                f"Found {len(rows)} result(s) for '{nm}'.", self.GREEN)
        else:
            suggestions = self.db.fuzzy_search(nm)
            if suggestions:
                pick = self._fuzzy_dialog(nm, suggestions)
                if pick:
                    rows = self.db.Search(pick)
                    self._fill(rows)
                    self._status(f"Showing results for '{pick}'.", self.GREEN)
            else:
                messagebox.showinfo(
                    "Not Found", f"No mosque found matching '{nm}'.")
                self._status("No results found.")

    def _fuzzy_dialog(self, orig, suggestions):
        dlg = tk.Toplevel(self)
        dlg.title("Did you mean?")
        dlg.configure(bg=self.BG)
        dlg.grab_set()
        dlg.resizable(False, False)

        tk.Label(dlg, text=f'No exact match for "{orig}".\nDid you mean:',
                 bg=self.BG, fg=self.DARK, font=self.fl,
                 justify="left").pack(padx=20, pady=(16, 8))

        picked = tk.StringVar(value="")
        for s in suggestions:
            tk.Radiobutton(dlg, text=s, variable=picked, value=s,
                           bg=self.BG, fg=self.DARK, font=self.fe,
                           activebackground=self.BG,
                           selectcolor=self.SELBG).pack(anchor="w", padx=28, pady=2)

        res = {"val": None}

        def ok():
            res["val"] = picked.get() or None
            dlg.destroy()

        def cancel():
            dlg.destroy()

        bf = tk.Frame(dlg, bg=self.BG)
        bf.pack(pady=12)
        tk.Button(bf, text="Search", command=ok,
                  bg=self.GREEN, fg="#FFFFFF", font=self.fb,
                  relief="flat", padx=10, pady=4).pack(side="left", padx=6)
        tk.Button(bf, text="Cancel", command=cancel,
                  bg="#888888", fg="#FFFFFF", font=self.fb,
                  relief="flat", padx=10, pady=4).pack(side="left", padx=6)

        self.wait_window(dlg)
        return res["val"]

    def cmd_add(self):
        id_ = self._get("id")
        nm = self._get("name")
        tp = self._get("type")
        addr = self._get("addr")
        crd = self._get("coords")
        imam = self._get("imam")

        if not id_ or not nm:
            messagebox.showwarning("Add Entry", "ID and Name are required.")
            return
        if not id_.isdigit():
            messagebox.showwarning("Add Entry", "ID must be a number.")
            return

        m = Mosque(int(id_), nm, tp, addr, crd, imam)
        ok = self.db.Insert(m.ID, m.name, m.type, m.addr, m.coords, m.imam)
        if ok:
            self.cmd_display()
            self._status(f"'{nm}' added successfully.", self.GREEN)
            self.cmd_clear()
        else:
            messagebox.showerror("Duplicate ID", f"ID {id_} already exists.")

    def cmd_delete(self):
        id_ = self._get("id")
        if not id_:
            messagebox.showwarning(
                "Delete", "Please select or enter a mosque ID.")
            return
        if not id_.isdigit():
            messagebox.showwarning("Delete", "ID must be a number.")
            return
        if not messagebox.askyesno("Confirm", f"Delete mosque ID {id_}?"):
            return
        ok = self.db.Delete(int(id_))
        if ok:
            self.cmd_display()
            self._status(f"Mosque ID {id_} deleted.", self.RED)
            self.cmd_clear()
        else:
            messagebox.showerror("Not Found", f"No mosque with ID {id_}.")

    def cmd_update(self):
        id_ = self._get("id")
        imam = self._get("imam")
        if not id_:
            messagebox.showwarning("Update", "Please select a mosque first.")
            return
        if not imam:
            messagebox.showwarning("Update", "Please enter the new Imam name.")
            return
        ok = self.db.Update(int(id_), imam)
        if ok:
            self.cmd_display()
            self._status(f"Imam updated for mosque ID {id_}.", "#7B5EA7")
        else:
            messagebox.showerror("Not Found", f"No mosque with ID {id_}.")

    def cmd_map(self):
        crd = self._get("coords")
        nm = self._get("name")
        if not crd:
            messagebox.showwarning(
                "Map", "Please select a mosque with coordinates.")
            return
        try:
            lat, lon = [x.strip() for x in crd.split(",")]
            float(lat)
            float(lon)
        except ValueError:
            messagebox.showerror(
                "Map Error", "Coordinates format: lat,lon  e.g. 21.4225,39.8262")
            return

        try:
            import folium
            mp = folium.Map(location=[float(lat), float(lon)], zoom_start=15)
            folium.Marker([float(lat), float(lon)],
                          popup=nm or "Mosque", tooltip=nm or "Mosque",
                          icon=folium.Icon(color="green", icon="star")).add_to(mp)
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html",
                                              mode="w", encoding="utf-8")
            mp.save(tmp.name)
            tmp.close()
            webbrowser.open(f"file://{tmp.name}")
        except ImportError:
            webbrowser.open(f"https://maps.google.com/?q={lat},{lon}")
        self._status(f"Map opened for {nm or 'mosque'}.", self.GOLD)


if __name__ == "__main__":
    app = App()
    app.mainloop()
