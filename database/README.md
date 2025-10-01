# 世界观数据库管理

本文档说明如何设置和管理PostgreSQL数据库中的世界观数据。

## 数据库结构

### 主要表

1. **worldviews** - 世界观主表
   - 存储基本信息：ID、名称、描述、核心概念等
   - 包含创建时间、更新时间、版本等元数据

2. **power_systems** - 力量体系表
   - cultivation_realms: 修炼境界数组
   - energy_types: 能量类型数组  
   - technique_categories: 功法类别数组

3. **geographies** - 地理设定表
   - main_regions: 主要区域数组
   - special_locations: 特殊地点数组

4. **societies** - 社会组织表
   - organizations: 组织数组
   - social_system: 社会系统对象

5. **history_cultures** - 历史文化表
   - historical_events: 历史事件数组
   - cultural_features: 文化特色数组
   - current_conflicts: 当前冲突数组

6. **worldview_metadata** - 元数据表
   - 存储额外的元信息和备份数据

### 视图和函数

- **worldview_complete** - 完整世界观信息视图
- **insert_worldview_complete()** - 插入完整世界观数据的存储过程
- **update_worldview_complete()** - 更新完整世界观数据的存储过程

## 设置步骤

### 1. 安装PostgreSQL 17

```bash
# macOS (使用Homebrew)
brew install postgresql@17

# 启动PostgreSQL服务
brew services start postgresql@17

# 创建用户和数据库
createuser -s postgres
createdb novel_generate
```

### 2. 配置数据库连接

在 `.env` 文件中设置数据库连接：

```env
DATABASE_URL=postgresql://username:password@localhost:5432/novel_generate
```

### 3. 初始化数据库

```bash
# 进入数据库目录
cd database

# 完整初始化（推荐）
python manage_db.py full_init

# 或者分步执行
python manage_db.py create_db
python manage_db.py init_tables
python manage_db.py check_tables
```

### 4. 验证设置

```bash
# 测试连接
python manage_db.py test_connection

# 查看统计信息
python manage_db.py get_stats
```

## 使用方法

### Python代码中使用

```python
from backend.app.core.world.database import worldview_db

# 插入世界观数据
worldview_id = worldview_db.insert_worldview(worldview_data, created_by="user")

# 获取世界观数据
worldview = worldview_db.get_worldview(worldview_id)

# 搜索世界观
results = worldview_db.search_worldviews("修仙")

# 获取世界观列表
worldviews = worldview_db.get_worldview_list(limit=10)
```

### API接口

世界观数据会自动保存到数据库，无需额外操作。可以通过以下方式访问：

1. **创建世界观** - `POST /api/v1/world/create`
   - 数据会自动保存到PostgreSQL

2. **获取世界观** - `GET /api/v1/world/{worldview_id}`
   - 从数据库读取数据

3. **搜索世界观** - `GET /api/v1/world/search?q={query}`
   - 在数据库中搜索

## 数据库管理命令

```bash
# 查看帮助
python manage_db.py --help

# 创建数据库
python manage_db.py create_db

# 初始化表结构
python manage_db.py init_tables

# 检查表结构
python manage_db.py check_tables

# 测试连接
python manage_db.py test_connection

# 获取统计信息
python manage_db.py get_stats

# 删除所有表（谨慎使用）
python manage_db.py drop_tables

# 完整初始化
python manage_db.py full_init
```

## 数据查询示例

### SQL查询示例

```sql
-- 获取所有活跃的世界观
SELECT worldview_id, name, core_concept, created_at 
FROM worldviews 
WHERE status = 'active' 
ORDER BY created_at DESC;

-- 搜索包含特定关键词的世界观
SELECT worldview_id, name, description 
FROM worldviews 
WHERE name ILIKE '%修仙%' OR description ILIKE '%修仙%';

-- 获取完整的世界观信息
SELECT * FROM worldview_complete WHERE worldview_id = 'world_123';

-- 查询特定修炼境界
SELECT worldview_id, name, cultivation_realms 
FROM worldview_complete 
WHERE cultivation_realms @> '[{"name": "筑基"}]';

-- 统计各类型的世界观数量
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active,
    COUNT(CASE WHEN status = 'archived' THEN 1 END) as archived
FROM worldviews;
```

### JSON查询示例

```sql
-- 查询包含特定修炼境界的世界观
SELECT worldview_id, name 
FROM power_systems 
WHERE cultivation_realms @> '[{"name": "筑基"}]';

-- 查询包含特定能量类型的世界观
SELECT worldview_id, name 
FROM power_systems 
WHERE energy_types @> '[{"name": "灵气"}]';

-- 查询包含特定区域的世界观
SELECT worldview_id, name 
FROM geographies 
WHERE main_regions @> '[{"name": "中州"}]';

-- 查询包含特定组织类型的世界观
SELECT worldview_id, name 
FROM societies 
WHERE organizations @> '[{"type": "宗门"}]';
```

## 性能优化

### 索引

数据库已自动创建以下索引：

- 主键索引
- 外键索引
- JSONB字段的GIN索引
- 常用查询字段的B-tree索引

### 查询优化建议

1. 使用JSONB操作符进行JSON查询
2. 利用GIN索引进行JSON字段搜索
3. 使用视图 `worldview_complete` 获取完整数据
4. 合理使用LIMIT和OFFSET进行分页

## 备份和恢复

### 备份

```bash
# 备份整个数据库
pg_dump novel_generate > backup_$(date +%Y%m%d_%H%M%S).sql

# 备份特定表
pg_dump -t worldviews -t power_systems novel_generate > worldview_backup.sql
```

### 恢复

```bash
# 恢复数据库
psql novel_generate < backup_20241201_120000.sql
```

## 故障排除

### 常见问题

1. **连接失败**
   - 检查PostgreSQL服务是否运行
   - 验证连接字符串是否正确
   - 确认用户权限

2. **表不存在**
   - 运行 `python manage_db.py init_tables`
   - 检查SQL文件是否存在

3. **权限错误**
   - 确保数据库用户有足够权限
   - 检查表的所有者设置

### 日志查看

```bash
# PostgreSQL日志
tail -f /usr/local/var/log/postgresql@17.log

# 应用日志
tail -f logs/app.log
```

## 扩展功能

### 添加新字段

1. 修改 `init_worldview_tables.sql`
2. 更新 `WorldViewDatabase` 类
3. 运行数据库迁移

### 自定义查询

可以在 `WorldViewDatabase` 类中添加新的查询方法：

```python
def get_worldviews_by_cultivation_realm(self, realm_name: str):
    """根据修炼境界查询世界观"""
    # 实现逻辑
```

## 监控和维护

### 定期维护

```sql
-- 更新表统计信息
ANALYZE;

-- 重建索引
REINDEX DATABASE novel_generate;

-- 清理过期数据
DELETE FROM worldviews WHERE status = 'deleted' AND updated_at < NOW() - INTERVAL '30 days';
```

### 性能监控

```sql
-- 查看慢查询
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- 查看表大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```
