#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拆分出的 ModManagerUI 模块，包含模组目录常量、辅助函数以及 ModManagerUI 类。
"""
from pathlib import Path
import shutil
import json
import subprocess
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from logger import log

import mod_controller as controller

from mod_menu import ModMenuUI

SCRIPT_DIR = Path(__file__).resolve().parent
MODS_DIR = SCRIPT_DIR / "mods"

DEFAULT_MANIFEST = {
    "id": "",
    "name": "",
    "description": "",
    "version": "0.0.1",
    "dependencies": []
}


def ensure_mods_dir():
    MODS_DIR.mkdir(parents=True, exist_ok=True)


def list_mods():
    ensure_mods_dir()
    mods = [p.name for p in MODS_DIR.iterdir() if p.is_dir() and not p.name.startswith('.')]
    mods.sort()
    return mods


class ModManagerUI:
    def __init__(self, root):
        self.root = root
        root.title('模组管理器')
        root.geometry('700x400')

        main = ttk.Frame(root, padding=8)
        main.pack(fill='both', expand=True)

        # 左侧：模组列表
        left = ttk.Frame(main)
        left.pack(side='left', fill='both', expand=True)

        lbl = ttk.Label(left, text='模组列表')
        lbl.pack(anchor='w')

        self.list_var = tk.StringVar(value=list_mods())
        self.listbox = tk.Listbox(left, listvariable=self.list_var, height=20)
        self.listbox.pack(side='left', fill='both', expand=True)
        self.listbox.bind('<Double-Button-1>', lambda e: self.open_selected())

        scrollbar = ttk.Scrollbar(left, orient='vertical', command=self.listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=scrollbar.set)

        # 右侧：按钮
        right = ttk.Frame(main, width=180)
        right.pack(side='right', fill='y')

        btn_open = ttk.Button(right, text='打开', command=self.open_selected)
        btn_open.pack(fill='x', pady=6)

        btn_new = ttk.Button(right, text='新建', command=self.create_new_mod)
        btn_new.pack(fill='x', pady=6)

        btn_delete = ttk.Button(right, text='删除', command=self.delete_selected)
        btn_delete.pack(fill='x', pady=6)

        #btn_edit = ttk.Button(right, text='编辑配置', command=self.edit_config_selected)
        #btn_edit.pack(fill='x', pady=6)

        btn_refresh = ttk.Button(right, text='刷新', command=self.refresh_list)
        btn_refresh.pack(fill='x', pady=6)

        # 状态栏
        self.status = tk.StringVar()
        statusbar = ttk.Label(root, textvariable=self.status, relief='sunken', anchor='w')
        statusbar.pack(side='bottom', fill='x')
        self.set_status('就绪')

    def set_status(self, text):
        self.status.set(text)

    def refresh_list(self):
        names = list_mods()
        self.list_var.set(names)
        self.set_status(f'共 {len(names)} 个模组')

    def get_selected_name(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        return self.listbox.get(sel[0])

    def open_selected(self):
        modid = self.get_selected_name()
        if not modid:
            messagebox.showinfo('提示', '请先选择一个模组')
            return
        path = MODS_DIR / modid
        if not path.exists():
            messagebox.showerror('错误', '选定的模组不存在')
            self.refresh_list()
            return
        try:
            mod_ctrl = controller.ModController(modid)
            mod_menu_ui = ModMenuUI(tk.Toplevel(self.root), mod_ctrl)
            self.set_status(f'已打开模组编辑界面：{modid}')
            log.console(f'启动 mod_menu 打开模组：{modid}', 'INFO')
        except Exception as e:
            messagebox.showerror('错误', f'无法打开模组文件夹：{e}')
            log.console(f'无法打开模组：{e}', 'ERROR')

    def create_new_mod(self):
        modid = simpledialog.askstring('新建模组', '请输入模组id：', parent=self.root)
        if not modid:
            return
        # 防止包含路径分隔符
        modid = modid.strip()
        if not modid:
            messagebox.showwarning('警告', '名称不能为空')
            return
        target = MODS_DIR / modid
        if target.exists():
            messagebox.showwarning('警告', '已存在同名模组')
            return
        try:
            mod_ctrl = controller.ModController(modid)
            mod_ctrl.init_mod_directory()
            self.refresh_list()
            self.set_status(f'已创建：{modid}')
        except Exception as e:
            messagebox.showerror('错误', f'创建失败：{e}')

    def delete_selected(self):
        modid = self.get_selected_name()
        if not modid:
            messagebox.showinfo('提示', '请先选择一个模组')
            return
        if not messagebox.askyesno('确认删除', f'确定要删除模组 "{modid}" 吗？此操作不可恢复。'):
            return
        target = MODS_DIR / modid
        try:
            shutil.rmtree(target)
            self.refresh_list()
            self.set_status(f'已删除：{modid}')
        except Exception as e:
            messagebox.showerror('错误', f'删除失败：{e}')

    def edit_config_selected(self):
        modid = self.get_selected_name()
        if not modid:
            messagebox.showinfo('提示', '请先选择一个模组')
            return
        cfg_path = MODS_DIR / modid / 'manifest.json'
        try:
            if not cfg_path.exists():
                cfg = DEFAULT_MANIFEST.copy()
                cfg['id'] = modid
                cfg_path.parent.mkdir(parents=True, exist_ok=True)
                with cfg_path.open('w', encoding='utf-8') as f:
                    json.dump(cfg, f, ensure_ascii=False, indent=2)
            # 在 macOS 上使用默认编辑器打开文件
            subprocess.run(['open', str(cfg_path)])
            self.set_status(f'打开配置：{modid}/manifest.json')
        except Exception as e:
            messagebox.showerror('错误', f'无法打开配置：{e}')
