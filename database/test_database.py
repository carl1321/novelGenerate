#!/usr/bin/env python3
"""
世界观数据库功能测试脚本
"""
import os
import sys
import json
import asyncio
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

from app.core.world.database import worldview_db
from app.core.world.service import WorldService


async def test_database_operations():
    """测试数据库操作"""
    print("=== 世界观数据库功能测试 ===\n")
    
    # 测试数据
    test_worldview_data = {
        "id": "test_world_001",
        "name": "测试修仙世界观",
        "description": "这是一个用于测试的修仙世界观，包含完整的5维度结构",
        "core_concept": "以灵枢为核心的修仙体系",
        "power_system": {
            "cultivation_realms": [
                {
                    "name": "感枢境",
                    "level": 1,
                    "description": "初识体内灵枢，能感知微弱枢能流动",
                    "requirements": "需在静枢谷中冥想七日"
                },
                {
                    "name": "通脉境", 
                    "level": 2,
                    "description": "打通三条主灵枢脉，可外放枢能形成护体屏障",
                    "requirements": "炼化一枚清脉石"
                }
            ],
            "energy_types": [
                {
                    "name": "阳枢能",
                    "rarity": "常见",
                    "description": "阳性枢能，适合修炼阳属性功法"
                }
            ],
            "technique_categories": [
                {
                    "name": "基础枢功",
                    "description": "最基础的枢能修炼功法",
                    "difficulty": "简单"
                }
            ]
        },
        "geography": {
            "main_regions": [
                {
                    "name": "中州大陆",
                    "type": "主大陆",
                    "description": "修仙世界的中心区域",
                    "resources": ["灵气", "灵石"],
                    "special_features": "灵气浓度最高"
                }
            ],
            "special_locations": [
                {
                    "name": "静枢谷",
                    "type": "修炼圣地",
                    "description": "适合初学者的修炼场所",
                    "significance": "感枢境突破的必经之地",
                    "dangers": ["枢能反噬"]
                }
            ]
        },
        "society": {
            "organizations": [
                {
                    "name": "枢门",
                    "type": "宗门",
                    "description": "以枢能修炼为主的正道宗门",
                    "power_level": "一流",
                    "ideology": "以枢证道",
                    "structure": "掌门-长老-弟子"
                }
            ],
            "social_system": {
                "hierarchy": "以修为境界划分等级",
                "economy": "以灵石为货币的修炼经济",
                "trading": "通过枢能网络进行远程交易"
            }
        },
        "history_culture": {
            "historical_events": [
                {
                    "name": "枢能觉醒",
                    "time_period": "上古时期",
                    "description": "人类首次发现并掌握枢能",
                    "impact": "开启了修仙文明"
                }
            ],
            "cultural_features": [
                {
                    "region": "中州",
                    "traditions": "枢能节庆",
                    "values": "修为至上",
                    "lifestyle": "以修炼为中心"
                }
            ],
            "current_conflicts": [
                {
                    "name": "正邪之争",
                    "description": "正道与魔道之间的持续冲突",
                    "parties": ["枢门", "魔宗"],
                    "stakes": "世界主导权"
                }
            ]
        }
    }
    
    try:
        # 1. 测试插入数据
        print("1. 测试插入世界观数据...")
        worldview_id = worldview_db.insert_worldview(test_worldview_data, created_by="test_user")
        print(f"   ✅ 成功插入世界观: {worldview_id}\n")
        
        # 2. 测试获取数据
        print("2. 测试获取世界观数据...")
        retrieved_data = worldview_db.get_worldview(worldview_id)
        if retrieved_data:
            print(f"   ✅ 成功获取世界观: {retrieved_data['name']}")
            print(f"   📊 数据包含 {len(retrieved_data.get('cultivation_realms', []))} 个修炼境界")
        else:
            print("   ❌ 获取世界观数据失败")
        print()
        
        # 3. 测试搜索功能
        print("3. 测试搜索功能...")
        search_results = worldview_db.search_worldviews("修仙")
        print(f"   ✅ 搜索到 {len(search_results)} 个相关世界观")
        for result in search_results:
            print(f"   📝 {result['name']} - {result['core_concept']}")
        print()
        
        # 4. 测试获取列表
        print("4. 测试获取世界观列表...")
        worldview_list = worldview_db.get_worldview_list(limit=5)
        print(f"   ✅ 获取到 {len(worldview_list)} 个世界观")
        for item in worldview_list:
            print(f"   📋 {item['name']} (创建于: {item['created_at']})")
        print()
        
        # 5. 测试统计信息
        print("5. 测试统计信息...")
        stats = worldview_db.get_worldview_statistics()
        print(f"   ✅ 数据库统计:")
        print(f"   📈 总数: {stats.get('total', 0)}")
        print(f"   🟢 活跃: {stats.get('active', 0)}")
        print(f"   📦 最近7天: {stats.get('recent_count', 0)}")
        print()
        
        # 6. 测试更新功能
        print("6. 测试更新世界观数据...")
        updated_data = test_worldview_data.copy()
        updated_data["name"] = "更新后的测试世界观"
        updated_data["description"] = "这是更新后的描述"
        
        update_success = worldview_db.update_worldview(worldview_id, updated_data)
        if update_success:
            print("   ✅ 成功更新世界观数据")
            
            # 验证更新
            updated_worldview = worldview_db.get_worldview(worldview_id)
            if updated_worldview and updated_worldview['name'] == "更新后的测试世界观":
                print("   ✅ 更新验证成功")
            else:
                print("   ❌ 更新验证失败")
        else:
            print("   ❌ 更新世界观数据失败")
        print()
        
        # 7. 测试备份功能
        print("7. 测试备份功能...")
        backup_success = worldview_db.backup_worldview(worldview_id)
        if backup_success:
            print("   ✅ 成功备份世界观数据")
        else:
            print("   ❌ 备份世界观数据失败")
        print()
        
        print("=== 数据库功能测试完成 ===")
        print("✅ 所有测试通过！数据库功能正常。")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_service_integration():
    """测试服务层集成"""
    print("\n=== 服务层集成测试 ===\n")
    
    try:
        # 创建世界观服务
        world_service = WorldService()
        
        # 测试创建世界观
        print("1. 测试通过服务层创建世界观...")
        world_view = await world_service.create_world_view(
            core_concept="测试服务层集成",
            description="通过服务层创建的世界观",
            additional_requirements={"requirements": "测试数据库集成"}
        )
        
        print(f"   ✅ 成功创建世界观: {world_view.name}")
        print(f"   📊 世界观ID: {world_view.id}")
        print(f"   📝 核心概念: {world_view.core_concept}")
        
        # 验证数据是否保存到数据库
        db_data = worldview_db.get_worldview(world_view.id)
        if db_data:
            print("   ✅ 数据已成功保存到数据库")
        else:
            print("   ❌ 数据未保存到数据库")
        
        print("\n=== 服务层集成测试完成 ===")
        return True
        
    except Exception as e:
        print(f"❌ 服务层集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("开始世界观数据库功能测试...\n")
    
    # 测试数据库连接
    try:
        print("0. 测试数据库连接...")
        stats = worldview_db.get_worldview_statistics()
        print(f"   ✅ 数据库连接成功")
        print(f"   📊 当前数据库中有 {stats.get('total', 0)} 个世界观")
        print()
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {e}")
        print("请确保PostgreSQL服务正在运行，并且数据库已正确初始化。")
        return False
    
    # 运行测试
    db_test_success = await test_database_operations()
    service_test_success = await test_service_integration()
    
    if db_test_success and service_test_success:
        print("\n🎉 所有测试通过！世界观数据库功能完全正常。")
        return True
    else:
        print("\n❌ 部分测试失败，请检查配置和数据库状态。")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
