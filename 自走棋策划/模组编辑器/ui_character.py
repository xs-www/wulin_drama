"""
Character 数据库管理 UI
使用 tkinter 创建可视化界面，用于对 character 表进行增删查改操作
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json, sys, os
from utils import log, effect_parser

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mod_controller import CharacterController, FactionController, SkillController

class CharacterManagerUI:
    """Character 管理 UI 类"""
    
    def __init__(self, root, modid):
        self.root = root
        self.root.title("Character 数据库管理")
        self.root.geometry("1400x800")
        self.modid = modid
        
        # 初始化数据访问对象
        #self.dao = CharacterDao()
        self.controller = CharacterController(modid)

        # 创建 UI 组件
        self.create_widgets()
        
        # 加载数据
        self.refresh_list()
    
    def create_widgets(self):
        """创建 UI 组件"""
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 左侧列表框架
        list_frame = ttk.LabelFrame(main_frame, text="Character 列表", padding="5")
        list_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Character 列表
        self.tree = ttk.Treeview(list_frame, columns=("ID", "Name", "ATK", "HP", "SPD"), show="headings", height=20)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="名称")
        self.tree.heading("ATK", text="攻击力")
        self.tree.heading("HP", text="生命值")
        self.tree.heading("SPD", text="速度")
        
        self.tree.column("ID", width=80)
        self.tree.column("Name", width=120)
        self.tree.column("ATK", width=60)
        self.tree.column("HP", width=60)
        self.tree.column("SPD", width=60)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 右侧按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N), pady=(0, 5))
        
        ttk.Button(button_frame, text="新建", command=self.create_character).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="新增列", command=self.add_column).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="编辑", command=self.edit_character).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="删除", command=self.delete_character).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="刷新", command=self.refresh_list).pack(side=tk.LEFT, padx=2)
        #ttk.Button(button_frame, text="导出 JSON", command=self.export_json).pack(side=tk.LEFT, padx=2)
        
        # 右侧详情框架
        detail_frame = ttk.LabelFrame(main_frame, text="Character 详情", padding="5")
        detail_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
        
        # 详情文本框
        self.detail_text = scrolledtext.ScrolledText(detail_frame, width=60, height=30, wrap=tk.WORD)
        self.detail_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def refresh_list(self):
        """刷新 character 列表"""
        # 清空列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 加载数据
        #characters = self.dao.read_all()
        characters = self.controller.get_all_characters()
        for char in characters:
            self.tree.insert("", tk.END, values=(
                char.get('id', ''),
                char.get('name', ''),
                char.get('attack_power', ''),
                char.get('health_points', ''),
                char.get('speed', '')
            ))
    
    def on_select(self, event):
        """选择 character 时显示详情"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            char_id = item['values'][0]

            # 获取完整数据
            #char = self.dao.read(char_id)
            char = self.controller.get_character_by_id(char_id)
            if char:
                # 显示详情
                self.detail_text.delete(1.0, tk.END)
                self.detail_text.insert(1.0, json.dumps(char, ensure_ascii=False, indent=2))

    def add_column(self):
        d = ColumnDialog(self.root, '新增 Character 列')
        if d.result:
            try:
                self.controller.add_character_column(d.result)
                self.refresh_list()
                messagebox.showinfo('成功', f'新增列 {d.result.get("name")} 成功')
            except Exception as e:
                messagebox.showerror('错误', f'新增列失败：{e}')
    
    def create_character(self):
        """创建新 character"""
        # 获取下一个可用的自增 ID 并传入对话框以便预填充
        dialog = CharacterDialog(self.root, "新建 Character", default_id=None, control=self.controller)
        if dialog.result:
            try:
                #self.dao.create(dialog.result)
                res = self.controller.create_character(dialog.result)
                if res:
                    self.refresh_list()
                    messagebox.showinfo("成功", "Character 创建成功！")
                else:
                    messagebox.showinfo("失败", "数据库操作错误")
            except Exception as e:
                messagebox.showerror("错误", f"创建失败：{str(e)}")
    
    def edit_character(self):
        """编辑 character"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个 Character！")
            return
        
        item = self.tree.item(selection[0])
        char_id = str(item['values'][0])
        
        # 获取完整数据
        #char = self.dao.read(char_id)
        char = self.controller.get_character_by_id(char_id)
        if char:
            dialog = CharacterDialog(self.root, "编辑 Character", char, control=self.controller)
            if dialog.result:
                try:
                    
                    res = self.controller.update_character(dialog.result)
                    if res:
                        self.refresh_list()
                        messagebox.showinfo("成功", "Character 更新成功！")
                    else:
                        messagebox.showinfo("失败", res)
                except Exception as e:
                    messagebox.showerror("错误", f"更新失败：{str(e)}")
    
    def delete_character(self):
        """删除 character"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个 Character！")
            return
        
        item = self.tree.item(selection[0])
        char_id = item['values'][0]
        
        if messagebox.askyesno("确认", f"确定要删除 Character {char_id} 吗？"):
            try:
                self.controller.delete_character(char_id)
                self.refresh_list()
                self.detail_text.delete(1.0, tk.END)
                messagebox.showinfo("成功", "Character 删除成功！")
            except Exception as e:
                messagebox.showerror("错误", f"删除失败：{str(e)}")

class CharacterDialog:
    """Character 编辑对话框"""

    def __init__(self, parent, title, character=None, default_id=None, control: CharacterController = None):
        self.result = None
        self.controller = control if control else CharacterController('default_mod')
        self.modid = self.controller.modid

        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建滚动画布
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 字段定义（静态字段）
        _fields = self.controller.get_default_fields()

        def get_type(field):
            field_dic = {
                'entry':['id', 'name', 'attack_power', 'health_points', 'speed', 'hate_value', 'price', 'energy'],
                # 注意：后端/元数据中可能使用 'faction' 或 'factions'，这里统一识别 'faction'
                'text':['weapon', 'avaliable_location', 'hate_matrix', 'faction', 'factions']
            }
            for t, f in field_dic.items():
                if field in f:
                    return t
            return 'text'

        # 使用后端返回的列顺序，但确保我们包含 faction 字段
        fields = [(field, field, get_type(field)) for field in _fields]
        self.entries = {}

        row = 0
        for field_name, field_label, field_type in fields:
            ttk.Label(scrollable_frame, text=f"{field_label}:").grid(row=row, column=0, sticky=tk.W, pady=2)
            
            if field_type == 'entry':
                entry = ttk.Entry(scrollable_frame, width=50)
                entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
                
                # 如果是编辑模式，填充现有数据
                if character and field_name in character:
                    value = character[field_name]
                    if value is not None:
                        entry.insert(0, str(value))
                    # 如果是编辑模式且为 id 字段，设置为只读，避免修改主键
                    if field_name == 'id':
                        try:
                            entry.state(['readonly'])
                        except Exception:
                            # 退回到通用方式
                            entry.config(state='readonly')
                # 如果是新建模式，且提供了默认 id，则预填充 id 字段
                elif (not character) and field_name == 'id' and default_id is not None:
                    entry.insert(0, str(default_id))

                self.entries[field_name] = entry
            
            elif field_type == 'text':
                # 特殊处理 faction 字段：改为只读文本 + 打开羁绊选择窗口
                if field_name in ('faction', 'factions'):
                     container = ttk.Frame(scrollable_frame)
                     container.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)

                     text_widget = tk.Text(container, width=40, height=4)
                     text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E))
                     container.columnconfigure(0, weight=1)
                     try:
                         text_widget.config(state='disabled')
                     except Exception:
                         pass

                     btn = ttk.Button(container, text='选择羁绊', command=lambda tw=text_widget: self.open_faction_selector(tw))
                     btn.grid(row=0, column=1, padx=5)

                     # 如果是编辑模式，填充现有数据（显示为 JSON）
                     if character and field_name in character:
                         value = character[field_name]
                         if value is not None:
                             if isinstance(value, (list, dict)):
                                 txt = json.dumps(value, ensure_ascii=False, indent=2)
                             else:
                                 txt = str(value)
                             text_widget.config(state='normal')
                             text_widget.delete(1.0, tk.END)
                             text_widget.insert(1.0, txt)
                             text_widget.config(state='disabled')

                     self.entries[field_name] = text_widget
                # 特殊处理技能字段：只读文本 + 打开技能选择窗口（行为类似羁绊选择器）
                elif field_name in ('skill', 'skills'):
                     container = ttk.Frame(scrollable_frame)
                     container.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)

                     text_widget = tk.Text(container, width=40, height=4)
                     text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E))
                     container.columnconfigure(0, weight=1)
                     try:
                         text_widget.config(state='disabled')
                     except Exception:
                         pass

                     btn = ttk.Button(container, text='选择技能', command=lambda tw=text_widget: self.open_skill_selector(tw))
                     btn.grid(row=0, column=1, padx=5)

                     # 如果是编辑模式，填充现有数据（显示为 JSON）
                     if character and field_name in character:
                         value = character[field_name]
                         if value is not None:
                             if isinstance(value, (list, dict)):
                                 txt = json.dumps(value, ensure_ascii=False, indent=2)
                             else:
                                 txt = str(value)
                             text_widget.config(state='normal')
                             text_widget.delete(1.0, tk.END)
                             text_widget.insert(1.0, txt)
                             text_widget.config(state='disabled')

                     self.entries[field_name] = text_widget
                # 特殊处理仇恨偏好矩阵：只读文本 + 打开 3x3 编辑窗口
                elif field_name == 'hate_matrix':
                    container = ttk.Frame(scrollable_frame)
                    container.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)

                    text_widget = tk.Text(container, width=40, height=4)
                    text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E))
                    container.columnconfigure(0, weight=1)
                    try:
                        text_widget.config(state='disabled')
                    except Exception:
                        pass

                    btn = ttk.Button(container, text='编辑仇恨表', command=lambda tw=text_widget: self.open_hate_matrix_editor(tw))
                    btn.grid(row=0, column=1, padx=5)

                    # 如果是编辑模式，填充现有数据（显示为 JSON）
                    if character and field_name in character:
                        value = character[field_name]
                        if value is not None:
                            if isinstance(value, (list, dict)):
                                txt = json.dumps(value, ensure_ascii=False, indent=2)
                            else:
                                txt = str(value)
                            text_widget.config(state='normal')
                            text_widget.delete(1.0, tk.END)
                            text_widget.insert(1.0, txt)
                            text_widget.config(state='disabled')

                    self.entries[field_name] = text_widget
                else:
                    text_widget = tk.Text(scrollable_frame, width=50, height=4)
                    text_widget.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
                    
                    # 如果是编辑模式，填充现有数据
                    if character and field_name in character:
                        value = character[field_name]
                        if value is not None:
                            if isinstance(value, (list, dict)):
                                text_widget.insert(1.0, json.dumps(value, ensure_ascii=False, indent=2))
                            else:
                                text_widget.insert(1.0, str(value))
                    
                    self.entries[field_name] = text_widget
            
            row += 1
        
        scrollable_frame.columnconfigure(1, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 按钮框架
        button_frame = ttk.Frame(self.dialog, padding="10")
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="确定", command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.on_cancel).pack(side=tk.RIGHT)
        
        # 等待窗口关闭
        self.dialog.wait_window()
    
    def on_ok(self):
        """确定按钮处理"""
        try:
            result = {}
            
            for field_name, widget in self.entries.items():
                if isinstance(widget, tk.Text):
                    raw = widget.get(1.0, tk.END).strip()
                else:
                    raw = widget.get().strip()
                
                # 跳过空值
                if not raw:
                    continue

                value = raw
                # 对 Text 字段，尝试解析为 JSON（优先返回结构化类型）
                if isinstance(widget, tk.Text):
                    try:
                        parsed = json.loads(raw)
                        # 如果解析得到的是列表/字典/数值/布尔，采用解析结果
                        if isinstance(parsed, (list, dict, int, float, bool)):
                            value = parsed
                        else:
                            # 字符串类型的 JSON（带引号）也保持为原始字符串
                            value = parsed if isinstance(parsed, str) and parsed != '' else raw
                    except Exception:
                        # 解析失败则保持原始字符串
                        value = raw
                else:
                    # 非 Text 字段：尝试根据字段名转换为整数（数字字段）
                    if field_name in ['attack_power', 'health_points', 'speed', 'hate_value', 'price', 'energy']:
                        try:
                            value = int(raw)
                        except Exception:
                            value = raw
                    else:
                        value = raw
                
                result[field_name] = value
            
            if not result.get('id'):
                messagebox.showerror("错误", "ID 不能为空！")
                return
            
            if not result.get('name'):
                messagebox.showerror("错误", "Name 不能为空！")
                return
            
            self.result = result
            self.dialog.destroy()
        
        except Exception as e:
            messagebox.showerror("错误", f"数据验证失败：{str(e)}")
    
    def on_cancel(self):
        """取消按钮处理"""
        self.dialog.destroy()

    def open_faction_selector(self, text_widget: tk.Text):
        """打开羁绊选择对话框，并把用户确认的预览写回到 faction 文本框（只写入 JSON 列表）"""
        # 解析当前已存在的 faction 内容作为初始选择
        current = []
        try:
            text_widget.config(state='normal')
            raw = text_widget.get(1.0, tk.END).strip()
            text_widget.config(state='disabled')
            if raw:
                try:
                    current = json.loads(raw)
                except Exception:
                    # 如果不是 JSON，则尝试按行或逗号分割
                    current = [s.strip() for s in raw.split(',') if s.strip()]
        except Exception:
            current = []

        dlg = FactionSelectorDialog(self.dialog, current, modid=self.modid)
        if dlg.result is not None:
            sel = dlg.result
            # 将选择结果写入只读文本框
            txt = json.dumps(sel, ensure_ascii=False, indent=2)
            text_widget.config(state='normal')
            text_widget.delete(1.0, tk.END)
            text_widget.insert(1.0, txt)
            text_widget.config(state='disabled')

    def open_skill_selector(self, text_widget: tk.Text):
        """打开技能选择对话框，并把用户确认的选择写回到文本框（JSON 列表或字符串）"""
        current = []
        try:
            text_widget.config(state='normal')
            raw = text_widget.get(1.0, tk.END).strip()
            text_widget.config(state='disabled')
            if raw:
                try:
                    current = json.loads(raw)
                except Exception:
                    current = [s.strip() for s in raw.split(',') if s.strip()]
        except Exception:
            current = []

        dlg = SkillSelectorDialog(self.dialog, current, modid=self.modid)
        if dlg.result is not None:
            sel = dlg.result
            txt = json.dumps(sel, ensure_ascii=False, indent=2)
            text_widget.config(state='normal')
            text_widget.delete(1.0, tk.END)
            text_widget.insert(1.0, txt)
            text_widget.config(state='disabled')

class ColumnDialog:
    """用于输入新列信息的对话框"""
    def __init__(self, parent, title):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        frame = ttk.Frame(self.dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text='列名 (name, 英文):').grid(row=0, column=0, sticky=tk.W)
        self.col_entry = ttk.Entry(frame, width=40)
        self.col_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='数据类型 (type):').grid(row=1, column=0, sticky=tk.W)
        self.type_entry = ttk.Entry(frame, width=40)
        self.type_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='默认值 (default, 可选):').grid(row=2, column=0, sticky=tk.W)
        self.default_entry = ttk.Entry(frame, width=40)
        self.default_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text='确定', command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text='取消', command=self.on_cancel).pack(side=tk.RIGHT)

        self.dialog.wait_window()

    def on_ok(self):
        col = self.col_entry.get().strip()
        type_ = self.type_entry.get().strip()
        default = self.default_entry.get().strip()
        if not col:
            messagebox.showerror('错误', '列名不能为空')
            return
        if not type_:
            messagebox.showerror('错误', '数据类型不能为空')
            return
        self.result = {'name': col, 'type': type_, 'default': default or None}
        self.dialog.destroy()

    def on_cancel(self):
        self.dialog.destroy()


class FactionSelectorDialog:
    """选择羁绊的对话框：左上为羁绊列表（同名只出现一次），右上为选中羁绊详情，双击列表项切换选中状态，下方为已选羁绊预览（JSON）。"""

    def __init__(self, parent, initial_selected=None, title='选择羁绊', modid='default_mod'):
        self.result = None
        self.controller = FactionController(modid=modid)

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry('800x600')
        self.dialog.transient(parent)
        self.dialog.grab_set()

        main = ttk.Frame(self.dialog, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        top_frame = ttk.Frame(main)
        top_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧羁绊列表
        left = ttk.LabelFrame(top_frame, text='羁绊 列表')
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))

        self.tree = ttk.Treeview(left, columns=('ID','Variants'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Variants', text='numofpeople')
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double)

        lscroll = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.tree.yview)
        lscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=lscroll.set)

        # 右侧详情
        right = ttk.LabelFrame(top_frame, text='羁绊 信息')
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.info_text = scrolledtext.ScrolledText(right, width=40, height=10)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.config(state='disabled')

        # 下方预览
        preview_frame = ttk.LabelFrame(main, text='已选择羁绊 预览 (JSON)')
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(5,0))
        self.preview = scrolledtext.ScrolledText(preview_frame, height=8)
        self.preview.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(5,0))
        ttk.Button(btn_frame, text='确定', command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text='取消', command=self.on_cancel).pack(side=tk.RIGHT)

        # load data
        self.selected = set(initial_selected or [])
        self._load_factions()
        self._refresh_preview()

        self.dialog.wait_window()

    def _load_factions(self):
        all_f = self.controller.get_all_factions()
        grouped = {}
        for f in all_f:
            fid = f.get('id')
            n = ','.join(f.get('effects', {}).keys()) if f.get('effects') else ''
            if fid is None:
                continue
            grouped.setdefault(fid, []).append(n)

        for fid, nums in grouped.items():
            nums_sorted = sorted([str(x) for x in nums])
            iid = self.tree.insert('', tk.END, values=(fid, ','.join(nums_sorted)))
            if fid in self.selected:
                self.tree.item(iid, tags=('selected',))

        self.tree.tag_configure('selected', background='#c6f7d0')

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        fid = item['values'][0]
        # show details for this fid
        faction_dict = self.controller.get_faction_by_id(fid)
        faction_dict['effects'] = self.controller.gen_description(faction_dict.get('effects', {}))
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, json.dumps(faction_dict, ensure_ascii=False, indent=2))
        self.info_text.config(state='disabled')

    def on_double(self, event):
        # toggle selection for double-clicked item
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        item = self.tree.item(item_id)
        fid = item['values'][0]
        if fid in self.selected:
            self.selected.remove(fid)
            self.tree.item(item_id, tags=())
        else:
            self.selected.add(fid)
            self.tree.item(item_id, tags=('selected',))
            self.tree.tag_configure('selected', background='#c6f7d0')
        self._refresh_preview()

    def _refresh_preview(self):
        arr = list(self.selected)
        self.preview.delete(1.0, tk.END)
        self.preview.insert(1.0, json.dumps(arr, ensure_ascii=False, indent=2))

    def on_ok(self):
        self.result = list(self.selected)
        self.dialog.destroy()

    def on_cancel(self):
        self.dialog.destroy()

class SkillSelectorDialog:
    """选择技能的对话框：左侧技能列表，右侧技能详情，下方为已选预览（支持多选，双击切换）。"""
    def __init__(self, parent, initial_selected=None, title='选择技能', modid='default_mod'):
        self.result = None
        self.controller = SkillController(modid=modid)

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry('700x520')
        self.dialog.transient(parent)
        self.dialog.grab_set()

        main = ttk.Frame(self.dialog, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        top_frame = ttk.Frame(main)
        top_frame.pack(fill=tk.BOTH, expand=True)

        left = ttk.LabelFrame(top_frame, text='技能 列表')
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))

        self.tree = ttk.Treeview(left, columns=('ID','Name'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='名称')
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double)

        lscroll = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.tree.yview)
        lscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=lscroll.set)

        right = ttk.LabelFrame(top_frame, text='技能 信息')
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.info_text = scrolledtext.ScrolledText(right, width=40, height=10)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        self.info_text.config(state='disabled')

        preview_frame = ttk.LabelFrame(main, text='已选择 技能 预览 (JSON)')
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(5,0))
        self.preview = scrolledtext.ScrolledText(preview_frame, height=8)
        self.preview.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(5,0))
        ttk.Button(btn_frame, text='确定', command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text='取消', command=self.on_cancel).pack(side=tk.RIGHT)

        # load data
        self.selected = set(initial_selected or [])
        self._load_skills()
        self._refresh_preview()

        self.dialog.wait_window()

    def _load_skills(self):
        all_s = self.controller.get_all_skills() or []
        for s in all_s:
            sid = s.get('id')
            name = s.get('name','')
            iid = self.tree.insert('', tk.END, values=(sid, name))
            if sid in self.selected:
                self.tree.item(iid, tags=('selected',))
        self.tree.tag_configure('selected', background='#c6f7d0')

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        sid = item['values'][0]
        skill = self.controller.get_skill_by_id(sid)
        if skill:
            self.info_text.config(state='normal')
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, json.dumps(skill, ensure_ascii=False, indent=2))
            self.info_text.config(state='disabled')

    def on_double(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        item = self.tree.item(item_id)
        sid = item['values'][0]
        if sid in self.selected:
            self.selected.remove(sid)
            self.tree.item(item_id, tags=())
        else:
            self.selected.add(sid)
            self.tree.item(item_id, tags=('selected',))
            self.tree.tag_configure('selected', background='#c6f7d0')
        self._refresh_preview()

    def _refresh_preview(self):
        arr = list(self.selected)
        self.preview.delete(1.0, tk.END)
        self.preview.insert(1.0, json.dumps(arr, ensure_ascii=False, indent=2))

    def on_ok(self):
        self.result = list(self.selected)
        self.dialog.destroy()

    def on_cancel(self):
        self.dialog.destroy()


class HateBiasMatrixDialog:
    """编辑 3x3 仇恨偏好矩阵的对话框，返回 3x3 的嵌套列表"""

    def __init__(self, parent, initial_matrix=None, title='编辑仇恨偏好矩阵'):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry('320x280')
        self.dialog.transient(parent)
        self.dialog.grab_set()

        main = ttk.Frame(self.dialog, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        # prepare initial matrix as 3x3 list
        im = initial_matrix if isinstance(initial_matrix, list) else None
        # 默认值为 1.0（float）
        matrix = [[1.0 for _ in range(3)] for _ in range(3)]
        try:
            if im and len(im) == 3 and all(isinstance(r, list) and len(r) == 3 for r in im):
                for i in range(3):
                    for j in range(3):
                        try:
                            matrix[i][j] = float(im[i][j])
                        except Exception:
                            # 如果无法解析为 float，保留默认 1.0
                            matrix[i][j] = 1.0
        except Exception:
            pass

        self.entries = [[None]*3 for _ in range(3)]
        grid_frame = ttk.Frame(main)
        grid_frame.pack(pady=5)
        # 列头：目标1..3
        for j in range(3):
            ttk.Label(grid_frame, text=f'目标{j+1}').grid(row=0, column=j+1, padx=4, pady=2)
        # 行头：前中后排
        row_labels = ['前排', '中排', '后排']
        for i in range(3):
            ttk.Label(grid_frame, text=row_labels[i]).grid(row=i+1, column=0, padx=4, pady=4)
            for j in range(3):
                e = ttk.Entry(grid_frame, width=6)
                e.grid(row=i+1, column=j+1, padx=4, pady=4)
                e.insert(0, str(matrix[i][j]))
                self.entries[i][j] = e

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(10,0))
        ttk.Button(btn_frame, text='保存', command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text='取消', command=self.on_cancel).pack(side=tk.RIGHT)

        self.dialog.wait_window()

    def on_ok(self):
        try:
            mat = []
            for i in range(3):
                row = []
                for j in range(3):
                    v = self.entries[i][j].get().strip()
                    try:
                        fv = float(v)
                    except Exception:
                        fv = 1.0
                    row.append(fv)
                mat.append(row)
            self.result = mat
            self.dialog.destroy()
        except Exception:
            messagebox.showerror('错误', '矩阵数据无效')

    def on_cancel(self):
        self.dialog.destroy()


    # 在 CharacterDialog 中使用此对话框时，会把返回的矩阵以 JSON 写回到只读文本框
    
    def __repr__(self):
        return '<HateBiasMatrixDialog>'
