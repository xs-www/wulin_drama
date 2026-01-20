#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import subprocess
import sys, os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from character_ui import CharacterManagerUI
from mod_controller import ModController

# 引入项目日志工具（若不存在则静默）
try:
    from utils import log
except Exception:
    class _DummyLog:
        def console(self, *a, **k):
            pass
    log = _DummyLog()

SCRIPT_DIR = Path(__file__).resolve().parent
MODS_DIR = SCRIPT_DIR / 'mods'


class FileTree(ttk.Frame):
    def __init__(self, master, root_path: Path, **kwargs):
        super().__init__(master, **kwargs)
        self.root_path = root_path
        self.tree = ttk.Treeview(self)
        self.tree.pack(fill='both', expand=True, side='left')
        self.vsb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=self.vsb.set)

        # 使用 root_path 名称作为根节点标题
        self.tree.heading('#0', text=str(self.root_path.name), anchor='w')
        self._populate_root()
        self.tree.bind('<Double-1>', self._on_double_click)

    def _populate_root(self):
        # 清空并构建整个树（递归）
        self.tree.delete(*self.tree.get_children())
        # 插入根节点，使用路径字符串作为 iid，便于定位
        root_iid = str(self.root_path)
        self.tree.insert('', 'end', iid=root_iid, text=self.root_path.name, open=True)
        self._insert_children_recursively(root_iid, self.root_path)

    def _insert_children_recursively(self, parent_iid: str, path: Path):
        try:
            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except Exception as e:
            log.console(f'列出目录失败：{e}', 'ERROR')
            return
        for p in entries:
            iid = str(p)
            display = p.name
            # 避免重复 iid
            if self.tree.exists(iid):
                # 如果已存在则跳过（理论上不应该）
                continue
            try:
                self.tree.insert(parent_iid, 'end', iid=iid, text=display, open=False)
                if p.is_dir():
                    # 递归插入子节点
                    self._insert_children_recursively(iid, p)
            except Exception as e:
                log.console(f'插入节点失败：{p} -> {e}', 'ERROR')

    def refresh(self):
        self._populate_root()

    def _on_double_click(self, event):
        item = self.tree.focus()
        if not item:
            return
        target_path = Path(item)
        if not target_path.exists():
            messagebox.showerror('错误', f'路径不存在: {target_path}')
            return
        if target_path.is_dir():
            # 切换展开状态
            cur_open = self.tree.item(item, 'open')
            self.tree.item(item, open=not cur_open)
            return
        # 打开文件
        try:
            if os.name == 'nt':                   # Windows
                subprocess.run(['start', '', str(target_path)], shell=True)
            else:                                # macOS / Linux
                subprocess.run(['open', str(target_path)])
            log.console(f'打开文件：{target_path}', 'INFO')
        except Exception as e:
            messagebox.showerror('错误', f'无法打开文件：{e}')
            log.console(f'无法打开文件：{e}', 'ERROR')

    def refresh(self):
        self._populate_root()


class ModMenuUI:
    def __init__(self, root, mod_controller: ModController):
        self.root = root
        self.controller = mod_controller
        self.mod_path = mod_controller.get_mod_path()
        root.title(f'模组：{mod_controller.modid}')
        root.geometry('900x600')

        main = ttk.Frame(root, padding=8)
        main.pack(fill='both', expand=True)

        left = ttk.Frame(main)
        left.pack(side='left', fill='both', expand=True)

        self.tree = FileTree(left, self.controller.get_mod_path())
        self.tree.pack(fill='both', expand=True)

        right = ttk.Frame(main, width=220)
        right.pack(side='right', fill='y')

        btn_role = ttk.Button(right, text='编辑角色', command=self.open_character_editor)
        btn_role.pack(fill='x', pady=6)

        btn_skill = ttk.Button(right, text='编辑技能', command=self.open_skills_editor)
        btn_skill.pack(fill='x', pady=6)

        btn_data = ttk.Button(right, text='编辑数据', command=self.open_data_editor)
        btn_data.pack(fill='x', pady=6)

        btn_cfg = ttk.Button(right, text='编辑配置', command=self.open_config)
        btn_cfg.pack(fill='x', pady=6)

        btn_open = ttk.Button(right, text='打开文件夹', command=self.open_folder)
        btn_open.pack(fill='x', pady=6)

        btn_refresh = ttk.Button(right, text='刷新', command=self.refresh)
        btn_refresh.pack(fill='x', pady=6)

        self.status = tk.StringVar()
        statusbar = ttk.Label(root, textvariable=self.status, relief='sunken', anchor='w')
        statusbar.pack(side='bottom', fill='x')
        self.set_status('就绪')

    def set_status(self, text: str):
        self.status.set(text)
        log.console(text, 'INFO')

    def open_or_prompt(self, target: Path, create_if_missing: bool = False):
        if not target.exists():
            if create_if_missing:
                try:
                    if target.suffix:  # a file
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_text('{}', encoding='utf-8')
                    else:
                        target.mkdir(parents=True, exist_ok=True)
                    self.set_status(f'已创建：{target}')
                except Exception as e:
                    messagebox.showerror('错误', f'无法创建：{e}')
                    log.console(f'无法创建：{e}', 'ERROR')
                    return
            else:
                messagebox.showinfo('提示', f'未找到：{target.name}')
                return
        try:
            if os.name == 'nt':                   # Windows
                subprocess.run(['start', '', str(target)], shell=True)
            else:                                # macOS / Linux
                subprocess.run(['open', str(target)])
            self.set_status(f'打开：{target.name}')
        except Exception as e:
            messagebox.showerror('错误', f'无法打开：{e}')
            log.console(f'无法打开：{e}', 'ERROR')

    def open_character_editor(self):
        # 约定：角色数据保存在 mods/<mod>/data/character/character_id.json
        win = tk.Toplevel(self.root)
        CharacterManagerUI(win, modid=self.controller.modid)

    def open_skills_editor(self):
        candidates = [self.controller.get_mod_path() / 'skills.json', self.controller.get_mod_path() / 'data' / 'skills.json']
        for c in candidates:
            if c.exists():
                self.open_or_prompt(c)
                return
        if messagebox.askyesno('创建技能数据', '未找到技能数据文件，是否创建默认 skills.json？'):
            self.open_or_prompt(candidates[0], create_if_missing=True)

    def open_data_editor(self):
        # 打开模组里的 data 文件夹
        target = self.controller.get_mod_path() / 'data'
        if not target.exists():
            if messagebox.askyesno('创建数据文件夹', '未找到 data 文件夹，是否创建？'):
                self.open_or_prompt(target, create_if_missing=True)
            return
        self.open_or_prompt(target)

    def open_config(self):
        cfg = self.mod_path / 'manifest.json'
        if not cfg.exists():
            if messagebox.askyesno('创建配置文件', '未找到 manifest.json，是否创建默认配置？'):
                self.open_or_prompt(cfg, create_if_missing=True)
            return
        self.open_or_prompt(cfg)

    def open_folder(self):
        self.open_or_prompt(self.mod_path)

    def refresh(self):
        self.tree.refresh()
        self.set_status('已刷新')


def choose_mod_interactively():
    root = tk.Tk()
    root.withdraw()
    ensure = MODS_DIR.exists() and any(MODS_DIR.iterdir())
    if not ensure:
        messagebox.showerror('错误', f'未找到模组目录：{MODS_DIR} 或目录为空')
        sys.exit(1)
    mods = sorted([p.name for p in MODS_DIR.iterdir() if p.is_dir()])
    choice = simpledialog.askstring('选择模组', '请输入模组名称（可从列表中复制）：\n' + '\n'.join(mods), parent=root)
    root.destroy()
    if not choice:
        sys.exit(0)
    candidate = MODS_DIR / choice.strip()
    if not candidate.exists():
        messagebox.showerror('错误', f'未找到模组：{choice}')
        sys.exit(1)
    return candidate


def main():
    if len(sys.argv) > 1:
        mod_path = Path(sys.argv[1])
        if not mod_path.is_absolute():
            mod_path = (Path.cwd() / mod_path).resolve()
    else:
        mod_path = choose_mod_interactively()

    root = tk.Tk()
    app = ModMenuUI(root, mod_path)
    root.mainloop()


if __name__ == '__main__':
    main()
