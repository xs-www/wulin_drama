"""
Event 管理 UI
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from dao import EventDao


class EventManagerUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Event 管理')
        self.root.geometry('700x500')
        self.dao = EventDao()
        self.create_widgets()
        # 初始化基础事件（如果表为空）
        try:
            self.dao.init_from_doc()
        except Exception:
            pass
        self.refresh_list()

    def create_widgets(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(left, columns=("ID", "Name"), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Name')
        self.tree.column('ID', width=200)
        self.tree.column('Name', width=300)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        right = ttk.Frame(main)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(right, text='新建', command=self.create_event).pack(fill=tk.X, pady=2)
        ttk.Button(right, text='编辑', command=self.edit_event).pack(fill=tk.X, pady=2)
        ttk.Button(right, text='删除', command=self.delete_event).pack(fill=tk.X, pady=2)
        ttk.Button(right, text='刷新', command=self.refresh_list).pack(fill=tk.X, pady=2)

        detail_frame = ttk.LabelFrame(main, text='详情')
        detail_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.detail = scrolledtext.ScrolledText(detail_frame, height=12)
        self.detail.pack(fill=tk.BOTH, expand=True)

    def refresh_list(self):
        for it in self.tree.get_children():
            self.tree.delete(it)
        rows = self.dao.read_all()
        for r in rows:
            self.tree.insert('', tk.END, values=(r.get('id'), r.get('name')))

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        eid = item['values'][0]
        ev = self.dao.read(eid)
        if ev:
            self.detail.delete(1.0, tk.END)
            self.detail.insert(1.0, json.dumps(ev, ensure_ascii=False, indent=2))

    def create_event(self):
        d = EventDialog(self.root, '新建 Event')
        if d.result:
            try:
                self.dao.create(d.result)
                self.refresh_list()
                messagebox.showinfo('成功', '创建成功')
            except Exception as e:
                messagebox.showerror('错误', str(e))

    def edit_event(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('警告', '请选择一项')
            return
        eid = self.tree.item(sel[0])['values'][0]
        ev = self.dao.read(eid)
        if ev:
            d = EventDialog(self.root, '编辑 Event', ev)
            if d.result:
                try:
                    upd = d.result.copy()
                    if 'id' in upd:
                        del upd['id']
                    self.dao.update(eid, upd)
                    self.refresh_list()
                    messagebox.showinfo('成功', '更新成功')
                except Exception as e:
                    messagebox.showerror('错误', str(e))

    def delete_event(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('警告', '请选择一项')
            return
        eid = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno('确认', f'确认删除 {eid}?'):
            try:
                self.dao.delete(eid)
                self.refresh_list()
                self.detail.delete(1.0, tk.END)
            except Exception as e:
                messagebox.showerror('错误', str(e))


class EventDialog:
    def __init__(self, parent, title, ev=None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        frame = ttk.Frame(self.dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text='ID:').grid(row=0, column=0, sticky=tk.W)
        self.id_entry = ttk.Entry(frame, width=60)
        self.id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='Name:').grid(row=1, column=0, sticky=tk.W)
        self.name_entry = ttk.Entry(frame, width=60)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='Context (JSON dict):').grid(row=2, column=0, sticky=tk.W)
        self.context_text = tk.Text(frame, height=10, width=60)
        self.context_text.grid(row=2, column=1, sticky=(tk.W, tk.E))

        if ev:
            self.id_entry.insert(0, ev.get('id', ''))
            self.id_entry.config(state='readonly')
            self.name_entry.insert(0, ev.get('name', '') or '')
            if ev.get('context'):
                self.context_text.insert(1.0, json.dumps(ev.get('context'), ensure_ascii=False, indent=2))

        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text='确定', command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text='取消', command=self.on_cancel).pack(side=tk.RIGHT)

        self.dialog.wait_window()

    def on_ok(self):
        idv = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        context = self.context_text.get(1.0, tk.END).strip()
        if not idv:
            messagebox.showerror('错误', 'ID 不能为空')
            return
        if not name:
            messagebox.showerror('错误', 'Name 不能为空')
            return
        try:
            ctx_val = json.loads(context) if context else None
        except Exception:
            messagebox.showerror('错误', 'Context 必须为 JSON 字典')
            return
        data = {'id': idv, 'name': name}
        if ctx_val is not None:
            data['context'] = ctx_val
        self.result = data
        self.dialog.destroy()

    def on_cancel(self):
        self.dialog.destroy()
