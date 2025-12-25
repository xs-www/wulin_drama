#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import json
import sys
from pathlib import Path

CSV_FILE = Path('characters.CSV')     # 原始文件
OUT_FILE = Path('roles.json')    # 输出文件

def split_to_list(raw: str) -> list:
    """把 a;b;c 转成 ['a','b','c']，空串返回空列表。"""
    return [s for s in raw.split(';') if s]

def build_matrix(raw: str):
    """9 个数字用 ; 分隔 → 3×3 二维列表。"""
    nums = [int(x) for x in split_to_list(raw)]
    if len(nums) != 9:
        raise ValueError('hate_matrix 必须是 9 个数字')
    return [nums[i:i+3] for i in range(0, 9, 3)]

def row_to_dict(headers: list[str], row: list[str]) -> dict:
    """单行转 dict，按需做类型/格式转换。"""
    out = {}
    for key, val in zip(headers, row):
        val = val.strip()
        if not val:                # 空字段直接跳过
            continue

        # 需要转列表的字段
        if key in {'avaliable_location'}:
            out[key] = split_to_list(val)
        # hate_matrix 特殊处理
        elif key == 'hate_matrix':
            out[key] = build_matrix(val)
        # 数值字段
        elif key in {'attack_power', 'health_points', 'speed', 'hate_value', 'price', 'energy'}:
            out[key] = int(val)
        # 其余当字符串
        else:
            out[key] = val

        out['id'] = str(out['id']).zfill(4)  # ID 补零到 4 位
    return out

def main():
    if not CSV_FILE.exists():
        sys.exit(f'找不到 {CSV_FILE}')

    with CSV_FILE.open(encoding='utf-8-sig') as f:
        rdr = csv.reader(f)
        rows = list(rdr)

    if len(rows) < 2:
        sys.exit('CSV 至少需要两行（说明+表头）')

    headers = rows[1]          # 第二行当键名
    data = [row_to_dict(headers, row) for row in rows[2:]]  # 从第三行开始是数据

    with OUT_FILE.open('w', encoding='utf-8') as f:
        json.dump({item['id']: item for item in data}, f, ensure_ascii=False, indent=2)

    print(f'已生成 {OUT_FILE} ，共 {len(data)} 条角色记录。')

if __name__ == '__main__':
    main()