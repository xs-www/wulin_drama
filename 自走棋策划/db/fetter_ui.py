"""
Fetter 数据库管理 UI
使用 tkinter 创建可视化界面，用于对 fetter 表进行增删查改操作
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json, sys, os
from init_database import import_from_json

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller import FetterControl
from dao import dumpSql, updateDb


class FetterManagerUI:
    """Fetter 管理 UI 类"""

    def __init__(self, root):
        self.root = root
        self.root.title("Fetter 数据库管理")
        self.root.geometry("1000x700")

        # 控制层
        self.control = FetterControl()

        # 创建 UI
        self.create_widgets()

        # 加载数据
        self.refresh_list()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 左侧列表
        list_frame = ttk.LabelFrame(main_frame, text="Fetter 列表", padding="5")
        list_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))

        self.tree = ttk.Treeview(list_frame, columns=("ID", "Variants"), show="headings", height=30)
        self.tree.heading("ID", text="名称 ID")
        self.tree.heading("Variants", text="人数变体 (numofpeople)")
        self.tree.column("ID", width=160)
        self.tree.column("Variants", width=160)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # 右侧按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N), pady=(0, 5))

        ttk.Button(button_frame, text="新建", command=self.create_fetter).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="编辑", command=self.edit_fetter).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="删除", command=self.delete_fetter).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="刷新", command=self.refresh_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="导入 JSON", command=import_from_json).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="导出 JSON", command=self.export_json).pack(side=tk.LEFT, padx=2)

        # 右侧详情
        detail_frame = ttk.LabelFrame(main_frame, text="Fetter 详情", padding="5")
        detail_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)

        self.detail_text = scrolledtext.ScrolledText(detail_frame, width=80, height=30, wrap=tk.WORD)
        self.detail_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def refresh_list(self):
        """刷新羁绊列表，左侧只显示同名羁绊一次，Variants 列显示可用 numofpeople 列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        fetters = self.control.get_all_fetters()
        # fetters expected to be list of dicts with keys: id, numofpeople, description
        grouped = {}
        for f in fetters:
            fid = f.get('id')
            n = f.get('numofpeople')
            if fid is None:
                continue
            grouped.setdefault(fid, []).append(n)

        for fid, nums in grouped.items():
            nums_sorted = sorted([str(x) for x in nums])
            self.tree.insert("", tk.END, values=(fid, ",".join(nums_sorted)))

        # 清空详情
        self.detail_text.delete(1.0, tk.END)

    def on_select(self, event):
        """选择某个羁绊 ID，显示该 ID 下所有变体的完整信息（JSON 列表）"""
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        fid = item['values'][0]

        # 获取所有与该 id 对应的记录
        fetters = self.control.get_all_fetters()
        res = [f for f in fetters if f.get('id') == fid]
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(1.0, json.dumps(res, ensure_ascii=False, indent=2))

    def create_fetter(self):
        """创建新羁绊。注意：Fetter 的主键是 (id, numofpeople)。
        后端如果需要提供自动生成 num 或 id 的接口，请在 new_control/new_service 中实现；
        当前前端要求用户手动填写 id 和 numofpeople。
        """
        dialog = FetterDialog(self.root, "新建 Fetter", control=self.control)
        if dialog.result:
            try:
                res = self.control.insert_fetter(dialog.result)
                if res:
                    self.refresh_list()
                    messagebox.showinfo("成功", "Fetter 创建成功！")
                else:
                    messagebox.showerror("失败", "数据库操作返回失败")
            except Exception as e:
                messagebox.showerror("错误", f"创建失败：{e}")

    def edit_fetter(self):
        """编辑羁绊。因为主键是 (id, numofpeople)，若所选 ID 有多个 numofpeople，需要先选择具体变体。"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先在左侧选择一个 Fetter ID！")
            return
        item = self.tree.item(selection[0])
        fid = item['values'][0]
        variants = str(item['values'][1]).split(',') if item['values'][1] else []

        chosen_num = None
        if len(variants) == 0:
            messagebox.showerror("错误", "未找到该 ID 的任何变体")
            return
        elif len(variants) == 1:
            chosen_num = variants[0]
        else:
            # 弹出选择对话框让用户选择 numofpeople
            vd = VariantSelectDialog(self.root, fid, variants)
            if not vd.result:
                return
            chosen_num = vd.result

        # 获取完整记录
        fetter = self.control.get_fetter_by_id(chosen_num) if False else None
        # 说明：new_control.get_fetter_by_id 接受一个 fetter_id（整型或文本），但在目前的后端实现中
        # get_fetter_by_id 接口是通过传入 numofpeople? 实际上 backend 提供 select_fetter_by_id(fetter_id)
        # 因此这里我们 need to fetch by both id 和 numofpeople. 后端没有提供复合主键查询接口时，前端
        # 通过 get_all_fetters 过滤。下面用通用方式从 get_all_fetters 里筛选。

        all_fetters = self.control.get_all_fetters()
        target = None
        for f in all_fetters:
            if f.get('id') == fid and str(f.get('numofpeople')) == str(chosen_num):
                target = f
                break

        if not target:
            messagebox.showerror("错误", "未能获取到指定的 Fetter 记录，请检查后端接口是否支持按复合主键查询")
            return

        dialog = FetterDialog(self.root, "编辑 Fetter", fetter=target, control=self.control)
        if dialog.result:
            try:
                updates = dialog.result.copy()
                # 必须移除 id 和 numofpeople，因为 update 接口通常以主键参数传入
                if 'id' in updates:
                    del updates['id']
                if 'numofpeople' in updates:
                    del updates['numofpeople']

                # 调用 update_fetter，需要传入复合主键；当前 control.update_fetter 接口定义为 (fetter_id, updates)
                # 这里我们传入一个元组 (id, numofpeople) 作为 fetter_id，后端若未实现，请在后端实现接收复合主键。
                fetter_key = (fid, int(chosen_num))
                try:
                    res = self.control.update_fetter(fetter_key, updates)
                except Exception:
                    # 后端可能只接受单个主键（numor id），降级为走 service 层更新：这里注释说明需要后端支持
                    # TODO: 如果后端未实现接受复合主键，请在 new_control/new_service/new_dao 中实现 update_fetter 支持 (id,numofpeople)
                    res = False

                if res:
                    self.refresh_list()
                    messagebox.showinfo("成功", "Fetter 更新成功！")
                else:
                    messagebox.showerror("失败", f"更新失败：{res}")
            except Exception as e:
                messagebox.showerror("错误", f"更新失败：{e}")

    def delete_fetter(self):
        """删除羁绊，同样需要指定 numofpeople。如果所选 ID 有多个变体，会要求选择具体变体。"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先在左侧选择一个 Fetter ID！")
            return
        item = self.tree.item(selection[0])
        fid = item['values'][0]
        variants = str(item['values'][1]).split(',') if item['values'][1] else []

        chosen_num = None
        if len(variants) == 0:
            messagebox.showerror("错误", "未找到该 ID 的任何变体")
            return
        elif len(variants) == 1:
            chosen_num = variants[0]
        else:
            vd = VariantSelectDialog(self.root, fid, variants, title="请选择要删除的 numofpeople")
            if not vd.result:
                return
            chosen_num = vd.result

        if not messagebox.askyesno("确认", f"确定要删除 Fetter {fid} (numofpeople={chosen_num}) 吗？"):
            return

        try:
            # 同 edit 中的说明，delete_fetter 接口在 control 层接受单个 fetter_id，目前后端实现可能需要调整为复合主键
            # 我们尝试直接调用 delete_fetter，并传入复合主键元组；若后端不支持，请在后端实现支持 (id, numofpeople)
            fetter_key = (fid, int(chosen_num))
            res = self.control.delete_fetter(fetter_key)
            if res:
                self.refresh_list()
                self.detail_text.delete(1.0, tk.END)
                messagebox.showinfo("成功", "Fetter 删除成功！")
            else:
                messagebox.showerror("失败", "删除失败，后端返回 False 或 未实现复合主键删除")
        except Exception as e:
            messagebox.showerror("错误", f"删除失败：{e}")

    def export_json(self):
        try:
            self.control.dumpJson()
            messagebox.showinfo("成功", "JSON 导出成功！")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{e}")


class VariantSelectDialog:
    """用于在同名羁绊有多个 numofpeople 变体时让用户选择具体变体"""

    def __init__(self, parent, fid, variants, title="选择变体"):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        ttk.Label(self.dialog, text=f"Fetter: {fid}").pack(pady=5)
        self.listbox = tk.Listbox(self.dialog)
        for v in variants:
            self.listbox.insert(tk.END, v)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="确定", command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.on_cancel).pack(side=tk.RIGHT)

        self.dialog.wait_window()

    def on_ok(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("警告", "请先选择一个变体")
            return
        self.result = self.listbox.get(sel[0])
        self.dialog.destroy()

    def on_cancel(self):
        self.dialog.destroy()


class FetterDialog:
    """用于创建/编辑单条 Fetter 记录的对话框"""

    def __init__(self, parent, title, fetter: dict = None, control: FetterControl = None):
        self.result = None
        self.control = control if control else FetterControl()

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x360")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 字段：id (文本), numofpeople (int), description (text)
        ttk.Label(main_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.id_entry = ttk.Entry(main_frame, width=40)
        self.id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="numofpeople:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.num_entry = ttk.Entry(main_frame, width=40)
        self.num_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="description:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.desc_text = tk.Text(main_frame, width=60, height=10)
        self.desc_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)

        # 如果是编辑模式，填充现有数据；注意 fetter 可能 来自 get_all_fetters 的一项
        if fetter:
            if 'id' in fetter and fetter['id'] is not None:
                self.id_entry.insert(0, str(fetter['id']))
                # id 为主键的一部分，编辑时设为只读
                try:
                    self.id_entry.state(['readonly'])
                except Exception:
                    self.id_entry.config(state='readonly')
            if 'numofpeople' in fetter and fetter['numofpeople'] is not None:
                self.num_entry.insert(0, str(fetter['numofpeople']))
                try:
                    self.num_entry.state(['readonly'])
                except Exception:
                    self.num_entry.config(state='readonly')
            if 'description' in fetter and fetter['description'] is not None:
                if isinstance(fetter['description'], (dict, list)):
                    self.desc_text.insert(1.0, json.dumps(fetter['description'], ensure_ascii=False, indent=2))
                else:
                    self.desc_text.insert(1.0, str(fetter['description']))

        btn_frame = ttk.Frame(self.dialog, padding="10")
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="确定", command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.on_cancel).pack(side=tk.RIGHT)

        self.dialog.wait_window()

    def on_ok(self):
        try:
            fid = self.id_entry.get().strip()
            num = self.num_entry.get().strip()
            desc = self.desc_text.get(1.0, tk.END).strip()

            if not fid:
                messagebox.showerror("错误", "ID 不能为空！")
                return
            if not num:
                messagebox.showerror("错误", "numofpeople 不能为空！")
                return

            # 尝试将 num 转为 int
            try:
                num_val = int(num)
            except Exception:
                messagebox.showerror("错误", "numofpeople 必须是整数！")
                return

            # 尝试解析 description 为 JSON，如果解析失败则保留为字符串
            desc_val = desc
            try:
                desc_val = json.loads(desc)
            except Exception:
                # 保持原始文本
                pass

            self.result = {
                'id': fid,
                'numofpeople': num_val,
                'description': desc_val
            }
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"数据验证失败：{e}")

    def on_cancel(self):
        self.dialog.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = FetterManagerUI(root)
    root.mainloop()