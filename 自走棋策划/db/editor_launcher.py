"""
Editor Launcher - 打开不同管理界面
"""
import tkinter as tk
from tkinter import ttk
import os, sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from character_ui import CharacterManagerUI
#from keywords_ui import KeywordManagerUI
#from event_ui import EventManagerUI
from fetter_ui import FetterManagerUI

from dao import updateDb, dumpSql

class EditorLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title('管理器启动器')
        self.root.geometry('400x200')
        frame = ttk.Frame(root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Button(frame, text='打开 Character 管理', command=self.open_character).pack(fill=tk.X, pady=5)
        ttk.Button(frame, text='打开 Fetter 管理', command=self.open_fetter).pack(fill=tk.X, pady=5)
        #ttk.Button(frame, text='打开 Event 管理', command=self.open_event).pack(fill=tk.X, pady=5)

    def open_character(self):
        win = tk.Toplevel(self.root)
        CharacterManagerUI(win)

    def open_fetter(self):
        win = tk.Toplevel(self.root)
        FetterManagerUI(win)

    def open_event(self):
        win = tk.Toplevel(self.root)
        #EventManagerUI(win)


def main():
    # 确保数据库表已创建
    try:
        updateDb()
    except Exception:
        pass

    root = tk.Tk()
    EditorLauncher(root)

    # 关闭窗口时导出 SQL
    def on_closing():
        print("正在导出数据库到 SQL 文件...")
        dumpSql()
        print("SQL 导出完成。")
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()


if __name__ == '__main__':
    main()
