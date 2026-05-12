import util
import entity, effect
import os, sys, importlib, zipfile, json, re
from pathlib import Path

BASE_DIR = util.BASE_DIR

OP_RE = r'(>=|<=|==|!=|~=|\^|>|<|=)?'
VER_RE = r'([0-9]+(?:\.[0-9]+)*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?'
PAT = re.compile(rf'{OP_RE}\s*{VER_RE}')

# 尝试使用 packaging 库进行版本比较和 Specifier 解析；不可用时回退到内置实现
try:
    from packaging.version import Version
    from packaging.specifiers import SpecifierSet
    PACKAGING_AVAILABLE = True
except Exception:
    Version = None
    SpecifierSet = None
    PACKAGING_AVAILABLE = False

# --- 备选：内置简单语义版本比较（支持数字段和可选 pre-release，用于当 packaging 不可用时）
def _split_ver(v: str):
    v = str(v).strip()
    parts = v.split('-', 1)
    nums = [int(x) for x in parts[0].split('.') if x != '']
    pre = parts[1].split('.') if len(parts) > 1 else None
    return nums, pre

def _cmp_prerelease(a, b):
    if a is None and b is None:
        return 0
    if a is None:
        return 1
    if b is None:
        return -1
    la, lb = len(a), len(b)
    for i in range(max(la, lb)):
        if i >= la: return -1
        if i >= lb: return 1
        ai, bi = a[i], b[i]
        if re.fullmatch(r'\d+', ai) and re.fullmatch(r'\d+', bi):
            ai_n, bi_n = int(ai), int(bi)
            if ai_n != bi_n: return 1 if ai_n > bi_n else -1
        else:
            if ai != bi: return 1 if ai > bi else -1
    return 0

def compare_semver(a: str, b: str) -> int:
    """比较两个语义版本号数字段和 pre-release，返回 1/0/-1 表示 a>b / == / <"""
    an, ap = _split_ver(a)
    bn, bp = _split_ver(b)
    for i in range(max(len(an), len(bn))):
        ai = an[i] if i < len(an) else 0
        bi = bn[i] if i < len(bn) else 0
        if ai != bi:
            return 1 if ai > bi else -1
    return _cmp_prerelease(ap, bp)

def _satisfy_by_op(current: str, required: str, op: str) -> bool:
    cmp = compare_semver(current, required)
    if op in ('=', '=='):
        return cmp == 0
    if op == '!=':
        return cmp != 0
    if op == '>':
        return cmp > 0
    if op == '<':
        return cmp < 0
    if op == '>=':
        return cmp >= 0
    if op == '<=':
        return cmp <= 0
    raise ValueError(f'不支持的运算符: {op}')

# 将约束字符串规范化为 packaging 可接受的形式：若单个约束缺少操作符，则默认按 '==' 处理
_OP_PREFIX_RE = re.compile(r"^\s*(>=|<=|==|!=|~=|\^|>|<|=)")

def normalize_requirement(req: str) -> str:
    parts = [p.strip() for p in str(req).split(',') if p.strip()]
    norm = []
    for p in parts:
        if _OP_PREFIX_RE.match(p):
            norm.append(p)
        else:
            # treat bare version as exact match
            norm.append('==' + p)
    return ','.join(norm)

def satisfies_constraint(current_version: str, requirement: str) -> bool:
    """判断当前版本是否满足 requirement（可以是单个约束或逗号分隔的复合约束）。
    优先使用 packaging 的 SpecifierSet；不可用时使用内置比较函数解析并逐一校验。
    """
    if current_version is None or requirement is None:
        return False
    cv = str(current_version).strip()
    req = str(requirement).strip()
    if PACKAGING_AVAILABLE:
        try:
            spec = SpecifierSet(normalize_requirement(req))
            return Version(cv) in spec
        except Exception:
            # 解析失败回退到内置实现
            pass
    # fallback: 使用 PAT 拆分并逐一比较（所有子约束均需满足）
    for op, ver in parse_constraints(req):
        if not _satisfy_by_op(cv, ver, op):
            return False
    return True

# 解析约束为 (op, version) 列表（保留原功能）
def parse_constraints(s):
    """返回 [(op, version), ...]，如果没有 op，则 op 返回 '='"""
    res = []
    for m in PAT.finditer(str(s)):
        op = m.group(1) or '='
        ver = m.group(2)
        res.append((op, ver))
    return res

class ModLoader:
    def __init__(self, mods_dir: Path = None):
        self.mods_dir = mods_dir or (BASE_DIR / 'mods')
        self.mods_dir = Path(self.mods_dir)

    def _parse_stem(self, stem: str):
        """解析 zip stem，如 'modname-1.2.3' -> (modname, '1.2.3')；如果无版本返回 (modname, None)"""
        m = re.match(r'^(?P<name>.+?)(?:-(?P<ver>\d+(?:\.\d+)*))?$', stem)
        if not m:
            return stem, None
        return m.group('name'), m.group('ver')

    def load_mods(self, mod_path: Path):
        """如果是 zip，解压到 mods_dir/modname 并返回解压目录（Path）；否则返回原路径"""
        mod_path = Path(mod_path)
        if zipfile.is_zipfile(mod_path):
            extract_path = self.mods_dir / mod_path.stem
            extract_path.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(mod_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            return extract_path
        return mod_path

    def get_load_order(self) -> dict:
        """扫描 mods 目录下的 zip 模组，读取 manifest.json 中的 dependencies，返回 dict：
        { mod_stem: { dependency_name: version_req, ... }, ... }
        """
        mods_dependency_dict = {}
        if not self.mods_dir.exists():
            return mods_dependency_dict
        # 先收集所有模组的 name/version 映射，便于依赖检查
        mods_info = {}
        for mod_file in sorted(self.mods_dir.glob('*.zip')):
            mods_info[mod_file.stem] = {'path': mod_file, 'name': None, 'version': None}
        for stem in list(mods_info.keys()):
            name, ver = self._parse_stem(stem)
            mods_info[stem]['name'] = name
            mods_info[stem]['version'] = ver

        for mod_file in sorted(self.mods_dir.glob('*.zip')):
            try:
                with zipfile.ZipFile(mod_file, 'r') as zip_ref:
                    deps = {}
                    if 'manifest.json' in zip_ref.namelist():
                        with zip_ref.open('manifest.json') as f:
                            try:
                                manifest = json.load(f)
                                deps = manifest.get('dependencies', {}) or {}
                            except Exception:
                                deps = {}
                    # 构建结构化信息并判断依赖是否满足
                    name, ver = self._parse_stem(mod_file.stem)
                    dep_check = {}
                    for dep_name, req in deps.items():
                        # 查找是否有模组匹配 dep_name
                        found = False
                        for other_stem, info in mods_info.items():
                            if info['name'] == dep_name and info['version']:
                                found = True
                                satisfied = satisfies_constraint(info['version'], req)
                                dep_check[dep_name] = {'required': req, 'found_version': info['version'], 'satisfied': satisfied}
                                break
                        if not found:
                            dep_check[dep_name] = {'required': req, 'found_version': None, 'satisfied': False}
                    mods_dependency_dict[mod_file.stem] = {'name': name, 'version': ver, 'dependencies': dep_check}
            except Exception:
                mods_dependency_dict[mod_file.stem] = {'name': None, 'version': None, 'dependencies': {}}
        return mods_dependency_dict

    # ---------- 新增：按依赖顺序加载所有 mod 并合并数据 ----------
    def _find_data_dir(self, base_path: Path):
        """查找解压后的 mod 中的 data 目录，返回 Path 或 None"""
        base_path = Path(base_path)
        candidates = [base_path / 'data']
        # 有些 zip 会把内容放在子目录（以 mod 名为目录）
        for child in base_path.iterdir() if base_path.exists() else []:
            if child.is_dir() and (child / 'data').exists():
                candidates.append(child / 'data')
        for c in candidates:
            if c.exists() and c.is_dir():
                return c
        return None

    def load_all_mods(self):
        """按照依赖（get_load_order）计算加载顺序，按顺序加载并把 data 下的 entities/effects 等合并到内存。
        若出现相同 id，后加载的模组会覆盖先加载的（遵循用户要求）。
        返回按加载顺序的模组 stem 列表。
        """
        order_info = self.get_load_order()
        if not order_info:
            util.log.console('未发现任何 zip 模组。', 'WARN')
            return []

        # 构建 name -> list of (stem, version) 映射
        name_map = {}
        for stem, info in order_info.items():
            name = info.get('name') or stem
            ver = info.get('version')
            name_map.setdefault(name, []).append((stem, ver))

        # 解析依赖为具体的 stem（选择满足约束且版本最高者）
        dep_graph = {stem: set() for stem in order_info.keys()}  # edge: dep_stem -> stem
        for stem, info in order_info.items():
            deps = info.get('dependencies', {}) or {}
            for dep_name, dep_meta in deps.items():
                req = dep_meta.get('required')
                candidates = name_map.get(dep_name, [])
                chosen = None
                # 选择满足 req 的候选并取最高版本
                valid = []
                for c_stem, c_ver in candidates:
                    if c_ver and satisfies_constraint(c_ver, req):
                        valid.append((c_stem, c_ver))
                if valid:
                    from functools import cmp_to_key
                    valid.sort(key=cmp_to_key(lambda a, b: compare_semver(a[1], b[1])))
                    chosen = valid[-1][0]
                if chosen:
                    # 依赖的模组（chosen）应在被依赖模组（stem）之前加载
                    dep_graph[chosen].add(stem)

        # 拓扑排序（Kahn）；如果有环则按字母顺序强制追加剩余节点
        indeg = {n: 0 for n in dep_graph}
        for frm, tos in dep_graph.items():
            for t in tos:
                indeg[t] = indeg.get(t, 0) + 1
        queue = [n for n, d in indeg.items() if d == 0]
        queue.sort()
        load_order = []
        while queue:
            n = queue.pop(0)
            load_order.append(n)
            for m in sorted(dep_graph.get(n, [])):
                indeg[m] -= 1
                if indeg[m] == 0:
                    queue.append(m)
            queue.sort()

        # 检查是否存在环
        remaining = [n for n, d in indeg.items() if d > 0]
        if remaining:
            util.log.console(f'发现依赖环或无法解析的依赖，剩余节点: {remaining}，将按名称顺序加载它们。', 'WARN')
            for n in sorted(remaining):
                if n not in load_order:
                    load_order.append(n)

        util.log.console(f'最终加载顺序: {load_order}', 'INFO')

        # 按顺序加载并合并 data/entities 和 data/effects
        for stem in load_order:
            modfile_zip = self.mods_dir / (stem + '.zip')
            mod_dir = None
            if modfile_zip.exists():
                try:
                    mod_dir = self.load_mods(modfile_zip)
                except Exception as e:
                    util.log.console(f'解压模组 {stem} 失败: {e}', 'ERROR')
                    continue
            else:
                # 也尝试目录形式
                cand = self.mods_dir / stem
                if cand.exists():
                    mod_dir = cand
                else:
                    util.log.console(f'模组文件/目录未找到: {stem}', 'WARN')
                    continue

            data_dir = self._find_data_dir(mod_dir)
            if not data_dir:
                util.log.console(f'模组 {stem} 未包含 data 目录，跳过。', 'INFO')
                continue

            # 合并 entities
            ent_folder = data_dir / 'entities'
            if ent_folder.exists():
                for jf in sorted(ent_folder.glob('*.json')):
                    try:
                        with open(jf, 'r', encoding='utf-8') as fh:
                            rec = json.load(fh)
                        eid = rec.get('id') or jf.stem
                        # 后加载覆盖先加载
                        self.entities[eid] = rec
                    except Exception as e:
                        util.log.console(f'读取实体文件 {jf} 失败: {e}', 'ERROR')

            # 合并 effects
            eff_folder = data_dir / 'effects'
            if eff_folder.exists():
                for jf in sorted(eff_folder.glob('*.json')):
                    try:
                        with open(jf, 'r', encoding='utf-8') as fh:
                            rec = json.load(fh)
                        fid = rec.get('id') or jf.stem
                        self.effects[fid] = rec
                    except Exception as e:
                        util.log.console(f'读取效果文件 {jf} 失败: {e}', 'ERROR')

        util.log.console('所有模组加载完成。', 'OK')
        return load_order


if __name__ == "__main__":
    mod_loader = ModLoader()
    print(mod_loader.get_load_order())