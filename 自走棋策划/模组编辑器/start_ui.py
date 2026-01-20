#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import tkinter as tk
from mod_manager_ui import ModManagerUI, ensure_mods_dir
from 自走棋策划.模组编辑器.utils import log


def main():
    ensure_mods_dir()
    root = tk.Tk()
    app = ModManagerUI(root)
    root.mainloop()


if __name__ == '__main__':
    print("正在启动模组管理器...")
    main()
    try:
        log.saveLog()
    except Exception:
        pass
    print("模组管理器已关闭.")