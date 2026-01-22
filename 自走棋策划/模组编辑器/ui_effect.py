#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模组编辑器：效果（effect）编辑界面
- effect 字典结构: {"type": ..., "param": ..., "mode": ...}
- 提供实时自然语言预览（调用 utils.effect_parser）
- 导出时返回 effect 字典
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict
from pathlib import Path
import json

try:
    from utils import effect_parser
except Exception:
    def effect_parser(d):
        return '无法加载解析器'

try:
    from utils import log
except Exception:
    class _Dummy:
        def console(self, *a, **k):
            pass
    log = _Dummy()

EFFECT_TYPES = [
    'modify_attr',
    'cause_damage',
    'heal',
    'add_buff',
    'remove_buff',
    'add_status',
    'remove_status',
    'add_skill',
    'remove_skill',
    'emit_event',
]


def show_effect_editor(parent: Optional[tk.Tk] = None, initial: Optional[Dict] = None, modid: Optional[str] = None) -> Optional[Dict]:
    """显示效果编辑器对话框，返回效果字典或 None（取消）"""
    owner = parent
    created_root = False
    # 如果没有传入父窗口，直接使用主窗口（Tk），否则使用模态 Toplevel
    if owner is None:
        dlg = tk.Tk()
        created_root = True
    else:
        dlg = tk.Toplevel(owner)
        # 设为模态窗口
        try:
            dlg.transient(owner)
            dlg.grab_set()
        except Exception:
            pass
    dlg.title('效果编辑器')
    dlg.geometry('600x300')

    # 确保窗口在最前并可见（防止被其他窗口遮挡或隐藏）
    try:
        dlg.lift()
        dlg.attributes('-topmost', True)
        dlg.after(100, lambda: dlg.attributes('-topmost', False))
        dlg.focus_force()
    except Exception:
        pass

    # 将窗口居中于屏幕
    try:
        dlg.update_idletasks()
        w = dlg.winfo_width()
        h = dlg.winfo_height()
        sw = dlg.winfo_screenwidth()
        sh = dlg.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        dlg.geometry(f'+{x}+{y}')
    except Exception:
        pass

    result = {'value': None}

    # Vars
    var_type = tk.StringVar(value=(initial.get('type') if initial else EFFECT_TYPES[0]))
    var_param = tk.StringVar(value=(initial.get('param') if initial else ''))
    var_mode = tk.StringVar(value=(initial.get('mode') if initial else ''))
    # 用于记录为 param 文本变量添加的 trace id，以便在替换控件时移除
    param_trace_ids = []

    def update_preview(*_):
        eff = {'type': var_type.get(), 'param': var_param.get(), 'mode': var_mode.get()}
        try:
            if var_param.get() != '' or var_mode.get() != '':
                desc = effect_parser(eff)
            else:
                desc = ''
        except Exception as e:
            desc = f'解析异常: {e}'
            log.console(f'效果解析异常: {e}', 'ERROR')
        txt_preview.config(state='normal')
        txt_preview.delete('1.0', 'end')
        txt_preview.insert('1.0', desc)
        txt_preview.config(state='disabled')

    # Left: form and preview
    top_label = ttk.Label(dlg, text='效果编辑器', font=('Helvetica', 14, 'bold'))
    top_label.pack(anchor='center', pady=(6, 0))

    # 左侧：输入与预览（宽度缩短）
    left = ttk.Frame(dlg, padding=8, width=340)
    left.pack(side='left', fill='both', expand=False)

    frm = ttk.Frame(left)
    frm.pack(fill='x')

    ttk.Label(frm, text='类型 (type)').grid(row=0, column=0, sticky='w')
    cb_type = ttk.Combobox(frm, values=EFFECT_TYPES, textvariable=var_type, state='readonly', width=30)
    cb_type.grid(row=0, column=1, sticky='ew', padx=6, pady=4)

    ttk.Label(frm, text='参数 (param)').grid(row=1, column=0, sticky='w')
    # param 区域为可替换容器：默认是 Entry，也可能是 选择 按钮 + 预览标签
    param_container = ttk.Frame(frm)
    param_container.grid(row=1, column=1, sticky='ew', padx=6, pady=4)

    def create_param_entry():
        # 移除之前为标签注册的 trace，防止回调引用已销毁控件
        try:
            for tid in list(param_trace_ids):
                try:
                    var_param.trace_remove('write', tid)
                except Exception:
                    pass
            param_trace_ids.clear()
        except Exception:
            pass
        for w in param_container.winfo_children():
            w.destroy()
        ent = ttk.Entry(param_container, textvariable=var_param, width=30)
        ent.pack(fill='x', expand=True)
        return ent

    def create_param_button(label_text, on_click):
        # 移除之前的 trace
        try:
            for tid in list(param_trace_ids):
                try:
                    var_param.trace_remove('write', tid)
                except Exception:
                    pass
            param_trace_ids.clear()
        except Exception:
            pass
        for w in param_container.winfo_children():
            w.destroy()
        btn = ttk.Button(param_container, text=label_text, command=on_click)
        btn.pack(side='left')
        lbl = ttk.Label(param_container, text=var_param.get() or '', width=18)
        lbl.pack(side='left', padx=(6,0))
        # 当 var_param 变化时更新标签，使用 try/except 包装以防 lbl 已被销毁
        def _update_lbl(*_):
            try:
                lbl.config(text=var_param.get() or '')
            except Exception:
                pass
        # 保存 trace id，便于以后移除
        try:
            tid = var_param.trace_add('write', _update_lbl)
            param_trace_ids.append(tid)
        except Exception:
            # 退回到不注册 trace 的模式
            pass
        return btn, lbl

    # 默认创建 Entry
    ent_param = create_param_entry()

    ttk.Label(frm, text='目标/模式 (mode)').grid(row=2, column=0, sticky='w')
    ent_mode = ttk.Entry(frm, textvariable=var_mode, width=30)
    ent_mode.grid(row=2, column=1, sticky='ew', padx=6, pady=4)

    frm.columnconfigure(1, weight=1)

    ttk.Label(left, text='实时预览:').pack(anchor='w', pady=(8, 0))
    # 预览窗口高度稍短，避免占用过多空间
    txt_preview = tk.Text(left, height=6, wrap='word', state='disabled', width=30)
    txt_preview.pack(fill='both', expand=True, pady=4)

    # 右侧：按钮（宽度缩短但保证中文显示）
    right = ttk.Frame(dlg, width=180, padding=10)
    right.pack(side='right', fill='y')

    def on_clear():
        var_type.set(EFFECT_TYPES[0])
        var_param.set('')
        var_mode.set('')
        update_preview()

    def on_ok():
        eff = {'type': var_type.get(), 'param': var_param.get(), 'mode': var_mode.get()}
        # 检查解析结果，若解析器返回空或错误提示，询问是否继续保存
        try:
            desc = effect_parser(eff)
        except Exception as e:
            desc = None
            log.console(f'解析器异常: {e}', 'ERROR')
        if not desc or (isinstance(desc, str) and '格式错误' in desc) or desc == '{}':
            if not messagebox.askyesno('解析失败', '当前输入无法被解析为有效描述，是否仍然保存？', parent=dlg):
                return
        result['value'] = eff
        dlg.destroy()

    def on_cancel():
        result['value'] = None
        dlg.destroy()

    def on_docs():
        # 尝试打开项目内的 data/效果文档.md，以只读预览窗口显示
        try:
            docs_path = Path(__file__).resolve().parent / 'data' / '效果文档.md'
            if docs_path.exists():
                with docs_path.open('r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = (
                    '未找到本地文档文件：data/效果文档.md\n\n'
                    '请在该路径下添加说明文档，或查看内置简要说明。\n\n'
                )
                # 内置简要说明
                content += (
                    '字段说明:\n'
                    '- type: 效果类型，例如 modify_attr / add_buff / remove_buff / add_statu / remove_statu\n'
                    "- param: 单行参数字符串，示例: ATK+15 或 MHP+10%b (支持 %b/%m/%r)\n"
                    "- mode: 目标/范围，例如 self / all_ally / all_enemy\n"
                )

            # 创建只读预览窗口
            pv = tk.Toplevel(dlg)
            pv.title('效果文档预览')
            pv.geometry('720x480')
            try:
                pv.transient(dlg)
                pv.grab_set()
            except Exception:
                pass

            txt = tk.Text(pv, wrap='word')
            txt.pack(fill='both', expand=True)
            txt.insert('1.0', content)
            txt.config(state='disabled')

            # 添加关闭按钮
            btn_close = ttk.Button(pv, text='关闭', command=pv.destroy)
            btn_close.pack(pady=6)

            # 居中并置顶预览窗口
            try:
                pv.update_idletasks()
                pv.lift()
                pv.attributes('-topmost', True)
                pv.after(120, lambda: pv.attributes('-topmost', False))
                pv.focus_force()
                w = pv.winfo_width()
                h = pv.winfo_height()
                sw = pv.winfo_screenwidth()
                sh = pv.winfo_screenheight()
                x = (sw - w) // 2
                y = (sh - h) // 2
                pv.geometry(f'+{x}+{y}')
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror('无法打开文档', f'读取文档失败: {e}', parent=dlg)

    # 固定按钮宽度（字符数），确保中文显示完整
    BTN_WIDTH = 12
    btn_clear = ttk.Button(right, text='清空', command=on_clear, width=BTN_WIDTH)
    btn_clear.pack(fill='x', pady=8, padx=6)

    btn_ok = ttk.Button(right, text='确定', command=on_ok, width=BTN_WIDTH)
    btn_ok.pack(fill='x', pady=8, padx=6)

    btn_cancel = ttk.Button(right, text='取消', command=on_cancel, width=BTN_WIDTH)
    btn_cancel.pack(fill='x', pady=8, padx=6)

    btn_docs = ttk.Button(right, text='查看文档', command=on_docs, width=BTN_WIDTH)
    btn_docs.pack(fill='x', pady=8, padx=6)

    # Trace changes for realtime preview
    var_type.trace_add('write', update_preview)
    var_param.trace_add('write', update_preview)
    var_mode.trace_add('write', update_preview)

    # 当 type 为某些值时，param 使用选择器而非文本输入
    CHOOSER_TYPES = {
        'add_buff': ('添加 Buff', 'buffs'),
        'remove_buff': ('移除 Buff', 'buffs'),
        'add_status': ('添加状态', 'statuses'),
        'remove_status': ('移除状态', 'statuses'),
        'add_skill': ('添加技能', 'skills'),
        'remove_skill': ('移除技能', 'skills'),
        'emit_event': ('添加事件', 'events')
    }

    def open_chooser(kind_key):
        # kind_key in {'buffs','statuses','skills','events'}
        mid = modid
        # 尝试使用对应 Controller
        try:
            from mod_controller import EventController, SkillController
        except Exception:
            EventController = None
            SkillController = None

        # Helper: scan all mods for files when mid is None or controller returned empty
        def scan_all(kind):
            base = Path(__file__).resolve().parent / 'mods'
            res = []
            if not base.exists():
                return res
            for m in sorted([p for p in base.iterdir() if p.is_dir()]):
                folder = m / 'data' / m.name / kind
                if folder.exists():
                    for f in sorted(folder.glob('*.json')):
                        try:
                            with open(f, 'r', encoding='utf-8') as fh:
                                data = json.load(fh)
                            res.append((data.get('id') or f.stem, data.get('name','')))
                        except Exception:
                            res.append((f.stem, ''))
            return res

        if kind_key == 'events':
            choices = []
            if mid and EventController:
                try:
                    evc = EventController(mid)
                    items = evc.get_all_events() or []
                    choices = [(e.get('id') or e.get('eid') or '', e.get('name','')) for e in items]
                except Exception:
                    choices = []
            # fallback: scan filesystem for events across mods
            if not choices:
                choices = scan_all('events')
            picker = _SimpleChoiceDialog(dlg_owner=dlg, title='选择事件', items=choices)
            return picker.result
        elif kind_key == 'skills':
            choices = []
            if mid and SkillController:
                try:
                    sc = SkillController(mid)
                    items = sc.get_all_skills() or []
                    choices = [(s.get('id') or '', s.get('name','')) for s in items]
                except Exception:
                    choices = []
            if not choices:
                # try scanning files across mods
                choices = scan_all('skills')
            picker = _SimpleChoiceDialog(dlg_owner=dlg, title='选择技能', items=choices)
            return picker.result
        else:
            # buffs / statuses: 尝试从文件夹读取
            choices = []
            if mid:
                base = Path(__file__).resolve().parent / 'mods' / mid / 'data' / mid
                folder = base / ('buffs' if kind_key == 'buffs' else 'statuses')
                if folder.exists():
                    for f in sorted(folder.glob('*.json')):
                        try:
                            with open(f, 'r', encoding='utf-8') as fh:
                                data = json.load(fh)
                            choices.append((data.get('id') or f.stem, data.get('name','')))
                        except Exception:
                            choices.append((f.stem, ''))
            # fallback: scan all mods
            if not choices:
                choices = scan_all('buffs' if kind_key == 'buffs' else 'statuses')
            picker = _SimpleChoiceDialog(dlg_owner=dlg, title='选择', items=choices)
            return picker.result

    def update_param_widget_by_type(_type=None):
        t = _type or var_type.get()
        if t in CHOOSER_TYPES:
            label_text, kind = CHOOSER_TYPES[t]
            # kind may be 'buffs','statuses','skills','events'
            def _on_choose():
                res = open_chooser(kind)
                if res:
                    var_param.set(res)
            create_param_button(label_text, _on_choose)
        else:
            create_param_entry()

    # 初始根据 type 更新 param 控件
    update_param_widget_by_type(var_type.get())

    # 初始化预览
    update_preview()

    # 当 type 变化时，切换 param 控件并更新预览
    def _on_type_changed(*_):
        update_param_widget_by_type()
        update_preview()
    var_type.trace_add('write', _on_type_changed)

    # 确保窗口更新并可见
    try:
        dlg.update_idletasks()
        dlg.minsize(460, 260)
        dlg.lift()
        dlg.attributes('-topmost', True)
        dlg.after(120, lambda: dlg.attributes('-topmost', False))
        dlg.focus_force()
    except Exception:
        pass

    # 等待对话框关闭：如果是独立主窗口则运行 mainloop，否则等待窗口销毁
    if created_root:
        try:
            dlg.mainloop()
        except Exception:
            pass
    else:
        dlg.wait_window()

    if created_root:
        try:
            dlg.destroy()
        except Exception:
            pass

    return result['value']


class _SimpleChoiceDialog:
    """内部简易选择器：items 是 list of (id, name)"""
    def __init__(self, dlg_owner, title='选择', items=None):
        self.result = None
        self.dlg = tk.Toplevel(dlg_owner) if dlg_owner else tk.Tk()
        self.dlg.title(title)
        self.dlg.geometry('420x380')
        try:
            if dlg_owner:
                self.dlg.transient(dlg_owner)
                self.dlg.grab_set()
        except Exception:
            pass
        frm = ttk.Frame(self.dlg, padding=8)
        frm.pack(fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(frm)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(frm, orient=tk.VERTICAL, command=self.listbox.yview)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.config(yscrollcommand=sb.set)
        items = items or []
        for iid, name in items:
            self.listbox.insert(tk.END, f"{iid} - {name}")
        btnf = ttk.Frame(self.dlg, padding=6)
        btnf.pack(fill=tk.X)
        ttk.Button(btnf, text='确定', command=self._on_ok).pack(side=tk.RIGHT, padx=6)
        ttk.Button(btnf, text='取消', command=self._on_cancel).pack(side=tk.RIGHT)
        self.listbox.bind('<Double-1>', lambda e: self._on_ok())
        self.dlg.wait_window()

    def _on_ok(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning('警告', '请先选择一项')
            return
        label = self.listbox.get(sel[0])
        self.result = label.split(' - ')[0]
        try:
            self.dlg.destroy()
        except Exception:
            pass

    def _on_cancel(self):
        try:
            self.dlg.destroy()
        except Exception:
            pass

if __name__ == '__main__':
    # 简单的运行示例
    def _test():
        res = show_effect_editor(modid='test')
        print('结果:', res)
    _test()
