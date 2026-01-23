"""
Skill 管理 UI
参考 default_skill.json
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json, sys, os
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mod_controller import SkillController
from utils import effect_parser, ParseError, log

class SkillManagerUI:
    def __init__(self, root, modid):
        self.root = root
        self.root.title('Skill 管理')
        self.root.geometry('1000x700')
        self.modid = modid
        self.control = SkillController(modid)
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 左列表
        list_frame = ttk.LabelFrame(main_frame, text='Skill 列表', padding=5)
        list_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0,5))
        self.tree = ttk.Treeview(list_frame, columns=('ID','Name'), show='headings', height=30)
        self.tree.heading('ID', text='技能 ID')
        self.tree.heading('Name', text='名称')
        self.tree.column('ID', width=160)
        self.tree.column('Name', width=200)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # 右侧按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N), pady=(0,5))
        ttk.Button(button_frame, text='创建技能', command=self.create_skill).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text='删除技能', command=self.delete_skill).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text='刷新', command=self.refresh_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text='保存详情', command=self.save_detail).pack(side=tk.LEFT, padx=6)

        # 右侧详情
        detail_frame = ttk.LabelFrame(main_frame, text='Skill 详情', padding=5)
        detail_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        detail_frame.columnconfigure(1, weight=1)
        detail_frame.rowconfigure(6, weight=1)
        detail_frame.rowconfigure(7, weight=1)

        # 基本字段
        ttk.Label(detail_frame, text='ID:').grid(row=0, column=0, sticky=tk.W)
        self.id_label = ttk.Label(detail_frame, text='')
        self.id_label.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Label(detail_frame, text='名称:').grid(row=1, column=0, sticky=tk.W)
        self.name_entry = ttk.Entry(detail_frame)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

        ttk.Label(detail_frame, text='类型:').grid(row=2, column=0, sticky=tk.W)
        self.type_var = tk.StringVar()
        self.type_cb = ttk.Combobox(detail_frame, textvariable=self.type_var, values=('active','passive'), state='readonly')
        self.type_cb.grid(row=2, column=1, sticky=(tk.W, tk.E))
        # 当类型变化时自动保存并切换触发器 UI
        self.type_cb.bind('<<ComboboxSelected>>', lambda e: self.on_type_change())

        # 触发器区域（根据类型显示单个触发器或多触发器列表）
        ttk.Label(detail_frame, text='触发器:').grid(row=3, column=0, sticky=tk.W)
        self.triggers_frame = ttk.Frame(detail_frame)
        self.triggers_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E))

        # 单触发器（用于 active）
        self.trigger_label = ttk.Label(self.triggers_frame, text='')
        self.trigger_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.add_trigger_btn = ttk.Button(self.triggers_frame, text='添加触发事件', command=self.add_trigger_event)
        self.add_trigger_btn.pack(side=tk.LEFT, padx=4)

        # 多触发器（用于 passive） - 使用 Listbox + 编辑/删除按钮
        self.triggers_list_frame = ttk.Frame(self.triggers_frame)
        self.triggers_listbox = tk.Listbox(self.triggers_list_frame, height=4)
        self.triggers_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        t_sb = ttk.Scrollbar(self.triggers_list_frame, orient=tk.VERTICAL, command=self.triggers_listbox.yview)
        t_sb.pack(side=tk.LEFT, fill=tk.Y)
        self.triggers_listbox.config(yscrollcommand=t_sb.set)
        t_btns = ttk.Frame(self.triggers_list_frame)
        t_btns.pack(side=tk.LEFT, fill=tk.Y, padx=6)
        ttk.Button(t_btns, text='添加', command=self.add_trigger_event).pack(fill=tk.X, pady=2)
        ttk.Button(t_btns, text='编辑', command=self.edit_trigger_event).pack(fill=tk.X, pady=2)
        ttk.Button(t_btns, text='删除', command=self.remove_trigger_event).pack(fill=tk.X, pady=2)

        # 初始隐藏多触发器列表，显示情况由 populate_detail 或类型变更控制
        self.triggers_list_frame.pack_forget()

        # 右侧详情 - 描述与条件效果
        ttk.Label(detail_frame, text='描述:').grid(row=4, column=0, sticky=tk.NW)
        self.desc_text = tk.Text(detail_frame, height=4, wrap=tk.WORD)
        self.desc_text.grid(row=4, column=1, sticky=(tk.W, tk.E))

        # 条件与效果显示
        cond_frame = ttk.LabelFrame(detail_frame, text='条件 (condition)', padding=4)
        cond_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(8,4))
        self.cond_text = tk.Text(cond_frame, height=6)
        self.cond_text.pack(fill=tk.BOTH, expand=True)
        self.cond_text.config(state='disabled')

        eff_frame = ttk.LabelFrame(detail_frame, text='效果 (effect)', padding=4)
        eff_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(4,0))
        # 使用 Listbox 显示每个效果条目，用户可选中后 编辑/删除
        self.eff_listbox = tk.Listbox(eff_frame, height=8)
        self.eff_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        eff_scroll = ttk.Scrollbar(eff_frame, orient=tk.VERTICAL, command=self.eff_listbox.yview)
        eff_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.eff_listbox.configure(yscrollcommand=eff_scroll.set)
        # 按钮区域
        eff_btn_frame = ttk.Frame(eff_frame)
        eff_btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=6)
        ttk.Button(eff_btn_frame, text='添加效果', command=lambda: self.on_add_effect_button()).pack(fill=tk.X, pady=2)
        ttk.Button(eff_btn_frame, text='修改效果', command=lambda: self.on_edit_effect_button()).pack(fill=tk.X, pady=2)
        ttk.Button(eff_btn_frame, text='删除效果', command=lambda: self.on_delete_effect_button()).pack(fill=tk.X, pady=2)

        # 绑定效果列表选择事件用于预览
        self.eff_listbox.bind('<<ListboxSelect>>', self.on_effect_select)

        # 效果预览区域（位于详情最下方）
        preview_frame = ttk.LabelFrame(detail_frame, text='效果预览', padding=4)
        preview_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(4,0))
        self.preview_text = tk.Text(preview_frame, height=8)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.config(state='disabled')

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

    def refresh_list(self):
        for it in self.tree.get_children():
            self.tree.delete(it)
        try:
            skills = self.control.get_all_skills()
        except Exception:
            skills = []
        # skills expected list of dicts with id/name
        for s in skills or []:
            sid = s.get('id')
            name = s.get('name') or sid
            self.tree.insert('', tk.END, values=(sid, name))

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        sid = item['values'][0]
        try:
            skill = self.control.get_skill_by_id(sid)
        except Exception as e:
            messagebox.showerror('错误', f'无法获取技能：{e}')
            return
        if not skill:
            return
        self.populate_detail(skill)

    def populate_detail(self, skill):
        self.id_label.config(text=str(skill.get('id','')))
        # 填充可编辑名称
        try:
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, str(skill.get('name','')))
        except Exception:
            pass

        # 根据类型展示触发器 UI
        typ = skill.get('type','')
        self.type_var.set(str(typ))
        self.update_trigger_ui_by_type(typ, skill)
        self.trigger_label.config(text=str(skill.get('trigger','')))
        # 描述可编辑
        self.desc_text.delete(1.0, tk.END)
        desc = skill.get('decription') or skill.get('description') or skill.get('desc') or ''
        if isinstance(desc, (dict,list)):
            self.desc_text.insert(1.0, json.dumps(desc, ensure_ascii=False, indent=2))
        else:
            self.desc_text.insert(1.0, str(desc))

        self.cond_text.config(state='normal')
        self.cond_text.delete(1.0, tk.END)
        cond = skill.get('condition') or []
        try:
            self.cond_text.insert(1.0, json.dumps(cond, ensure_ascii=False, indent=2))
        except Exception:
            self.cond_text.insert(1.0, str(cond))
        self.cond_text.config(state='disabled')

        self.eff_listbox.delete(0, tk.END)
        eff = skill.get('effect') or skill.get('effects') or []
        # 规范成列表
        if not isinstance(eff, list):
            try:
                eff = list(eff)
            except Exception:
                eff = [eff]
        # 填充 listbox
        for e in eff:
            try:
                label = json.dumps(e, ensure_ascii=False)
            except Exception:
                label = str(e)
            self.eff_listbox.insert(tk.END, label)
        # 保留当前 skill
        self.current_skill = skill
        # 如果有效果则选中首项并展示预览
        if self.eff_listbox.size() > 0:
            self.eff_listbox.select_set(0)
            self.on_effect_select(None)
        else:
            self.update_preview(None)

    def create_skill(self):
        dialog = SimpleSkillDialog(self.root, '新建 Skill')
        if not dialog.result:
            return
        rec = dialog.result
        rec.setdefault('condition', [])
        rec.setdefault('effect', [])
        try:
            if hasattr(self.control, 'create_skill'):
                # mod_controller.SkillController.create_skill 接口可能是 (id, data) 或 (data,)
                try:
                    ok = self.control.create_skill(rec.get('id'), rec)
                except TypeError:
                    ok = self.control.create_skill(rec)
            elif hasattr(self.control, 'save_skill'):
                ok = self.control.save_skill(rec)
            else:
                raise AttributeError('control 不支持 create/save_skill')
            if ok:
                self.refresh_list()
                messagebox.showinfo('成功', '技能创建成功')
            else:
                messagebox.showerror('失败', '后端返回失败或未实现')
        except Exception as e:
            messagebox.showerror('错误', f'创建失败：{e}')

    def edit_skill(self):
        # 编辑功能已移除为单独按钮；保留方法以兼容但不用于 UI
        pass

    def delete_skill(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('警告', '请先选择一个技能')
            return
        item = self.tree.item(sel[0])
        sid = item['values'][0]
        if not messagebox.askyesno('确认', f'确定删除技能 {sid} ?'):
            return
        try:
            if hasattr(self.control, 'delete_skill'):
                ok = self.control.delete_skill(sid)
            else:
                raise AttributeError('control 不支持 delete_skill')
            if ok:
                self.refresh_list()
                messagebox.showinfo('成功', '删除成功')
            else:
                messagebox.showerror('失败', '后端返回失败或未实现')
        except Exception as e:
            messagebox.showerror('错误', f'删除失败：{e}')

    def save_current_skill(self):
        # save self.current_skill to backend
        if not getattr(self, 'current_skill', None):
            return False
        sid = self.current_skill.get('id')
        try:
            if hasattr(self.control, 'update_skill'):
                return self.control.update_skill(self.current_skill)
            elif hasattr(self.control, 'save_skill'):
                return self.control.save_skill(self.current_skill)
        except Exception as e:
            messagebox.showerror('错误', f'保存技能失败：{e}')
        return False

    def save_detail(self):
        """保存名称和描述到当前技能并提交到后端"""
        if not getattr(self, 'current_skill', None):
            messagebox.showwarning('警告', '请先选择一个技能')
            return
        name = self.name_entry.get().strip()
        desc_raw = self.desc_text.get(1.0, tk.END).strip()
        # 尝试把描述解析为 JSON，否则保留字符串
        desc_val = desc_raw
        try:
            desc_val = json.loads(desc_raw)
        except Exception:
            desc_val = desc_raw
        self.current_skill['name'] = name
        # 使用现有字段名保持兼容
        self.current_skill['decription'] = desc_val
        self.current_skill['description'] = desc_val
        ok = self.save_current_skill()
        if ok:
            messagebox.showinfo('成功', '详情已保存')
            self.refresh_list()
        else:
            messagebox.showerror('失败', '保存失败')

    def on_type_change(self):
        typ = self.type_var.get()
        # 更新当前技能数据结构
        if not getattr(self, 'current_skill', None):
            return
        self.current_skill['type'] = typ
        if typ == 'active':
            # active 默认为无触发器
            if 'triggers' in self.current_skill:
                self.current_skill.pop('triggers', None)
            self.current_skill['trigger'] = []
        else:
            # passive 使用 triggers 列表
            if 'trigger' in self.current_skill and self.current_skill.get('trigger'):
                # 将单触发器迁移到 triggers 列表
                self.current_skill['triggers'] = [self.current_skill.get('trigger')]
                self.current_skill.pop('trigger', None)
            self.current_skill.setdefault('triggers', [])
        # 更新 UI 并保存
        self.update_trigger_ui_by_type(typ, self.current_skill)
        self.save_current_skill()

    def update_trigger_ui_by_type(self, typ, skill):
        # typ: 'active'|'passive'
        if typ == 'passive':
            # show listbox
            self.trigger_label.pack_forget()
            self.add_trigger_btn.pack_forget()
            self.triggers_list_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            # populate listbox
            self.triggers_listbox.delete(0, tk.END)
            trigs = skill.get('triggers') or skill.get('trigger') or []
            if isinstance(trigs, str):
                trigs = [trigs]
            for t in trigs:
                self.triggers_listbox.insert(tk.END, str(t))
        else:
            # show single label + add button
            self.triggers_list_frame.pack_forget()
            self.trigger_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.add_trigger_btn.pack(side=tk.LEFT, padx=4)
            # set text
            self.trigger_label.config(text=str(skill.get('trigger','')))

    def add_trigger_event(self):
        if not getattr(self, 'current_skill', None):
            messagebox.showwarning('警告', '请先选择一个技能')
            return
        try:
            from ui_effect import show_effect_editor  # keep local import for compatibility
        except Exception:
            pass
        try:
            from ui_skill import EventChooserDialog
        except Exception:
            try:
                from ui_event import EventChooserDialog
            except Exception as e:
                messagebox.showerror('错误', f'无法加载事件选择器：{e}')
                return
        chooser = EventChooserDialog(self.root, self.modid)
        selected = chooser.result
        if not selected:
            return
        typ = self.current_skill.get('type')
        if typ == 'passive':
            trigs = self.current_skill.get('triggers') or []
            if selected in trigs:
                messagebox.showwarning('警告', '该事件已添加，不能重复')
                return
            trigs.append(selected)
            self.current_skill['triggers'] = trigs
            if self.save_current_skill():
                self.update_trigger_ui_by_type('passive', self.current_skill)
                messagebox.showinfo('成功', '事件已添加')
            else:
                messagebox.showerror('失败', '保存失败')
        else:
            # active
            self.current_skill['trigger'] = selected
            if 'triggers' in self.current_skill:
                self.current_skill.pop('triggers', None)
            if self.save_current_skill():
                self.trigger_label.config(text=str(selected))
                messagebox.showinfo('成功', '触发器已设置')
            else:
                messagebox.showerror('失败', '保存失败')

    def edit_trigger_event(self):
        # 仅针对 passive 列表编辑选中项
        if not getattr(self, 'current_skill', None):
            messagebox.showwarning('警告', '请先选择一个技能')
            return
        sel = self.triggers_listbox.curselection()
        if not sel:
            messagebox.showwarning('警告', '请先选择要编辑的事件')
            return
        idx = sel[0]
        old = self.triggers_listbox.get(idx)
        try:
            from ui_event import EventChooserDialog
            chooser = EventChooserDialog(self.root, self.modid)
            new = chooser.result
        except Exception as e:
            messagebox.showerror('错误', f'打开选择器失败：{e}')
            return
        if not new:
            return
        trigs = self.current_skill.get('triggers') or []
        if new in trigs and new != old:
            messagebox.showwarning('警告', '该事件已存在，不能重复')
            return
        trigs[idx] = new
        self.current_skill['triggers'] = trigs
        if self.save_current_skill():
            self.update_trigger_ui_by_type('passive', self.current_skill)
            messagebox.showinfo('成功', '事件已更新')
        else:
            messagebox.showerror('失败', '保存失败')

    def remove_trigger_event(self):
        if not getattr(self, 'current_skill', None):
            messagebox.showwarning('警告', '请先选择一个技能')
            return
        sel = self.triggers_listbox.curselection()
        if not sel:
            messagebox.showwarning('警告', '请先选择要删除的事件')
            return
        idx = sel[0]
        if not messagebox.askyesno('确认', '确定删除所选事件吗？'):
            return
        trigs = self.current_skill.get('triggers') or []
        trigs.pop(idx)
        self.current_skill['triggers'] = trigs
        if self.save_current_skill():
            self.update_trigger_ui_by_type('passive', self.current_skill)
            messagebox.showinfo('成功', '已删除')
        else:
            messagebox.showerror('失败', '保存失败')

    def on_add_effect_button(self):
        """添加效果：调用效果编辑器，加入 self.current_skill 的 effect 列表并保存"""
        if not getattr(self, 'current_skill', None):
            messagebox.showwarning('警告', '请先选择一个技能')
            return
        try:
            from ui_effect import show_effect_editor
        except Exception:
            messagebox.showerror('错误', '无法加载效果编辑器')
            return
        new_eff = show_effect_editor(self.root, None, self.modid)
        if not new_eff:
            return
        # 兼容 effect / effects 字段
        effs = self.current_skill.get('effect') or self.current_skill.get('effects') or []
        if not isinstance(effs, list):
            effs = [effs]
        effs.append(new_eff)
        # prefer 'effect' key
        self.current_skill['effect'] = effs
        # 更新界面
        try:
            label = json.dumps(new_eff, ensure_ascii=False)
        except Exception:
            label = str(new_eff)
        self.eff_listbox.insert(tk.END, label)
        # 选中新添加项并更新预览
        last_index = self.eff_listbox.size() - 1
        if last_index >= 0:
            self.eff_listbox.select_clear(0, tk.END)
            self.eff_listbox.select_set(last_index)
            self.on_effect_select(None)
        # 保存
        if self.save_current_skill():
            messagebox.showinfo('成功', '效果已添加并保存')
        else:
            messagebox.showerror('失败', '添加后保存失败')

    def on_edit_effect_button(self):
        """编辑选中的效果条目，保存变更"""
        if not getattr(self, 'current_skill', None):
            messagebox.showwarning('警告', '请先选择一个技能')
            return
        sel = self.eff_listbox.curselection()
        if not sel:
            messagebox.showwarning('警告', '请先选择一个效果项')
            return
        idx = sel[0]
        effs = self.current_skill.get('effect') or self.current_skill.get('effects') or []
        if not isinstance(effs, list):
            effs = [effs]
        old = effs[idx]
        try:
            from ui_effect import show_effect_editor
        except Exception:
            messagebox.showerror('错误', '无法加载效果编辑器')
            return
        new = show_effect_editor(self.root, old, self.modid)
        if new is None:
            return
        effs[idx] = new
        self.current_skill['effect'] = effs
        # 刷新 listbox 项
        try:
            label = json.dumps(new, ensure_ascii=False)
        except Exception:
            label = str(new)
        self.eff_listbox.delete(idx)
        self.eff_listbox.insert(idx, label)
        # 重新选中并更新预览
        self.eff_listbox.select_clear(0, tk.END)
        self.eff_listbox.select_set(idx)
        self.on_effect_select(None)
        # 保存
        if self.save_current_skill():
            messagebox.showinfo('成功', '效果已更新并保存')
        else:
            messagebox.showerror('失败', '更新后保存失败')

    def on_delete_effect_button(self):
        """删除选中的效果项并保存"""
        if not getattr(self, 'current_skill', None):
            messagebox.showwarning('警告', '请先选择一个技能')
            return
        sel = self.eff_listbox.curselection()
        if not sel:
            messagebox.showwarning('警告', '请先选择一个效果项')
            return
        idx = sel[0]
        if not messagebox.askyesno('确认', '确定删除该效果项吗？'):
            return
        effs = self.current_skill.get('effect') or self.current_skill.get('effects') or []
        if not isinstance(effs, list):
            effs = [effs]
        try:
            effs.pop(idx)
        except Exception:
            messagebox.showerror('错误', '删除失败')
            return
        self.current_skill['effect'] = effs
        self.eff_listbox.delete(idx)
        # 更新预览：选中下一个可用项或清空
        if self.eff_listbox.size() > 0:
            new_idx = min(idx, self.eff_listbox.size() - 1)
            self.eff_listbox.select_set(new_idx)
            self.on_effect_select(None)
        else:
            self.update_preview(None)
        if self.save_current_skill():
            messagebox.showinfo('成功', '已删除并保存')
        else:
            messagebox.showerror('失败', '删除后保存失败')

    def on_effect_select(self, event=None):
        """当用户在效果列表选择某项时，展示预览"""
        if not getattr(self, 'current_skill', None):
            self.update_preview(None)
            return
        sel = self.eff_listbox.curselection()
        if not sel:
            self.update_preview(None)
            return
        idx = sel[0]
        effs = self.current_skill.get('effect') or self.current_skill.get('effects') or []
        if not isinstance(effs, list):
            effs = [effs]
        try:
            eff = effs[idx]
        except Exception:
            eff = None
        self.update_preview(eff)

    def update_preview(self, eff):
        """把效果对象格式化并显示在预览框中，使用 utils.effect_parser 生成自然语言描述"""
        try:
            self.preview_text.config(state='normal')
            self.preview_text.delete(1.0, tk.END)
            if eff is None:
                self.preview_text.insert(1.0, '未选择效果')
            else:
                # 如果是字串尝试解析为 json 对象
                parsed = None
                if isinstance(eff, str):
                    try:
                        parsed = json.loads(eff)
                    except Exception:
                        parsed = eff
                else:
                    parsed = eff

                # 优先使用 effect_parser 输出自然语言描述
                try:
                    if isinstance(parsed, dict):
                        desc = effect_parser(parsed, highlight_num=True)
                        self.preview_text.insert(1.0, desc)
                    else:
                        # 非字典则直接显示其字符串形式
                        try:
                            self.preview_text.insert(1.0, json.dumps(parsed, ensure_ascii=False, indent=2))
                        except Exception:
                            self.preview_text.insert(1.0, str(parsed))
                except ParseError as pe:
                    # 解析失败，显示友好错误并回退到 JSON
                    self.preview_text.insert(1.0, f"解析效果失败: {pe}\n\n原始数据:\n")
                    try:
                        self.preview_text.insert(tk.END, json.dumps(eff, ensure_ascii=False, indent=2))
                    except Exception:
                        self.preview_text.insert(tk.END, str(eff))
                except Exception as e:
                    # 其它异常，记录并显示原始
                    try:
                        self.preview_text.insert(1.0, json.dumps(eff, ensure_ascii=False, indent=2))
                    except Exception:
                        self.preview_text.insert(1.0, str(eff))
        finally:
            self.preview_text.config(state='disabled')

class SkillDialog:
    def __init__(self, parent, title, skill: dict = None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry('700x420')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        frame = ttk.Frame(self.dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text='ID:').grid(row=0, column=0, sticky=tk.W)
        self.id_entry = ttk.Entry(frame, width=40)
        self.id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='名称:').grid(row=1, column=0, sticky=tk.W)
        self.name_entry = ttk.Entry(frame, width=40)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='类型:').grid(row=2, column=0, sticky=tk.W)
        self.type_entry = ttk.Entry(frame, width=40)
        self.type_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='触发器:').grid(row=3, column=0, sticky=tk.W)
        self.trigger_entry = ttk.Entry(frame, width=40)
        self.trigger_entry.grid(row=3, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='描述:').grid(row=4, column=0, sticky=tk.W)
        self.desc_text = tk.Text(frame, height=4)
        self.desc_text.grid(row=4, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='condition (JSON):').grid(row=5, column=0, sticky=tk.W)
        self.cond_text = tk.Text(frame, height=6)
        self.cond_text.grid(row=5, column=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text='effect (JSON):').grid(row=6, column=0, sticky=tk.W)
        self.eff_text = tk.Text(frame, height=6)
        self.eff_text.grid(row=6, column=1, sticky=(tk.W, tk.E))

        if skill:
            sid = skill.get('id')
            if sid is not None:
                self.id_entry.insert(0, str(sid))
                try:
                    self.id_entry.state(['readonly'])
                except Exception:
                    self.id_entry.config(state='readonly')
            self.name_entry.insert(0, str(skill.get('name') or ''))
            self.type_entry.insert(0, str(skill.get('type') or ''))
            self.trigger_entry.insert(0, str(skill.get('trigger') or ''))
            d = skill.get('decription') or skill.get('description') or ''
            if isinstance(d, (dict,list)):
                self.desc_text.insert(1.0, json.dumps(d, ensure_ascii=False, indent=2))
            else:
                self.desc_text.insert(1.0, str(d))
            try:
                self.cond_text.insert(1.0, json.dumps(skill.get('condition') or [], ensure_ascii=False, indent=2))
            except Exception:
                self.cond_text.insert(1.0, str(skill.get('condition') or []))
            try:
                self.eff_text.insert(1.0, json.dumps(skill.get('effect') or skill.get('effects') or [], ensure_ascii=False, indent=2))
            except Exception:
                self.eff_text.insert(1.0, str(skill.get('effect') or skill.get('effects') or []))

        btn_frame = ttk.Frame(self.dialog, padding=10)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text='确定', command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text='取消', command=self.on_cancel).pack(side=tk.RIGHT)
        self.dialog.wait_window()

    def on_ok(self):
        sid = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        typ = self.type_entry.get().strip()
        trigger = self.trigger_entry.get().strip()
        desc = self.desc_text.get(1.0, tk.END).strip()
        cond_raw = self.cond_text.get(1.0, tk.END).strip()
        eff_raw = self.eff_text.get(1.0, tk.END).strip()
        if not sid:
            messagebox.showerror('错误', 'ID 不能为空')
            return
        cond = []
        if cond_raw:
            try:
                cond = json.loads(cond_raw)
                if not isinstance(cond, list):
                    messagebox.showerror('错误', 'condition 必须为列表')
                    return
            except Exception as e:
                messagebox.showerror('错误', f'condition 解析失败：{e}')
                return
        eff = []
        if eff_raw:
            try:
                eff = json.loads(eff_raw)
                if not isinstance(eff, list):
                    messagebox.showerror('错误', 'effect 必须为列表')
                    return
            except Exception as e:
                messagebox.showerror('错误', f'effect 解析失败：{e}')
                return
        # description 尝试 json 解析
        desc_val = desc
        try:
            desc_val = json.loads(desc)
        except Exception:
            pass
        self.result = {
            'id': sid,
            'name': name,
            'type': typ,
            'trigger': trigger,
            'decription': desc_val,
            'condition': cond,
            'effect': eff
        }
        self.dialog.destroy()

    def on_cancel(self):
        self.dialog.destroy()


class SimpleSkillDialog:
    def __init__(self, parent, title='新建 Skill 简化'):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry('480x220')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        frame = ttk.Frame(self.dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text='ID:').grid(row=0, column=0, sticky=tk.W)
        self.id_entry = ttk.Entry(frame, width=40)
        self.id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Label(frame, text='名称:').grid(row=1, column=0, sticky=tk.W)
        self.name_entry = ttk.Entry(frame, width=40)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))
        ttk.Label(frame, text='描述:').grid(row=2, column=0, sticky=tk.W)
        self.desc_entry = ttk.Entry(frame, width=60)
        self.desc_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))
        btn_frame = ttk.Frame(self.dialog, padding=8)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text='确定', command=self.on_ok).pack(side=tk.RIGHT, padx=6)
        ttk.Button(btn_frame, text='取消', command=self.on_cancel).pack(side=tk.RIGHT)
        self.dialog.wait_window()

    def on_ok(self):
        sid = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get().strip()
        if not sid:
            messagebox.showerror('错误', 'ID 不能为空')
            return
        self.result = {'id': sid, 'name': name, 'decription': desc}
        self.dialog.destroy()

    def on_cancel(self):
        self.dialog.destroy()


class EventChooserDialog:
    """
    简单的事件选择器对话框：列出 mods/{modid}/data/{modid}/events/*.json 中的事件文件，显示 "id - name"，双击或选择后点击确定返回 id。
    返回结果保存在 self.result（字符串或 None）。
    """
    def __init__(self, parent, modid):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title('选择触发事件')
        self.dialog.geometry('420x380')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        frame = ttk.Frame(self.dialog, padding=8)
        frame.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(frame)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind('<Double-1>', self._on_double)
        sb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.listbox.yview)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.config(yscrollcommand=sb.set)

        btnf = ttk.Frame(self.dialog, padding=6)
        btnf.pack(fill=tk.X)
        ttk.Button(btnf, text='确定', command=self._on_ok).pack(side=tk.RIGHT, padx=6)
        ttk.Button(btnf, text='取消', command=self._on_cancel).pack(side=tk.RIGHT)

        # 加载事件文件列表
        # 优先通过后端获取事件列表，若失败回退到文件读取
        items = []
        try:
            from mod_controller import EventController
            evc = EventController(modid)
            events = evc.get_all_events(is_self_mod=False) or []
            for ev in events:
                eid = ev.get('id') or ev.get('file') or ''
                name = ev.get('name', '')
                label = f"{eid} - {name}" if eid else name
                items.append((eid or name, label))
        except Exception as e:
            # 后端获取失败，回退到直接读取文件
            log.console(f"从后端加载事件失败，回退到文件读取: {e}", "WARN")
            events_path = Path(__file__).resolve().parent / 'mods' / modid / 'data' / modid / 'events'
            if events_path.exists():
                for f in sorted(events_path.glob('*.json')):
                    try:
                        with open(f, 'r', encoding='utf-8') as fh:
                            data = json.load(fh)
                        eid = data.get('id') or f.stem
                        name = data.get('name', '')
                        label = f"{eid} - {name}"
                    except Exception:
                        label = f.stem
                        eid = f.stem
                    items.append((eid, label))
        for eid, label in items:
            self.listbox.insert(tk.END, label)

        self.dialog.wait_window()

    def _on_double(self, _ev=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        label = self.listbox.get(sel[0])
        eid = label.split(' - ')[0]
        self.result = eid
        self.dialog.destroy()

    def _on_ok(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning('警告', '请先选择一个事件')
            return
        label = self.listbox.get(sel[0])
        eid = label.split(' - ')[0]
        self.result = eid
        self.dialog.destroy()

    def _on_cancel(self):
        self.dialog.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = SkillManagerUI(root, 'test')
    root.mainloop()
