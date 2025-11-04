import json
import os
from typing import List, Dict, Optional


class LinkDataManager:
    def __init__(self, file_path: str):
        """
        初始化管理器
        :param file_path: JSON文件路径
        """
        self.file_path = file_path
        # 如果文件不存在则创建空文件
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _load_data(self) -> List[Dict]:
        """从文件加载数据"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def _save_data(self, data: List[Dict]) -> None:
        """保存数据到文件"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_entry(self, usr_id: str, qq_id: str, link_time: str, b_dislink: int = 0) -> bool:
        """
        添加新的用户QQ关联记录
        :param usr_id: 用户ID（字符串）
        :param qq_id: QQ号码（字符串）
        :param link_time: 关联时间（字符串）
        :param b_dislink: 是否解除关联（0或1，默认为0）
        :return: 添加成功返回True，失败返回False
        """
        # 验证b_dislink的值
        if b_dislink not in (0, 1):
            return False

        # 验证所有字符串字段
        if not all(isinstance(field, str) for field in [usr_id, qq_id, link_time]):
            return False

        data = self._load_data()
        
        # 检查是否已存在相同的usr_id和qq_id组合（防止重复）
        for entry in data:
            if entry['usr_id'] == usr_id or entry['qq_id'] == qq_id:
                return False

        # 添加新记录
        new_entry = {
            'usr_id': usr_id,
            'qq_id': qq_id,
            'link_time': link_time,
            'b_dislink': b_dislink
        }
        data.append(new_entry)
        self._save_data(data)
        return True

    def find_entries(self, column: str, value: str or int) -> List[Dict]:
        """
        根据指定列和值查找记录（忽略b_dislink为0的记录）
        :param column: 列名（usr_id, qq_id, link_time, b_dislink）
        :param value: 要匹配的值
        :return: 匹配的记录列表
        """
        # 验证列名是否有效
        valid_columns = ['usr_id', 'qq_id', 'link_time', 'b_dislink']
        if column not in valid_columns:
            print(f"错误：无效的列名。有效列名：{valid_columns}")
            return []

        data = self._load_data()
        results = []

        for entry in data:
            # 忽略b_dislink为0的记录
            if entry.get('b_dislink', 0) == 0:
                continue
                
            # 检查是否匹配
            if entry.get(column) == value:
                results.append(entry.copy())

        return results

    def modify_entry(self, search_column: str, search_value: str or int, 
                    modify_column: str, modify_value: str or int) -> bool:
        """
        修改符合条件的记录（忽略b_dislink为0的记录）
        :param search_column: 搜索列名
        :param search_value: 搜索值
        :param modify_column: 要修改的列名
        :param modify_value: 要修改的值
        :return: 修改成功返回True，否则返回False
        """
        # 验证列名是否有效
        valid_columns = ['usr_id', 'qq_id', 'link_time', 'b_dislink']
        if search_column not in valid_columns or modify_column not in valid_columns:
            print(f"错误：无效的列名。有效列名：{valid_columns}")
            return False

        # 如果修改的是b_dislink，验证值是否有效
        if modify_column == 'b_dislink' and modify_value not in (0, 1):
            print("错误：b_dislink必须是0或1")
            return False

        data = self._load_data()
        modified = False

        for entry in data:
            # 忽略b_dislink为0的记录
            if entry.get('b_dislink', 0) == 0:
                continue
                
            # 找到匹配的记录并修改
            if entry.get(search_column) == search_value:
                entry[modify_column] = modify_value
                modified = True

        if modified:
            self._save_data(data)
            return True
        return False

    def get_all_active_entries(self) -> List[Dict]:
        """获取所有未解除关联的记录（b_dislink不为0）"""
        data = self._load_data()
        return [entry.copy() for entry in data if entry.get('b_dislink', 0) != 0]


# 示例用法
def testfunc():
    # 创建管理器实例
    manager = UserQQManager("user_qq_links.json")
    
    # 添加示例数据
    manager.add_entry("user123", "123456789", "2023-01-01 10:00:00", 1)
    manager.add_entry("user456", "987654321", "2023-01-02 14:30:00", 1)
    manager.add_entry("user789", "567890123", "2023-01-03 09:15:00", 0)  # 这条会被忽略
    
    # 查找示例
    print("查找usr_id为user123的记录：")
    results = manager.find_entries("usr_id", "user123")
    for res in results:
        print(res)
    
    # 修改示例
    print("\n修改qq_id为987654321的link_time：")
    success = manager.modify_entry("qq_id", "987654321", "link_time", "2023-01-05 16:45:00")
    if success:
        print("修改成功")
        results = manager.find_entries("qq_id", "987654321")
        for res in results:
            print(res)
    else:
        print("修改失败")
    
    # 获取所有活跃记录
    print("\n所有活跃记录：")
    active_entries = manager.get_all_active_entries()
    for entry in active_entries:
        print(entry)
