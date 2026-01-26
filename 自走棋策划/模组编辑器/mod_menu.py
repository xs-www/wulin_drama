#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import subprocess
import sys, os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json

from ui_character import CharacterManagerUI
from ui_faction import FactionManagerUI
from ui_skill import SkillManagerUI
from ui_trigger import TriggerManagerUI
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
    def __init__(self, root, mod_controller_or_path):
        self.root = root
        # 支持传入 ModController 对象或 Path/字符串
        if hasattr(mod_controller_or_path, 'get_mod_path'):
            self.controller = mod_controller_or_path
            try:
                self.mod_path = self.controller.get_mod_path()
            except Exception:
                # 尝试从 controller 的 modid 推断路径
                self.mod_path = SCRIPT_DIR / 'mods' / getattr(self.controller, 'modid', '')
            self.modid = getattr(self.controller, 'modid', self.mod_path.name)
        else:
            self.controller = None
            self.mod_path = Path(mod_controller_or_path)
            self.modid = self.mod_path.name

        root.title(f'模组：{self.modid}')
        root.geometry('900x600')

        main = ttk.Frame(root, padding=8)
        main.pack(fill='both', expand=True)

        # 左侧：显示 manifest.json 内容（可编辑）
        left = ttk.LabelFrame(main, text='manifest.json', padding=6)
        left.pack(side='left', fill='both', expand=True)

        text_frame = ttk.Frame(left)
        text_frame.pack(fill='both', expand=True)

        self.manifest_text = tk.Text(text_frame, wrap='none')
        self.manifest_text.pack(side='left', fill='both', expand=True)
        vsb = ttk.Scrollbar(text_frame, orient='vertical', command=self.manifest_text.yview)
        vsb.pack(side='left', fill='y')
        hsb = ttk.Scrollbar(left, orient='horizontal', command=self.manifest_text.xview)
        hsb.pack(side='bottom', fill='x')
        self.manifest_text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        mf_btn_frame = ttk.Frame(left)
        mf_btn_frame.pack(fill=tk.X, pady=6)
        ttk.Button(mf_btn_frame, text='刷新 manifest', command=self.load_manifest_to_text).pack(side=tk.LEFT, padx=4)
        ttk.Button(mf_btn_frame, text='保存 manifest', command=self.save_manifest_from_text).pack(side=tk.LEFT, padx=4)
        ttk.Button(mf_btn_frame, text='在文件中打开', command=self.open_manifest_file).pack(side=tk.LEFT, padx=4)

        # 右侧：工具按钮（保留原有功能入口）
        right = ttk.Frame(main, width=220)
        right.pack(side='right', fill='y')

        btn_role = ttk.Button(right, text='管理角色', command=self.open_character_editor)
        btn_role.pack(fill='x', pady=6)

        btn_faction = ttk.Button(right, text='管理羁绊', command=self.open_faction_editor)
        btn_faction.pack(fill='x', pady=6)

        btn_skills = ttk.Button(right, text='管理技能', command=self.open_skills_editor)
        btn_skills.pack(fill='x', pady=6)

        btn_events = ttk.Button(right, text='管理触发器事件', command=self.open_trigger_manager)
        btn_events.pack(fill='x', pady=6)

        btn_buff = ttk.Button(right, text='管理 Buff', command=self.open_buff_editor)
        btn_buff.pack(fill='x', pady=6)

        btn_cfg = ttk.Button(right, text='打开 manifest 文件夹', command=self.open_manifest_folder)
        btn_cfg.pack(fill='x', pady=6)

        btn_open = ttk.Button(right, text='打开模组文件夹', command=self.open_folder)
        btn_open.pack(fill='x', pady=6)

        btn_refresh = ttk.Button(right, text='刷新界面', command=self.refresh)
        btn_refresh.pack(fill='x', pady=6)

        btn_export = ttk.Button(right, text='导出模组', command=self.export_mod)
        btn_export.pack(fill='x', pady=6)

        self.status = tk.StringVar()
        statusbar = ttk.Label(root, textvariable=self.status, relief='sunken', anchor='w')
        statusbar.pack(side='bottom', fill='x')
        self.set_status('就绪')

        # 初次加载 manifest
        self.load_manifest_to_text()

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

    def load_manifest_to_text(self):
        mf = self.mod_path / 'manifest.json'
        if mf.exists():
            try:
                with open(mf, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                s = json.dumps(data, ensure_ascii=False, indent=2)
            except Exception:
                try:
                    s = mf.read_text(encoding='utf-8')
                except Exception:
                    s = '{}'
        else:
            s = '{}'
        self.manifest_text.delete(1.0, tk.END)
        self.manifest_text.insert(1.0, s)
        self.set_status('manifest 已加载')

    def save_manifest_from_text(self):
        raw = self.manifest_text.get(1.0, tk.END).strip()
        if not raw:
            messagebox.showerror('错误', 'manifest 内容为空，无法保存')
            return
        try:
            parsed = json.loads(raw)
        except Exception as e:
            messagebox.showerror('错误', f'manifest 不是合法 JSON：{e}')
            return
        mf = self.mod_path / 'manifest.json'
        try:
            mf.parent.mkdir(parents=True, exist_ok=True)
            with open(mf, 'w', encoding='utf-8') as f:
                json.dump(parsed, f, ensure_ascii=False, indent=2)
            self.set_status('manifest 已保存')
            messagebox.showinfo('成功', 'manifest 保存成功')
        except Exception as e:
            messagebox.showerror('错误', f'保存失败：{e}')
            log.console(f'保存 manifest 失败：{e}', 'ERROR')

    def open_manifest_file(self):
        mf = self.mod_path / 'manifest.json'
        if not mf.exists():
            if messagebox.askyesno('创建', '未找到 manifest.json，是否创建？'):
                try:
                    mf.parent.mkdir(parents=True, exist_ok=True)
                    mf.write_text('{}', encoding='utf-8')
                except Exception as e:
                    messagebox.showerror('错误', f'无法创建 manifest：{e}')
                    return
            else:
                return
        self.open_or_prompt(mf)

    def open_manifest_folder(self):
        self.open_or_prompt(self.mod_path)

    def open_character_editor(self):
        win = tk.Toplevel(self.root)
        CharacterManagerUI(win, modid=self.modid)

    def open_faction_editor(self):
        win = tk.Toplevel(self.root)
        FactionManagerUI(win, modid=self.modid)

    def open_skills_editor(self):
        win = tk.Toplevel(self.root)
        SkillManagerUI(win, modid=self.modid)

    def open_trigger_manager(self):
        win = tk.Toplevel(self.root)
        TriggerManagerUI(win, modid=self.modid)

    def open_buff_editor(self):
        from ui_buff import BuffManagerUI
        win = tk.Toplevel(self.root)
        BuffManagerUI(win, modid=self.modid)

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
        # 仅刷新 manifest 内容与状态
        self.load_manifest_to_text()
        self.set_status('已刷新')

    def export_mod(self):
        if self.controller:
            res = self.controller.export_mod()
        else:
            # 尝试用 ModController 导出（若可用）
            try:
                mc = ModController(self.mod_path)
                res = mc.export_mod()
            except Exception as e:
                messagebox.showerror('错误', f'无法导出模组：{e}')
                log.console(f'导出失败：{e}', 'ERROR')
                return
        if res:
            messagebox.showinfo('导出成功', f'模组已导出到：{res}')
            self.set_status(f'模组已导出到：{res}')
        else:
            messagebox.showerror('导出失败', '模组导出失败，请查看日志获取更多信息。')
            self.set_status('模组导出失败。')


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
