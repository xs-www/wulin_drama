"""
Character 数据库管理 UI
使用 tkinter 创建可视化界面，用于对 character 表进行增删查改操作
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from dao import CharacterDao, updateDb, dumpSql, dumpJson


class CharacterManagerUI:
    """Character 管理 UI 类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Character 数据库管理")
        self.root.geometry("1000x700")
        
        # 初始化数据访问对象
        self.dao = CharacterDao()
        
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
        ttk.Button(button_frame, text="编辑", command=self.edit_character).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="删除", command=self.delete_character).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="刷新", command=self.refresh_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="导出 JSON", command=self.export_json).pack(side=tk.LEFT, padx=2)
        
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
        characters = self.dao.read_all()
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
            char_id = str(item['values'][0]).rjust(4, '0')
            
            # 获取完整数据
            char = self.dao.read(char_id)
            if char:
                # 显示详情
                self.detail_text.delete(1.0, tk.END)
                self.detail_text.insert(1.0, json.dumps(char, ensure_ascii=False, indent=2))
    
    def create_character(self):
        """创建新 character"""
        # 获取下一个可用的自增 ID 并传入对话框以便预填充
        next_id = self.dao.get_next_id()
        dialog = CharacterDialog(self.root, "新建 Character", default_id=next_id)
        if dialog.result:
            try:
                self.dao.create(dialog.result)
                self.refresh_list()
                messagebox.showinfo("成功", "Character 创建成功！")
            except Exception as e:
                messagebox.showerror("错误", f"创建失败：{str(e)}")
    
    def edit_character(self):
        """编辑 character"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个 Character！")
            return
        
        item = self.tree.item(selection[0])
        char_id = str(item['values'][0]).rjust(4, '0')
        
        # 获取完整数据
        char = self.dao.read(char_id)
        print("编辑 Character:", char)
        if char:
            dialog = CharacterDialog(self.root, "编辑 Character", char)
            if dialog.result:
                try:
                    # 移除 id 字段，因为 update 方法中 id 是作为参数传入的
                    update_data = dialog.result.copy()
                    if 'id' in update_data:
                        del update_data['id']
                    
                    self.dao.update(char_id, update_data)
                    self.refresh_list()
                    messagebox.showinfo("成功", "Character 更新成功！")
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
                self.dao.delete(char_id)
                self.refresh_list()
                self.detail_text.delete(1.0, tk.END)
                messagebox.showinfo("成功", "Character 删除成功！")
            except Exception as e:
                messagebox.showerror("错误", f"删除失败：{str(e)}")
    
    def export_json(self):
        """导出 JSON"""
        try:
            dumpJson()
            messagebox.showinfo("成功", "JSON 导出成功！")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")


class CharacterDialog:
    """Character 编辑对话框"""
    
    def __init__(self, parent, title, character=None, default_id=None):
        self.result = None
        
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
        
        # 字段定义
        fields = [
            ('id', 'ID', 'entry'),
            ('name', '名称 Name', 'entry'),
            ('localization', '本地化 Localization', 'entry'),
            ('attack_power', '攻击力 Attack Power', 'entry'),
            ('health_points', '生命值 Health Points', 'entry'),
            ('speed', '速度 Speed', 'entry'),
            ('hate_value', '仇恨值 Hate Value', 'entry'),
            ('price', '价格 Price', 'entry'),
            ('weapon', '武器 Weapon', 'entry'),
            ('energy', '能量 Energy', 'entry'),
            ('avaliable_location', '可用位置 Available Location (JSON)', 'text'),
            ('fetter', '羁绊 Fetter (JSON)', 'text'),
            ('hate_matrix', '仇恨矩阵 Hate Matrix (JSON)', 'text'),
        ]
        
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
                    entry.insert(0, str(default_id).rjust(4, '0'))
                
                self.entries[field_name] = entry
            
            elif field_type == 'text':
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
                    value = widget.get(1.0, tk.END).strip()
                else:
                    value = widget.get().strip()
                
                # 跳过空值
                if not value:
                    continue
                
                # 对于 JSON 字段，尝试解析
                if field_name in ['avaliable_location', 'fetter', 'hate_matrix']:
                    try:
                        value = json.loads(value)
                    except:
                        pass
                
                # 对于数字字段，转换为整数
                elif field_name in ['attack_power', 'health_points', 'speed', 'hate_value', 'price', 'energy']:
                    try:
                        value = int(value)
                    except:
                        pass
                
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


def main():
    """主函数"""
    # 启动前更新数据库
    print("正在从 SQL 文件更新数据库...")
    updateDb()
    print("数据库更新完成。")
    
    # 创建主窗口
    root = tk.Tk()
    app = CharacterManagerUI(root)
    
    # 关闭窗口时导出 SQL
    def on_closing():
        print("正在导出数据库到 SQL 文件...")
        dumpSql()
        print("SQL 导出完成。")
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 运行主循环
    root.mainloop()


if __name__ == '__main__':
    main()
