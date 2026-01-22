"""
Faction 数据库管理 UI
使用 tkinter 创建可视化界面，用于对 faction 表进行增删查改操作
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json, sys, os
import copy

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mod_controller import FactionController
from utils import effect_parser

class FactionManagerUI:
    """Faction 管理 UI 类"""

    def __init__(self, root, modid):
        self.root = root
        self.root.title("Faction 数据库管理")
        self.root.geometry("1000x700")

        # 控制层
        self.modid = modid
        self.controller = FactionController(modid)

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
        list_frame = ttk.LabelFrame(main_frame, text="Faction 列表", padding="5")
        list_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))

        self.tree = ttk.Treeview(list_frame, columns=("ID", "Variants"), show="headings", height=30)
        self.tree.heading("ID", text="名称 ID")
        self.tree.heading("Variants", text="人数变体")
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

        ttk.Button(button_frame, text="新建", command=self.create_faction).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="编辑", command=self.edit_faction).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="删除", command=self.delete_faction).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="刷新", command=self.refresh_list).pack(side=tk.LEFT, padx=2)
        #ttk.Button(button_frame, text="导入 JSON", command=import_from_json).pack(side=tk.LEFT, padx=2)
        #ttk.Button(button_frame, text="导出 JSON", command=self.export_json).pack(side=tk.LEFT, padx=2)

        # 右侧详情（分块显示）
        detail_frame = ttk.LabelFrame(main_frame, text="Faction 详情", padding="5")
        detail_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(1, weight=1)

        # 右上：基本信息区（ID / 名称 / 描述）
        info_frame = ttk.Frame(detail_frame)
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        info_frame.columnconfigure(1, weight=1)

        ttk.Label(info_frame, text='ID:').grid(row=0, column=0, sticky=tk.W, padx=(0,6))
        self.id_label = ttk.Label(info_frame, text='')
        self.id_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Button(info_frame, text='修改', command=lambda: self.on_edit_field('id')).grid(row=0, column=2, padx=6)

        ttk.Label(info_frame, text='名称:').grid(row=1, column=0, sticky=tk.W, padx=(0,6))
        self.name_label = ttk.Label(info_frame, text='')
        self.name_label.grid(row=1, column=1, sticky=(tk.W, tk.E))
        ttk.Button(info_frame, text='修改', command=lambda: self.on_edit_field('name')).grid(row=1, column=2, padx=6)

        ttk.Label(info_frame, text='描述:').grid(row=2, column=0, sticky=tk.NW, padx=(0,6), pady=(6,0))
        self.desc_label = tk.Text(info_frame, height=4, wrap=tk.WORD)
        self.desc_label.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(6,0))
        self.desc_label.config(state='disabled')
        ttk.Button(info_frame, text='修改', command=lambda: self.on_edit_field('description')).grid(row=2, column=2, padx=6, pady=(6,0))

        # 右下：effects 区（门槛与对应效果列表）
        effects_frame = ttk.LabelFrame(detail_frame, text='效果列表（按门槛）', padding=6)
        effects_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(8,0))
        effects_frame.columnconfigure(0, weight=1)
        #effects_frame.rowconfigure(0, weight=1)
        # 顶部操作栏不应被拉伸，设置第0行为固定高度，第1行为可伸缩
        effects_frame.rowconfigure(0, weight=0)
        effects_frame.rowconfigure(1, weight=1)

        # 顶部操作栏
        ops_frame = ttk.Frame(effects_frame, padding=0)
        ops_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        # 去掉按钮的垂直内外间距，缩短栏高度
        ttk.Button(ops_frame, text='添加门槛', command=self.on_add_threshold).pack(side=tk.LEFT, padx=4, pady=0)
        ttk.Button(ops_frame, text='保存', command=self.save_current_composite).pack(side=tk.LEFT, padx=4, pady=0)
        # 全局生成描述按钮（为所有门槛尝试自动生成描述）
        ttk.Button(ops_frame, text='生成描述', command=self.on_generate_all_descriptions).pack(side=tk.LEFT, padx=4, pady=0)

        # 滚动区域，显示门槛条目
        self.threshold_canvas = tk.Canvas(effects_frame)
        self.threshold_canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        th_scroll = ttk.Scrollbar(effects_frame, orient=tk.VERTICAL, command=self.threshold_canvas.yview)
        th_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.threshold_canvas.configure(yscrollcommand=th_scroll.set)

        self.threshold_inner = ttk.Frame(self.threshold_canvas)
        self.threshold_canvas.create_window((0,0), window=self.threshold_inner, anchor='nw')
        self.threshold_inner.bind('<Configure>', lambda e: self.threshold_canvas.configure(scrollregion=self.threshold_canvas.bbox('all')))

        # 当前复合数据
        self.current_composite = None

    def refresh_list(self):
        """刷新羁绊列表，左侧只显示同名羁绊一次，Variants 列显示可用 numofpeople 列表
        现在直接从每个羁绊的 composite.effects 中读取可用人数变体（keys）。"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 先拿到所有原始记录以获取 ID 列表及备用的 name
        records = self.controller.get_all_factions() or []
        ids = []
        backup_name = {}
        for r in records:
            fid = r.get('id')
            if not fid:
                continue
            if fid not in ids:
                ids.append(fid)
            if fid not in backup_name:
                backup_name[fid] = r.get('name') or fid

        # 对每个 id 获取复合结构并从 effects 字典读取变体 keys
        for fid in ids:
            comp = None
            try:
                comp = self.controller.get_faction_by_id(fid) or {}
            except Exception:
                comp = {}
            display_name = comp.get('name') or backup_name.get(fid, fid)
            effects = comp.get('effects') or {}
            nums = []
            if isinstance(effects, dict):
                # 按数字升序排序，非数字按字符串顺序
                try:
                    nums = sorted([str(k) for k in effects.keys()], key=lambda x: int(x) if str(x).isdigit() else x)
                except Exception:
                    nums = sorted([str(k) for k in effects.keys()])
            # 回退：若 effects 为空，则尝试从原始 records 中收集 numofpeople
            if not nums:
                nums = [str(r.get('numofpeople')) for r in records if r.get('id') == fid and r.get('numofpeople') is not None]
                nums = sorted(list(set(nums)), key=lambda x: int(x) if str(x).isdigit() else x)

            self.tree.insert("", tk.END, values=(display_name, ",".join(nums), fid))

        # 清空详情
        # self.detail_text.delete(1.0, tk.END)

    def on_select(self, event):
        """选择某个羁绊 ID，显示该 ID 下所有变体的完整信息（JSON 列表）"""
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        # 值格式为 (display_name, nums_str, fid)
        if len(item['values']) >= 3:
            fid = item['values'][2]
        else:
            fid = item['values'][0]

        # 获取所有与该 id 对应的记录
        #faction = self.controller.get_faction_by_id(fid)

        # 生成复合结构: id, name, description (taken from first), effects: {num: [effects...]}
        # composite = faction.copy()

        # 存储当前复合数据并渲染到右侧面板
        self.current_composite = self.controller.get_faction_by_id(fid)
        self.populate_detail()

    def populate_detail(self):
        """把 self.current_composite 渲染到右侧信息与效果区"""
        comp = self.current_composite or {'id':'','name':'','description':'','effects':{}}
        self.id_label.config(text=str(comp.get('id','')))
        self.name_label.config(text=str(comp.get('name','')))
        # description 写入只读文本
        self.desc_label.config(state='normal')
        self.desc_label.delete(1.0, tk.END)
        self.desc_label.insert(1.0, str(comp.get('description','')))
        self.desc_label.config(state='disabled')

        # 清空门槛显示区
        for child in self.threshold_inner.winfo_children():
            child.destroy()

        effects_with_num = comp.get('effects', {}) or {}
        # 按门槛数值升序渲染
        for idx, num in enumerate(sorted(effects_with_num.keys(), key=lambda x: int(x))):
            row_frame = ttk.Frame(self.threshold_inner, padding=4, relief='ridge')
            row_frame.grid(row=idx, column=0, sticky=(tk.W, tk.E), pady=4, padx=4)
            row_frame.columnconfigure(1, weight=1)
            ttk.Label(row_frame, text=f'人数: {num}').grid(row=0, column=0, sticky=tk.W)
            # 删除门槛按钮与添加效果按钮
            ttk.Button(row_frame, text='删除门槛', command=lambda n=num: self.on_remove_threshold(n)).grid(row=0, column=1, padx=6)
            ttk.Button(row_frame, text='添加效果', command=lambda n=num: self.on_add_effect(n)).grid(row=0, column=2, padx=6)
            # 列表区域
            eff_list = effects_with_num.get(num) or []
            if not eff_list:
                ttk.Label(row_frame, text='(无效果)').grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=2)
            else:
                for j, e in enumerate(eff_list):
                    print(j, e)
                    desc = effect_parser(e) if callable(effect_parser) else str(e)
                    # 效果描述
                    ttk.Label(row_frame, text=f'  - {desc}').grid(row=1+j, column=0, sticky=tk.W)
                    # 修改效果按钮
                    ttk.Button(row_frame, text='修改', command=lambda n=num, idx=j: self.on_edit_effect(n, idx)).grid(row=1+j, column=1, padx=4)
                    # 删除效果按钮
                    ttk.Button(row_frame, text='删除', command=lambda n=num, idx=j: self.on_remove_effect(n, idx)).grid(row=1+j, column=2)

        # force update scrollregion
        self.threshold_inner.update_idletasks()
        self.threshold_canvas.configure(scrollregion=self.threshold_canvas.bbox('all'))

    def on_edit_field(self, field):
        """编辑 id/name/description，使用简单对话获得新值并保存"""
        if not self.current_composite:
            return
        initial = str(self.current_composite.get(field, ''))
        if field == 'description':
            new = tk.simpledialog.askstring('编辑 描述', '输入新的描述：', initialvalue=initial, parent=self.root)
        else:
            new = tk.simpledialog.askstring('编辑 字段', f'输入新的 {field}：', initialvalue=initial, parent=self.root)
        if new is None:
            return
        self.current_composite[field] = new
        self.populate_detail()
        # 尝试保存
        self.save_current_composite()

    def on_add_threshold(self):
        if not self.current_composite:
            messagebox.showwarning('提示', '请先选择或创建一个 Faction')
            return
        # 如果已有门槛，建议一个默认的 num（最大 +1），便于快速添加连续门槛
        suggested = ''
        existing = self.current_composite.get('effects', {}) or {}
        try:
            if existing:
                max_num = max([int(x) for x in existing.keys()])
                suggested = str(max_num + 1)
        except Exception:
            suggested = ''

        num = tk.simpledialog.askstring('添加门槛', '请输入人数门槛（整数）：', parent=self.root, initialvalue=suggested)
        if not num:
            return
        try:
            int(num)
        except Exception:
            messagebox.showerror('错误', '门槛必须为整数')
            return
        if 'effects' not in self.current_composite:
            self.current_composite['effects'] = {}
        if str(num) in self.current_composite['effects']:
            messagebox.showinfo('提示', '该门槛已存在')
            return

        # 如果存在其他人数门槛，则以第一个（按数字升序）门槛的效果作为新门槛的默认值
        new_effects = []
        if existing:
            try:
                first_key = sorted(existing.keys(), key=lambda x: int(x))[0]
                src = existing.get(first_key, [])
                new_effects = copy.deepcopy(src)
            except Exception:
                new_effects = []

        self.current_composite['effects'][str(num)] = new_effects
        self.populate_detail()
        self.save_current_composite()

    # 新增：删除整个人数门槛（含其下所有效果），带二次确认
    def on_remove_threshold(self, num):
        if not self.current_composite:
            return
        if not messagebox.askyesno('确认', f'确定删除人数门槛 {num} 及其所有效果吗？'):
            return
        effects = self.current_composite.get('effects', {})
        if str(num) in effects:
            effects.pop(str(num), None)
            self.populate_detail()
            self.save_current_composite()

    def on_add_effect(self, num):
        # 呼出效果编辑器
        try:
            from ui_effect import show_effect_editor
        except Exception:
            messagebox.showerror('错误', '无法加载效果编辑器')
            return
        res = show_effect_editor(self.root, modid=self.modid)
        if res is None:
            return
        # 添加到当前 composite
        if 'effects' not in self.current_composite:
            self.current_composite['effects'] = {}
        self.current_composite['effects'].setdefault(str(num), []).append(res)
        self.populate_detail()
        self.save_current_composite()

    def on_generate_description(self, num):
        """为指定人数门槛生成自然语言描述，询问用户是否替换当前 description 并保存"""
        if not self.current_composite:
            return
        effects = self.current_composite.get('effects', {})
        target = {str(num): effects.get(str(num), [])}

        gen = None
        # 优先调用 controller 的 gen_description_sentence
        try:
            if hasattr(self.controller, 'gen_description_sentence'):
                gen = self.controller.gen_description_sentence(target)
            elif hasattr(self.controller, 'gen_description'):
                # gen_description 可能返回 dict，取第一条
                gd = self.controller.gen_description(target)
                if isinstance(gd, dict):
                    gen = '；'.join(list(gd.values()))
                else:
                    gen = str(gd)
            else:
                # 降级：在 UI 层拼接（简单）
                items = target.get(str(num), [])
                parts = []
                for it in items:
                    parts.append(effect_parser(it) if callable(effect_parser) else str(it))
                gen = f"当人数{num}时，" + '；'.join(parts) if parts else ''
        except Exception as e:
            messagebox.showerror('错误', f'生成描述失败：{e}')
            return

        if not gen:
            messagebox.showinfo('提示', '未能生成描述（可能没有效果或生成逻辑未实现）')
            return

        # 询问用户是否替换当前 description
        if messagebox.askyesno('生成描述', f'为人数 {num} 生成的描述：\n{gen}\n\n是否替换当前描述并保存？'):
            self.current_composite['description'] = gen
            self.populate_detail()
            self.save_current_composite()

    def on_generate_all_descriptions(self):
        """为当前羁绊的所有门槛生成合并后的描述，并询问是否替换 description 并保存"""
        if not self.current_composite:
            return
        effects = self.current_composite.get('effects', {}) or {}
        gen = None
        try:
            gd = self.controller.gen_description(effects)
            if isinstance(gd, dict):
                gen = '；'.join(list(gd.values()))
            else:
                gen = str(gd)
            
        except Exception as e:
            messagebox.showerror('错误', f'生成描述失败：{e}')
            return

        if not gen:
            messagebox.showinfo('提示', '未能生成描述（可能没有效果或生成逻辑未实现）')
            return

        if messagebox.askyesno('生成描述', f'为当前羁绊生成的描述：\n{gen}\n\n是否替换当前描述并保存？'):
            self.current_composite['description'] = gen
            self.populate_detail()
            self.save_current_composite()

    # 新增：修改指定人数门槛下的某个效果
    def on_edit_effect(self, num, idx):
        if not self.current_composite:
            return
        lst = self.current_composite.get('effects', {}).get(str(num), [])
        if not (0 <= idx < len(lst)):
            return
        orig = lst[idx]
        try:
            from ui_effect import show_effect_editor
        except Exception:
            messagebox.showerror('错误', '无法加载效果编辑器')
            return
        # 尝试以原始效果作为初始值调用编辑器，若编辑器不支持该签名则降级调用
        res = None
        try:
            res = show_effect_editor(self.root, orig)
        except TypeError:
            try:
                res = show_effect_editor(self.root)
            except Exception as e:
                messagebox.showerror('错误', f'打开效果编辑器失败：{e}')
                return
        except Exception as e:
            messagebox.showerror('错误', f'打开效果编辑器失败：{e}')
            return
        if res is None:
            return
        # 替换并保存
        lst[idx] = res
        self.populate_detail()
        self.save_current_composite()

    def on_remove_effect(self, num, idx):
        lst = self.current_composite.get('effects', {}).get(str(num), [])
        if 0 <= idx < len(lst):
            lst.pop(idx)
            self.populate_detail()
            self.save_current_composite()

    def save_current_composite(self):
        if not self.current_composite:
            return
        try:
            if hasattr(self.controller, 'save_faction'):
                ok = self.controller.save_faction(self.current_composite)
            elif hasattr(self.controller, 'update_faction_composite'):
                ok = self.controller.update_faction_composite(self.current_composite)
            else:
                # 降级：尝试把 composite 拆成单条记录并调用 create/update
                # 这里只做本地提示
                raise AttributeError('control 不支持复合保存')
            if not ok:
                messagebox.showwarning('警告', '保存操作返回 False 或未实现')
        except Exception as e:
            messagebox.showerror('保存失败', f'保存失败：{e}\n请检查后端接口')

    def create_faction(self):
        """创建新羁绊。注意：Faction 的主键是 (id, numofpeople)。
        后端如果需要提供自动生成 num 或 id 的接口，请在 new_control/new_service 中实现；
        当前前端要求用户手动填写 id 和 numofpeople。
        """
        # 使用简化对话仅收集 id/name/description
        dialog = SimpleFactionDialog(self.root, "新建 Faction")
        if dialog.result:
            composite = dialog.result
            # 将 effects 留空（创建时仅保存元信息，后续可由编辑界面补充）
            composite.setdefault('effects', {})
            ok = self.controller.save_faction(composite)
            if ok:
                self.refresh_list()
                messagebox.showinfo("成功", "Faction 创建成功！")
            else:
                messagebox.showerror("失败", "后端返回失败或未实现保存逻辑")

    def edit_faction(self):
        """编辑羁绊。"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先在左侧选择一个 Faction ID！")
            return
        item = self.tree.item(selection[0])
        fid = item['values'][0]
        variants = str(item['values'][1]).split(',') if item['values'][1] else []

        # 构建复合结构并交给编辑对话框
        all_factions = self.controller.get_all_factions()
        variants = [f for f in all_factions if f.get('id') == fid]
        if not variants:
            messagebox.showerror("错误", "未能获取到指定的 Faction 记录，请检查后端接口是否支持查询")
            return

        composite = {
            'id': fid,
            'name': variants[0].get('name') or fid,
            'description': variants[0].get('description') or '',
            'effects': {}
        }
        for v in variants:
            key = str(v.get('numofpeople')) if v.get('numofpeople') is not None else '0'
            if 'effects' in v and isinstance(v['effects'], (list, dict)):
                composite['effects'][key] = v['effects']
            else:
                # 如果 description 中包含结构化 effects，尝试解析
                try:
                    d = v.get('description')
                    if isinstance(d, dict) and 'effects' in d:
                        composite['effects'][key] = d['effects']
                    else:
                        composite['effects'][key] = []
                except Exception:
                    composite['effects'][key] = []

        dialog = FactionDialog(self.root, "编辑 Faction", faction=composite, control=self.controller)
        if dialog.result:
            composite_res = dialog.result
            try:
                if hasattr(self.controller, 'save_faction'):
                    ok = self.controller.save_faction(composite_res)
                elif hasattr(self.controller, 'update_faction_composite'):
                    ok = self.controller.update_faction_composite(composite_res)
                else:
                    raise AttributeError('control 不支持保存复合 faction，请实现 save_faction(composite)')
                if ok:
                    self.refresh_list()
                    messagebox.showinfo("成功", "Faction 更新成功！")
                else:
                    messagebox.showerror("失败", "后端返回失败或未实现保存逻辑")
            except Exception as e:
                messagebox.showerror("错误", f"更新失败：{e}\n生成的数据：{json.dumps(composite_res, ensure_ascii=False, indent=2)}")

    def delete_faction(self):
        """删除羁绊，同样需要指定 numofpeople。如果所选 ID 有多个变体，会要求选择具体变体。"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先在左侧选择一个 Faction ID！")
            return
        item = self.tree.item(selection[0])
        fid = self.current_composite.get('id') if self.current_composite else item['values'][0]
        variants = str(item['values'][1]).split(',') if item['values'][1] else []

        try:
            # 同 edit 中的说明，delete_faction 接口在 control 层接受单个 faction_id，目前后端实现可能需要调整为复合主键
            # 我们尝试直接调用 delete_faction，并传入复合主键元组；若后端不支持，请在后端实现支持 (id, numofpeople)
            res = self.controller.delete_faction(fid)
            if res:
                self.refresh_list()
                # self.detail_text.delete(1.0, tk.END)
                messagebox.showinfo("成功", "Faction 删除成功！")
            else:
                messagebox.showerror("失败", "删除失败，后端返回 False 或 未实现复合主键删除")
        except Exception as e:
            messagebox.showerror("错误", f"删除失败：{e}")

    def export_json(self):
        try:
            self.controller.dumpJson()
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

        ttk.Label(self.dialog, text=f"Faction: {fid}").pack(pady=5)
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


class FactionDialog:
    """用于创建/编辑单条 Faction 记录的对话框"""

    def __init__(self, parent, title, faction: dict = None, control: FactionController = None):
        self.result = None
        self.controller = control

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x360")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 字段：id, name, description, effects（JSON 字符串）
        ttk.Label(main_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.id_entry = ttk.Entry(main_frame, width=40)
        self.id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="名称 (name):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="描述 (description):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.desc_text = tk.Text(main_frame, width=60, height=6)
        self.desc_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="effects (JSON):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.effects_text = tk.Text(main_frame, width=60, height=6)
        self.effects_text.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)

        # 如果是编辑模式，填充现有数据；支持传入复合结构或单项结构
        if faction:
            # faction 可能是复合结构
            fid = faction.get('id')
            if fid is not None:
                self.id_entry.insert(0, str(fid))
                try:
                    self.id_entry.state(['readonly'])
                except Exception:
                    self.id_entry.config(state='readonly')
            name = faction.get('name') or ''
            self.name_entry.insert(0, str(name))
            desc = faction.get('description', '')
            if isinstance(desc, (dict, list)):
                self.desc_text.insert(1.0, json.dumps(desc, ensure_ascii=False, indent=2))
            else:
                self.desc_text.insert(1.0, str(desc))
            # effects 期望为 dict，显示为 json
            effects = faction.get('effects') or {}
            try:
                self.effects_text.insert(1.0, json.dumps(effects, ensure_ascii=False, indent=2))
            except Exception:
                self.effects_text.insert(1.0, str(effects))

        btn_frame = ttk.Frame(self.dialog, padding="10")
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="确定", command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.on_cancel).pack(side=tk.RIGHT)

        self.dialog.wait_window()

    def on_ok(self):
        try:
            fid = self.id_entry.get().strip()
            name = self.name_entry.get().strip()
            desc = self.desc_text.get(1.0, tk.END).strip()
            effects_raw = self.effects_text.get(1.0, tk.END).strip()

            if not fid:
                messagebox.showerror("错误", "ID 不能为空！")
                return

            # 解析 description
            desc_val = desc
            try:
                desc_val = json.loads(desc)
            except Exception:
                pass

            # 解析 effects 为 dict
            effects_val = {}
            if effects_raw:
                try:
                    effects_val = json.loads(effects_raw)
                    if not isinstance(effects_val, dict):
                        messagebox.showerror("错误", "effects 必须是一个 JSON 对象（字典），键为人数门槛，值为效果列表）")
                        return
                except Exception as e:
                    messagebox.showerror("错误", f"effects JSON 解析错误：{e}")
                    return

            self.result = {
                'id': fid,
                'name': name,
                'description': desc_val,
                'effects': effects_val
            }
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"数据验证失败：{e}")
    
    def on_cancel(self):
        self.dialog.destroy()


class SimpleFactionDialog:
    """用于仅创建时收集 id、name、description 的简化对话框"""
    def __init__(self, parent, title="新建 Faction 简化"):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("480x220")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.id_entry = ttk.Entry(main_frame, width=40)
        self.id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=4)

        ttk.Label(main_frame, text="名称 (name):").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=4)

        ttk.Label(main_frame, text="描述 (description):").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.desc_entry = ttk.Entry(main_frame, width=60)
        self.desc_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=4)

        btn_frame = ttk.Frame(self.dialog, padding="8")
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="确定", command=self.on_ok).pack(side=tk.RIGHT, padx=6)
        ttk.Button(btn_frame, text="取消", command=self.on_cancel).pack(side=tk.RIGHT)

        self.dialog.wait_window()

    def on_ok(self):
        fid = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get().strip()
        if not fid:
            messagebox.showerror("错误", "ID 不能为空！")
            return
        self.result = {'id': fid, 'name': name, 'description': desc}
        self.dialog.destroy()

    def on_cancel(self):
        self.dialog.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = FactionManagerUI(root, 'test')
    root.mainloop()