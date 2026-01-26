import tkinter as tk
from tkinter import ttk, messagebox
import json, sys, os
from pathlib import Path

# 添加当前目录到路径，确保能导入本工程的模块（如需要）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mod_controller import TriggerController

class TriggerManagerUI:
    def __init__(self, root, modid):
        self.root = root
        self.modid = modid
        self.root.title('触发器注册管理')
        self.root.geometry('640x360')
        # 使用 TriggerController 处理后端操作
        self.ctrl = TriggerController(modid)
        self.current = None
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        main = ttk.Frame(self.root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,8))

        self.listbox = tk.Listbox(left, width=30, height=18)
        self.listbox.pack(side=tk.TOP, fill=tk.Y, expand=False)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        lb_scroll = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.listbox.yview)
        lb_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.config(yscrollcommand=lb_scroll.set)
        # parallel array to store full IDs corresponding to listbox entries
        self.list_ids = []

        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill=tk.X, pady=6)
        ttk.Button(btn_frame, text='新建', command=self.new_trigger).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text='删除', command=self.delete_trigger).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text='刷新', command=self.refresh_list).pack(side=tk.LEFT, padx=4)
        # 仅显示本模组选项
        self.only_self_var = tk.BooleanVar(value=False)
        cb = ttk.Checkbutton(btn_frame, text='只看本模组', variable=self.only_self_var, command=self.refresh_list)
        cb.pack(side=tk.LEFT, padx=(8,0))

        # 右侧精简详情编辑
        right = ttk.Frame(main)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right.columnconfigure(1, weight=1)

        ttk.Label(right, text='ID:').grid(row=0, column=0, sticky=tk.W, pady=4, padx=4)
        self.id_var = tk.StringVar()
        self.id_entry = ttk.Entry(right, textvariable=self.id_var)
        self.id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=4, padx=4)

        ttk.Label(right, text='名称:').grid(row=1, column=0, sticky=tk.W, pady=4, padx=4)
        self.name_var = tk.StringVar()
        ttk.Entry(right, textvariable=self.name_var).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=4, padx=4)

        ttk.Label(right, text='描述:').grid(row=2, column=0, sticky=tk.NW, pady=4, padx=4)
        self.desc_text = tk.Text(right, height=8)
        self.desc_text.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=4, padx=4)

        self.enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(right, text='启用', variable=self.enabled_var).grid(row=3, column=1, sticky=tk.W, pady=2, padx=4)

        action_btn_frame = ttk.Frame(right)
        action_btn_frame.grid(row=4, column=1, sticky=tk.EW, pady=(8,0), padx=4)
        ttk.Button(action_btn_frame, text='保存', command=self.save_trigger).pack(side=tk.RIGHT, padx=4)

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        self.list_ids.clear()
        # 根据复选框决定是否仅加载本模组
        is_self = bool(self.only_self_var.get()) if hasattr(self, 'only_self_var') else False
        try:
            # 尝试将 is_self 传给 controller；若不支持该参数则回退到无参数调用
            try:
                triggers = self.ctrl.get_all_triggers(is_self) or []
            except TypeError:
                triggers = self.ctrl.get_all_triggers() or []
        except Exception:
            triggers = []
        for trig in triggers:
            full_id = str(trig.get('id') or '')
            short = full_id.split('/')[-1] if full_id else ''
            label = f"{short} - {trig.get('name','') }"
            self.listbox.insert(tk.END, label)
            self.list_ids.append(full_id)

    def on_select(self, event):
         sel = self.listbox.curselection()
         if not sel:
            return
         idx = sel[0]
         # use stored full id for lookup
         try:
            full_id = self.list_ids[idx]
         except Exception:
            full_id = None
         if not full_id:
            messagebox.showerror('错误', '无法获取对应的触发器 ID')
            return
         try:
            data = self.ctrl.get_trigger_by_id(full_id)
         except Exception:
            data = None
         if not data:
            short = full_id.split('/')[-1]
            messagebox.showerror('错误', f'无法加载触发器 {short}')
            return
         self.load_into_form(data)
         # keep current as short id for UI purposes
         self.current = full_id.split('/')[-1]

    def load_into_form(self, data: dict):
        # 在界面中仅显示短 ID（不含 mod 前缀），保存时使用完整 ID
        full_id = str(data.get('id',''))
        short_id = full_id.split('/')[-1] if full_id else ''
        self.id_var.set(short_id)
        # 将 ID 设为只读，防止修改已存在的 ID
        try:
            self.id_entry.config(state='readonly')
        except Exception:
            pass
        self.name_var.set(str(data.get('name','')))
        try:
            self.desc_text.delete(1.0, tk.END)
            d = data.get('description') or data.get('decription') or ''
            if isinstance(d, (dict, list)):
                self.desc_text.insert(1.0, json.dumps(d, ensure_ascii=False, indent=2))
            else:
                self.desc_text.insert(1.0, str(d))
        except Exception:
            self.desc_text.delete(1.0, tk.END)
            self.desc_text.insert(1.0, '')
        self.enabled_var.set(bool(data.get('enabled', True)))

    def new_trigger(self):
        # 清空表单，允许输入新 ID
        self.current = None
        try:
            self.listbox.selection_clear(0, tk.END)
        except Exception:
            pass
        self.id_var.set('')
        try:
            self.id_entry.config(state='normal')
            self.id_entry.focus_set()
        except Exception:
            pass
        self.name_var.set('')
        self.desc_text.delete(1.0, tk.END)
        self.enabled_var.set(True)

    def delete_trigger(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning('警告', '请先选择要删除的触发器')
            return
        idx = sel[0]
        # use stored full id
        try:
            full_id = self.list_ids[idx]
        except Exception:
            messagebox.showerror('错误', '无法获取对应的触发器 ID')
            return
        short = full_id.split('/')[-1]
        if not messagebox.askyesno('确认', f'确定删除触发器 {short} ?'):
            return
        try:
            ok = self.ctrl.delete_trigger(full_id)
        except Exception as e:
            ok = False
        if ok:
            messagebox.showinfo('成功', '删除成功')
            self.refresh_list()
        else:
            messagebox.showerror('失败', '删除失败')

    def save_trigger(self):
        entered = self.id_var.get().strip()
        if not entered:
            messagebox.showerror('错误', 'ID 不能为空')
            return
        # 生成完整 ID（modid: Trigger/id），如果用户已经输入完整 ID 则保持不变
        if entered.startswith(f"{self.modid}:Trigger/") or (':' in entered and '/' in entered):
            full_id = entered
        else:
            full_id = f"{self.modid}:Trigger/{entered}"
        eid = full_id
        name = self.name_var.get().strip()
        desc_raw = self.desc_text.get(1.0, tk.END).strip()
        desc_val = desc_raw
        # 尝试解析 description 为 JSON，否则保持为字符串
        try:
            desc_val = json.loads(desc_raw) if desc_raw else ''
        except Exception:
            desc_val = desc_raw
        enabled = bool(self.enabled_var.get())

        rec = {
            'id': eid,
            'name': name,
            'description': desc_val,
            'enabled': enabled
        }

        try:
            exists = self.ctrl.get_trigger_by_id(eid)
        except Exception:
            exists = None
        # 注意：self.current 在 UI 中保留短 id（不含 mod 前缀），因此比较时用短 id
        short_entered = eid.split('/')[-1]
        if exists and (not self.current or self.current != short_entered):
            # 存在且不是当前正在编辑的项，询问是否覆盖
            if not messagebox.askyesno('覆盖', f'ID {short_entered} 已存在，是否覆盖？'):
                return
        try:
            if exists:
                ok = self.ctrl.update_trigger(rec)
            else:
                ok = self.ctrl.create_trigger(rec)
        except Exception:
            ok = False
        if ok:
            messagebox.showinfo('成功', '保存成功')
            self.refresh_list()
            # 更新 current 为短 id
            self.current = short_entered
        else:
            messagebox.showerror('失败', '保存失败')


if __name__ == '__main__':
    root = tk.Tk()
    app = TriggerManagerUI(root, 'test')
    root.mainloop()