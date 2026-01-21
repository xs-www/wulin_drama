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
    'add_buff',
    'remove_buff',
    'add_statu',
    'remove_statu'
]


def show_effect_editor(parent: Optional[tk.Tk] = None, initial: Optional[Dict] = None) -> Optional[Dict]:
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
    ent_param = ttk.Entry(frm, textvariable=var_param, width=30)
    ent_param.grid(row=1, column=1, sticky='ew', padx=6, pady=4)

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

    # 初始化预览
    update_preview()

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
            # owner 不存在场景下 owner==None; 确保销毁 dlg
            dlg.destroy()
        except Exception:
            pass

    return result['value']


if __name__ == '__main__':
    # 简单的运行示例
    def _test():
        res = show_effect_editor()
        print('结果:', res)
    _test()
