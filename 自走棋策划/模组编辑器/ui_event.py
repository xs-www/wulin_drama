import tkinter as tk
from tkinter import ttk, messagebox
import json, sys, os
from pathlib import Path

# 添加当前目录到路径，确保能导入本工程的模块（如需要）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mod_controller import EventController

# 简单事件类型列表，参考 文档：文档中可扩展或从文件读取
EVENT_TYPES = {
    'onAttack': ['beforeAttack', 'afterAttack'],
    'onTurnStart': [],
    'onGameStart': [],
    'onAct': [],
    'onGetHurt': ['beforeGetHurt', 'afterGetHurt'],
    'onEntityDead': [],
    'onAttrChanged': [],
    'onSkillReleased': [],
    'onBuffApplied': [],
    'onBuffExpired': [],
    'onBuffRemoved': [],
    'onAddStatu': [],
    'onRemoveStatu': []
}


class EventManagerUI:
    def __init__(self, root, modid):
        self.root = root
        self.modid = modid
        self.root.title('事件注册管理')
        self.root.geometry('640x360')
        # 使用 EventController 处理后端操作
        self.ctrl = EventController(modid)
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

        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill=tk.X, pady=6)
        ttk.Button(btn_frame, text='新建', command=self.new_event).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text='删除', command=self.delete_event).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text='刷新', command=self.refresh_list).pack(side=tk.LEFT, padx=4)

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
        ttk.Button(action_btn_frame, text='保存', command=self.save_event).pack(side=tk.RIGHT, padx=4)

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        try:
            events = self.ctrl.get_all_events() or []
        except Exception:
            events = []
        for e in events:
            eid = e.get('id').split('/')[-1]
            label = f"{eid} - {e.get('name','') }"
            self.listbox.insert(tk.END, label)

    def on_select(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        label = self.listbox.get(idx)
        eid = label.split(' - ')[0]
        try:
            data = self.ctrl.get_event_by_id(eid)
        except Exception:
            data = None
        if not data:
            messagebox.showerror('错误', f'无法加载事件 {eid}')
            return
        self.load_into_form(data)
        self.current = eid

    def load_into_form(self, data: dict):
        self.id_var.set(str(data.get('id','')))
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

    def new_event(self):
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

    def delete_event(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning('警告', '请先选择要删除的事件注册')
            return
        idx = sel[0]
        label = self.listbox.get(idx)
        eid = label.split(' - ')[0]
        if not messagebox.askyesno('确认', f'确定删除事件注册 {eid} ?'):
            return
        try:
            ok = self.ctrl.delete_event(eid)
        except Exception as e:
            ok = False
        if ok:
            messagebox.showinfo('成功', '删除成功')
            self.refresh_list()
        else:
            messagebox.showerror('失败', '删除失败')

    def save_event(self):
        eid = self.id_var.get().strip()
        if not eid:
            messagebox.showerror('错误', 'ID 不能为空')
            return
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
            exists = self.ctrl.get_event_by_id(eid)
        except Exception:
            exists = None
        if exists and (not self.current or self.current != eid):
            # 存在且不是当前正在编辑的项，询问是否覆盖
            if not messagebox.askyesno('覆盖', f'ID {eid} 已存在，是否覆盖？'):
                return
        try:
            if exists:
                ok = self.ctrl.update_event(rec)
            else:
                ok = self.ctrl.create_event(rec)
        except Exception:
            ok = False
        if ok:
            messagebox.showinfo('成功', '保存成功')
            self.refresh_list()
            self.current = eid
        else:
            messagebox.showerror('失败', '保存失败')


if __name__ == '__main__':
    root = tk.Tk()
    app = EventManagerUI(root, 'test')
    root.mainloop()