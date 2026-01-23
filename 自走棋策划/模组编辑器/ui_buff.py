#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Buff 管理 UI
参考 data/defalut_buff.json
功能：列出所有 buff，创建/删除/刷新，编辑 id/name/description/duration/max_stacks，以及 effects（使用效果编辑器）
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json, sys, os
from pathlib import Path

# 添加项目上层目录到路径，确保能导入 mod_controller
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mod_controller import BuffController

try:
    from ui_effect import show_effect_editor
except Exception:
    def show_effect_editor(*a, **k):
        return None


class BuffManagerUI:
    def __init__(self, root, modid):
        self.root = root
        self.root.title('Buff 管理')
        self.root.geometry('900x640')
        self.modid = modid
        self.control = BuffController(modid)
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 左：列表
        list_frame = ttk.LabelFrame(main_frame, text='Buff 列表', padding=6)
        list_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0,6))
        self.tree = ttk.Treeview(list_frame, columns=('ID','Name'), show='headings', height=30)
        self.tree.heading('ID', text='Buff ID')
        self.tree.heading('Name', text='名称')
        self.tree.column('ID', width=200)
        self.tree.column('Name', width=250)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        sb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=sb.set)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # 右上：按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N))
        ttk.Button(btn_frame, text='创建 Buff', command=self.create_buff).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text='删除 Buff', command=self.delete_buff).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text='保存', command=self.save_current_buff).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text='刷新', command=self.refresh_list).pack(side=tk.LEFT, padx=4)

        # 右下：详情
        detail_frame = ttk.LabelFrame(main_frame, text='Buff 详情', padding=6)
        detail_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        detail_frame.columnconfigure(1, weight=1)
        detail_frame.rowconfigure(6, weight=1)

        ttk.Label(detail_frame, text='ID:').grid(row=0, column=0, sticky=tk.W)
        self.id_var = tk.StringVar()
        self.id_entry = ttk.Entry(detail_frame, textvariable=self.id_var)
        self.id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Label(detail_frame, text='名称:').grid(row=1, column=0, sticky=tk.W)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(detail_frame, textvariable=self.name_var)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

        ttk.Label(detail_frame, text='描述:').grid(row=2, column=0, sticky=tk.NW)
        self.desc_text = tk.Text(detail_frame, height=4, wrap=tk.WORD)
        self.desc_text.grid(row=2, column=1, sticky=(tk.W, tk.E))

        ttk.Label(detail_frame, text='持续回合 (duration):').grid(row=3, column=0, sticky=tk.W)
        self.duration_var = tk.StringVar()
        self.duration_entry = ttk.Entry(detail_frame, textvariable=self.duration_var)
        self.duration_entry.grid(row=3, column=1, sticky=(tk.W, tk.E))

        ttk.Label(detail_frame, text='最大叠加 (max_stacks):').grid(row=4, column=0, sticky=tk.W)
        self.stacks_var = tk.StringVar()
        self.stacks_entry = ttk.Entry(detail_frame, textvariable=self.stacks_var)
        self.stacks_entry.grid(row=4, column=1, sticky=(tk.W, tk.E))

        # effects 列表
        eff_frame = ttk.LabelFrame(detail_frame, text='Effects', padding=4)
        eff_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(8,0))
        eff_frame.columnconfigure(0, weight=1)

        self.eff_listbox = tk.Listbox(eff_frame, height=10)
        self.eff_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        eff_sb = ttk.Scrollbar(eff_frame, orient=tk.VERTICAL, command=self.eff_listbox.yview)
        eff_sb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.eff_listbox.config(yscrollcommand=eff_sb.set)

        eff_btnf = ttk.Frame(eff_frame)
        eff_btnf.grid(row=0, column=2, sticky=(tk.N, tk.S), padx=6)
        ttk.Button(eff_btnf, text='添加效果', command=self.add_effect).pack(fill=tk.X, pady=2)
        ttk.Button(eff_btnf, text='编辑效果', command=self.edit_effect).pack(fill=tk.X, pady=2)
        ttk.Button(eff_btnf, text='删除效果', command=self.remove_effect).pack(fill=tk.X, pady=2)

        # filler
        ttk.Label(detail_frame, text='（保存会将 name/description 同步到语言文件）').grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(6,0))

    def refresh_list(self):
        for it in self.tree.get_children():
            self.tree.delete(it)
        try:
            buffs = self.control.get_all_buffs() or []
        except Exception:
            buffs = []
        for b in buffs:
            bid = b.get('id') or ''
            name = b.get('name') or bid
            self.tree.insert('', tk.END, values=(bid, name))

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        bid = item['values'][0]
        try:
            buff = self.control.get_buff_by_id(bid)
        except Exception as e:
            messagebox.showerror('错误', f'无法获取 buff：{e}')
            return
        if not buff:
            return
        self.populate_detail(buff)

    def populate_detail(self, buff):
        # buff may have id like modid:buff/id or simple id
        self.current_buff = buff.copy()
        bid = buff.get('id')
        self.id_var.set(str(bid))
        # name/description may be strings or dicts; show raw text or json
        name = buff.get('name') or ''
        self.name_var.set(str(name))
        desc = buff.get('description') or buff.get('decription') or ''
        self.desc_text.delete(1.0, tk.END)
        try:
            if isinstance(desc, (dict, list)):
                self.desc_text.insert(1.0, json.dumps(desc, ensure_ascii=False, indent=2))
            else:
                self.desc_text.insert(1.0, str(desc))
        except Exception:
            self.desc_text.insert(1.0, str(desc))
        self.duration_var.set(str(buff.get('duration') if buff.get('duration') is not None else ''))
        self.stacks_var.set(str(buff.get('max_stacks') if buff.get('max_stacks') is not None else ''))

        self.eff_listbox.delete(0, tk.END)
        effs = buff.get('effects') or []
        if not isinstance(effs, list):
            try:
                effs = list(effs)
            except Exception:
                effs = [effs]
        for e in effs:
            try:
                label = json.dumps(e, ensure_ascii=False)
            except Exception:
                label = str(e)
            self.eff_listbox.insert(tk.END, label)
        # store effects in current_buff normalized
        self.current_buff['effects'] = effs

    def create_buff(self):
        d = SimpleBuffDialog(self.root, '新建 Buff')
        if not d.result:
            return
        rec = d.result
        # ensure fields
        rec.setdefault('effects', [])
        rec.setdefault('duration', 0)
        rec.setdefault('max_stacks', 1)
        try:
            ok = self.control.create_buff(rec)
        except Exception as e:
            messagebox.showerror('错误', f'创建失败：{e}')
            return
        if ok:
            messagebox.showinfo('成功', '创建成功')
            self.refresh_list()
        else:
            messagebox.showerror('失败', '创建失败或未实现')

    def delete_buff(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('警告', '请先选择一个 Buff')
            return
        item = self.tree.item(sel[0])
        bid = item['values'][0]
        if not messagebox.askyesno('确认', f'确定删除 Buff {bid} ?'):
            return
        try:
            ok = self.control.delete_buff(bid)
        except Exception as e:
            messagebox.showerror('错误', f'删除失败：{e}')
            return
        if ok:
            messagebox.showinfo('成功', '删除成功')
            self.refresh_list()
        else:
            messagebox.showerror('失败', '删除失败或未实现')

    def save_current_buff(self):
        if not getattr(self, 'current_buff', None):
            messagebox.showwarning('警告', '没有可保存的 Buff')
            return False
        b = self.current_buff
        # update from UI
        bid = self.id_var.get().strip()
        if not bid:
            messagebox.showerror('错误', 'ID 不能为空')
            return False
        # If id contains modid prefix, allow it; service will normalize
        b['id'] = bid
        b['name'] = self.name_var.get().strip()
        desc_raw = self.desc_text.get(1.0, tk.END).strip()
        try:
            desc_val = json.loads(desc_raw)
        except Exception:
            desc_val = desc_raw
        b['description'] = desc_val
        # numeric fields
        try:
            b['duration'] = int(self.duration_var.get().strip()) if self.duration_var.get().strip()!='' else None
        except Exception:
            messagebox.showerror('错误', 'duration 必须为整数')
            return False
        try:
            b['max_stacks'] = int(self.stacks_var.get().strip()) if self.stacks_var.get().strip()!='' else None
        except Exception:
            messagebox.showerror('错误', 'max_stacks 必须为整数')
            return False
        # effects already in list
        effs = self.current_buff.get('effects') or []
        b['effects'] = effs

        try:
            ok = self.control.update_buff(b)
        except Exception as e:
            messagebox.showerror('错误', f'保存失败：{e}')
            return False
        if ok:
            messagebox.showinfo('成功', '保存成功')
            self.refresh_list()
            return True
        else:
            messagebox.showerror('失败', '保存失败或未实现')
            return False

    def add_effect(self):
        # 使用 effect 编辑器创建新效果
        eff = show_effect_editor(self.root, None, self.modid)
        if not eff:
            return
        self.current_buff.setdefault('effects', [])
        self.current_buff['effects'].append(eff)
        try:
            label = json.dumps(eff, ensure_ascii=False)
        except Exception:
            label = str(eff)
        self.eff_listbox.insert(tk.END, label)

    def edit_effect(self):
        sel = self.eff_listbox.curselection()
        if not sel:
            messagebox.showwarning('警告', '请先选择一个效果项')
            return
        idx = sel[0]
        old = self.current_buff.get('effects', [])[idx]
        new = show_effect_editor(self.root, old, self.modid)
        if new is None:
            return
        self.current_buff['effects'][idx] = new
        try:
            label = json.dumps(new, ensure_ascii=False)
        except Exception:
            label = str(new)
        self.eff_listbox.delete(idx)
        self.eff_listbox.insert(idx, label)

    def remove_effect(self):
        sel = self.eff_listbox.curselection()
        if not sel:
            messagebox.showwarning('警告', '请先选择一个效果项')
            return
        idx = sel[0]
        if not messagebox.askyesno('确认', '确定删除该效果项吗？'):
            return
        self.eff_listbox.delete(idx)
        try:
            self.current_buff.get('effects', []).pop(idx)
        except Exception:
            pass


class SimpleBuffDialog:
    def __init__(self, parent, title='新建 Buff'):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry('480x280')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        frame = ttk.Frame(self.dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text='ID:').grid(row=0, column=0, sticky=tk.W)
        self.id_entry = ttk.Entry(frame, width=40)
        self.id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='名称:').grid(row=1, column=0, sticky=tk.W)
        self.name_entry = ttk.Entry(frame, width=40)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='描述:').grid(row=2, column=0, sticky=tk.W)
        self.desc_entry = ttk.Entry(frame, width=60)
        self.desc_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='持续回合 (duration):').grid(row=3, column=0, sticky=tk.W)
        self.duration_entry = ttk.Entry(frame, width=20)
        self.duration_entry.grid(row=3, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='最大叠加 (max_stacks):').grid(row=4, column=0, sticky=tk.W)
        self.stacks_entry = ttk.Entry(frame, width=20)
        self.stacks_entry.grid(row=4, column=1, sticky=(tk.W, tk.E))

        btnf = ttk.Frame(self.dialog, padding=8)
        btnf.pack(fill=tk.X)
        ttk.Button(btnf, text='确定', command=self.on_ok).pack(side=tk.RIGHT, padx=6)
        ttk.Button(btnf, text='取消', command=self.on_cancel).pack(side=tk.RIGHT)
        self.dialog.wait_window()

    def on_ok(self):
        sid = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get().strip()
        dur = self.duration_entry.get().strip()
        stacks = self.stacks_entry.get().strip()
        if not sid:
            messagebox.showerror('错误', 'ID 不能为空')
            return
        try:
            dur_val = int(dur) if dur != '' else 0
        except Exception:
            messagebox.showerror('错误', 'duration 必须为整数')
            return
        try:
            stacks_val = int(stacks) if stacks != '' else 1
        except Exception:
            messagebox.showerror('错误', 'max_stacks 必须为整数')
            return
        self.result = {'id': sid, 'name': name, 'description': desc, 'duration': dur_val, 'max_stacks': stacks_val, 'effects': []}
        self.dialog.destroy()

    def on_cancel(self):
        self.dialog.destroy()


class BuffChooserDialog:
    """
    弹出对话框选择 Buff：列出当前模组下的 Buff（id - name），双击或选择后点击确定返回 id。
    使用方式：chooser = BuffChooserDialog(parent, modid); 选择结果保存在 chooser.result
    """
    def __init__(self, parent, modid):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title('选择 Buff')
        self.dialog.geometry('420x380')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        frame = ttk.Frame(self.dialog, padding=8)
        frame.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(frame)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind('<Double-1>', self._on_double)
        sb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.listbox.yview)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.config(yscrollcommand=sb.set)

        btnf = ttk.Frame(self.dialog, padding=6)
        btnf.pack(fill=tk.X)
        ttk.Button(btnf, text='确定', command=self._on_ok).pack(side=tk.RIGHT, padx=6)
        ttk.Button(btnf, text='取消', command=self._on_cancel).pack(side=tk.RIGHT)

        items = []
        # 优先使用后端获取列表
        try:
            ctrl = BuffController(modid)
            buffs = ctrl.get_all_buffs() or []
            for b in buffs:
                bid = b.get('id') or ''
                name = b.get('name') or ''
                label = f"{bid} - {name}" if bid else name
                items.append((bid or name, label))
        except Exception:
            # 回退到直接读取文件
            buffs_path = Path(__file__).resolve().parent / 'mods' / modid / 'data' / modid / 'buffs'
            if buffs_path.exists():
                for f in sorted(buffs_path.glob('*.json')):
                    try:
                        with open(f, 'r', encoding='utf-8') as fh:
                            data = json.load(fh)
                        bid = data.get('id') or f.stem
                        name = data.get('name', '')
                        label = f"{bid} - {name}"
                    except Exception:
                        label = f.stem
                        bid = f.stem
                    items.append((bid, label))

        for bid, label in items:
            self.listbox.insert(tk.END, label)

        self.dialog.wait_window()

    def _on_double(self, _ev=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        label = self.listbox.get(sel[0])
        bid = label.split(' - ')[0]
        self.result = bid
        self.dialog.destroy()

    def _on_ok(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning('警告', '请先选择一个 Buff')
            return
        label = self.listbox.get(sel[0])
        bid = label.split(' - ')[0]
        self.result = bid
        self.dialog.destroy()

    def _on_cancel(self):
        self.dialog.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = BuffManagerUI(root, 'test')
    root.mainloop()
