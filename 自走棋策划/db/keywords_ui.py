"""
Keywords 管理 UI
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from dao import KeywordDao


class KeywordManagerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Keyword 管理")
        self.root.geometry("700x500")
        self.dao = KeywordDao()
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(left, columns=("ID", "Name", "Type"), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='名称')
        self.tree.heading('Type', text='类型')
        self.tree.column('ID', width=120)
        self.tree.column('Name', width=200)
        self.tree.column('Type', width=120)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        right = ttk.Frame(main)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(right, text='新建', command=self.create_keyword).pack(fill=tk.X, pady=2)
        ttk.Button(right, text='编辑', command=self.edit_keyword).pack(fill=tk.X, pady=2)
        ttk.Button(right, text='删除', command=self.delete_keyword).pack(fill=tk.X, pady=2)
        ttk.Button(right, text='刷新', command=self.refresh_list).pack(fill=tk.X, pady=2)

        detail_frame = ttk.LabelFrame(main, text='详情')
        detail_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.detail = scrolledtext.ScrolledText(detail_frame, height=8)
        self.detail.pack(fill=tk.BOTH, expand=True)

    def refresh_list(self):
        for it in self.tree.get_children():
            self.tree.delete(it)
        rows = self.dao.read_all()
        for r in rows:
            self.tree.insert('', tk.END, values=(r.get('id'), r.get('name'), r.get('type') or ''))

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        kw_id = item['values'][0]
        kw = self.dao.read(kw_id)
        if kw:
            self.detail.delete(1.0, tk.END)
            self.detail.insert(1.0, json.dumps(kw, ensure_ascii=False, indent=2))

    def create_keyword(self):
        d = KeywordDialog(self.root, '新建 Keyword')
        if d.result:
            try:
                self.dao.create(d.result)
                self.refresh_list()
                messagebox.showinfo('成功', '创建成功')
            except Exception as e:
                messagebox.showerror('错误', str(e))

    def edit_keyword(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('警告', '请选择一项')
            return
        item = self.tree.item(sel[0])
        kw_id = item['values'][0]
        kw = self.dao.read(kw_id)
        if kw:
            d = KeywordDialog(self.root, '编辑 Keyword', kw)
            if d.result:
                try:
                    upd = d.result.copy()
                    if 'id' in upd:
                        del upd['id']
                    self.dao.update(kw_id, upd)
                    self.refresh_list()
                    messagebox.showinfo('成功', '更新成功')
                except Exception as e:
                    messagebox.showerror('错误', str(e))

    def delete_keyword(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('警告', '请选择一项')
            return
        item = self.tree.item(sel[0])
        kw_id = item['values'][0]
        if messagebox.askyesno('确认', f'确认删除 {kw_id}?'):
            try:
                self.dao.delete(kw_id)
                self.refresh_list()
                self.detail.delete(1.0, tk.END)
            except Exception as e:
                messagebox.showerror('错误', str(e))


class KeywordDialog:
    def __init__(self, parent, title, kw=None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        frame = ttk.Frame(self.dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text='ID:').grid(row=0, column=0, sticky=tk.W)
        self.id_entry = ttk.Entry(frame, width=50)
        self.id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='Name:').grid(row=1, column=0, sticky=tk.W)
        self.name_entry = ttk.Entry(frame, width=50)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='Description:').grid(row=2, column=0, sticky=tk.W)
        self.desc_entry = ttk.Entry(frame, width=50)
        self.desc_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='Type:').grid(row=3, column=0, sticky=tk.W)
        self.type_entry = ttk.Entry(frame, width=50)
        self.type_entry.grid(row=3, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='Trigger:').grid(row=4, column=0, sticky=tk.W)
        self.trigger_entry = ttk.Entry(frame, width=50)
        self.trigger_entry.grid(row=4, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='Condition (JSON dict):').grid(row=5, column=0, sticky=tk.W)
        self.cond_text = tk.Text(frame, height=4, width=50)
        self.cond_text.grid(row=5, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='Effects (JSON list):').grid(row=6, column=0, sticky=tk.W)
        self.effects_text = tk.Text(frame, height=4, width=50)
        self.effects_text.grid(row=6, column=1, sticky=(tk.W, tk.E))

        if kw:
            self.id_entry.insert(0, kw.get('id', ''))
            self.id_entry.config(state='readonly')
            self.name_entry.insert(0, kw.get('name', '') or '')
            self.desc_entry.insert(0, kw.get('description', '') or '')
            self.type_entry.insert(0, kw.get('type', '') or '')
            self.trigger_entry.insert(0, kw.get('trigger', '') or '')
            if kw.get('condition'):
                self.cond_text.insert(1.0, json.dumps(kw.get('condition'), ensure_ascii=False, indent=2))
            if kw.get('effects'):
                self.effects_text.insert(1.0, json.dumps(kw.get('effects'), ensure_ascii=False, indent=2))

        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text='确定', command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text='取消', command=self.on_cancel).pack(side=tk.RIGHT)

        self.dialog.wait_window()

    def on_ok(self):
        idv = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get().strip()
        typ = self.type_entry.get().strip()
        trigger = self.trigger_entry.get().strip()
        cond = self.cond_text.get(1.0, tk.END).strip()
        effects = self.effects_text.get(1.0, tk.END).strip()

        if not idv:
            messagebox.showerror('错误', 'ID 不能为空')
            return
        if not name:
            messagebox.showerror('错误', 'Name 不能为空')
            return
        try:
            cond_val = json.loads(cond) if cond else None
        except Exception:
            messagebox.showerror('错误', 'Condition 必须为 JSON 格式的字典')
            return
        try:
            effects_val = json.loads(effects) if effects else None
        except Exception:
            messagebox.showerror('错误', 'Effects 必须为 JSON 格式的列表')
            return
        data = {'id': idv, 'name': name}
        if desc:
            data['description'] = desc
        if typ:
            data['type'] = typ
        if trigger:
            data['trigger'] = trigger
        if cond_val is not None:
            data['condition'] = cond_val
        if effects_val is not None:
            data['effects'] = effects_val
        self.result = data
        self.dialog.destroy()

    def on_cancel(self):
        self.dialog.destroy()
