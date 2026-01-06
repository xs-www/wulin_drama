"""
初始化数据库脚本
将现有的 character_config.json 导入到数据库中
"""
import json
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dao import CharacterDao, dumpSql, updateDb

def import_from_json():
    """从 character_config.json 导入数据"""
    # 读取现有的 character_config.json
    json_path = Path(__file__).resolve().parent.parent / "py灰盒" / "character_config.json"
    
    if not json_path.exists():
        print(f"找不到文件: {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    dao = CharacterDao()
    
    # 导入每个 character
    for char_id, char_data in config.items():
        try:
            # 确保 id 字段存在
            if 'id' not in char_data:
                char_data['id'] = char_id
            
            # 检查是否已存在
            existing = dao.read(char_id)
            if existing:
                print(f"更新 Character {char_id}: {char_data.get('name', 'Unknown')}")
                update_data = char_data.copy()
                del update_data['id']
                dao.update(char_id, update_data)
            else:
                print(f"创建 Character {char_id}: {char_data.get('name', 'Unknown')}")
                dao.create(char_data)
        except Exception as e:
            print(f"处理 Character {char_id} 时出错: {str(e)}")
    
    print("\n数据导入完成！")
    
    # 导出 SQL
    print("正在导出 SQL...")
    dumpSql()
    print("SQL 导出完成！")

if __name__ == '__main__':
    import_from_json()
