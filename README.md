# 小说生成智能体框架

基于AI的智能小说生成系统，采用前后端分离架构，支持手动控制各个模块的生成过程。

## 功能特性

### 🎯 手动生成控制台
- **分步生成**: 按需生成世界观、角色、剧情大纲、章节大纲、事件和详细剧情
- **实时控制**: 手动控制每个模块的生成过程
- **进度监控**: 实时显示生成进度和状态
- **错误处理**: 完善的错误处理和重试机制

### 📚 核心模块
1. **世界观架构引擎** - 生成自洽的修仙宇宙设定
2. **角色管理引擎** - 创建有血有肉的角色
3. **剧情生成引擎** - 生成主线、支线剧情
4. **叙事逻辑与反思引擎** - 检查故事自洽性
5. **多维度评分模块** - 量化评估内容质量
6. **进化与重写引擎** - 驱动故事进化

## 技术架构

### 前端技术栈
- **React 18** - 用户界面框架
- **TypeScript** - 类型安全的JavaScript
- **Ant Design** - 企业级UI组件库
- **React Router** - 单页面应用路由
- **React Query** - 数据获取和状态管理
- **Vite** - 快速的前端构建工具

### 后端技术栈
- **Python 3.9+** - 主要编程语言
- **FastAPI** - 现代、快速的Web框架
- **Pydantic** - 数据验证和序列化
- **PostgreSQL 15+** - 关系型数据库
- **Redis** - 缓存和任务队列（可选）
- **psycopg2** - PostgreSQL 数据库驱动

## 快速开始

### 方式一：Docker Compose 部署（推荐）

最简单快速的部署方式，适合生产环境。

```bash
# 1. 配置环境变量
cp env.example .env
# 编辑 .env 文件，至少配置 AI API Key

# 2. 启动所有服务
docker-compose up -d

# 3. 访问系统
# 前端: http://localhost:3001
# 后端: http://localhost:8001
# API文档: http://localhost:8001/docs
```

详细部署说明请查看 [DEPLOYMENT.md](./DEPLOYMENT.md)

### 方式二：本地开发部署

适合开发和调试。

#### 1. 环境要求
- Python 3.9+
- Node.js 18+
- PostgreSQL 15+
- npm 或 yarn

#### 2. 安装依赖

**后端依赖**
```bash
cd backend
pip install -r requirements.txt
```

**前端依赖**
```bash
cd frontend
npm install
```

#### 3. 配置数据库

```bash
# 创建数据库
createdb novel_generate
createuser novel_user
psql novel_generate -c "ALTER USER novel_user WITH PASSWORD 'novel_password';"
psql novel_generate -c "GRANT ALL PRIVILEGES ON DATABASE novel_generate TO novel_user;"

# 初始化数据库表
psql -U novel_user -d novel_generate -f database/init_all_tables.sql
```

#### 4. 配置环境变量

```bash
cp env.example .env
# 编辑 .env 文件，配置数据库连接和 AI API Key
# 注意：本地开发时 DATABASE_URL 应使用 localhost
```

#### 5. 启动系统

**使用启动脚本（推荐）**
```bash
# 自动检测 Docker，优先使用 Docker Compose
./start.sh

# 或指定模式
./start.sh docker    # Docker Compose 模式
./start.sh local     # 本地开发模式
```

**手动启动**
```bash
# 启动后端
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 启动前端（新终端）
cd frontend
npm run dev
```

#### 6. 访问系统
- **前端界面**: http://localhost:3001
- **后端API**: http://localhost:8001
- **API文档**: http://localhost:8001/docs

## 使用指南

### 手动生成流程

1. **设置核心概念**
   - 在首页输入小说的核心概念
   - 例如："现代修仙者的都市生活"

2. **生成世界观**
   - 点击"世界观生成"按钮
   - 系统将生成修仙世界的完整设定

3. **生成角色**
   - 点击"角色生成"按钮
   - 系统将生成主角、配角、反派等角色

4. **生成剧情大纲**
   - 点击"剧情大纲"按钮
   - 系统将生成整体剧情结构

5. **生成章节大纲**
   - 点击"章节大纲"按钮
   - 系统将生成详细的章节规划

6. **生成事件序列**
   - 点击"事件生成"按钮
   - 系统将生成具体的事件序列

7. **生成详细剧情**
   - 选择要生成的章节
   - 选择要包含的事件（可选）
   - 点击"详细剧情"按钮

### API接口

#### 生成接口
- `POST /api/generate/worldview` - 生成世界观
- `POST /api/generate/characters` - 生成角色
- `POST /api/generate/plot-outline` - 生成剧情大纲
- `POST /api/generate/chapter-outline` - 生成章节大纲
- `POST /api/generate/events` - 生成事件序列
- `POST /api/generate/detailed-plot` - 生成详细剧情

#### 查询接口
- `GET /api/progress` - 获取生成进度
- `GET /api/chapters` - 获取可用章节
- `GET /api/events` - 获取可用事件
- `GET /api/health` - 健康检查

## 项目结构

```
novelGenerate/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── api/               # API 路由
│   │   ├── core/               # 核心模块
│   │   │   ├── character/      # 角色管理
│   │   │   ├── chapter_engine/ # 章节生成
│   │   │   ├── detailed_plot/  # 详细剧情
│   │   │   ├── event/          # 事件管理
│   │   │   ├── plot_engine/    # 剧情生成
│   │   │   ├── scoring/        # 评分系统
│   │   │   ├── world/          # 世界观生成
│   │   │   └── ...
│   │   ├── utils/              # 工具函数
│   │   └── main.py             # 主程序
│   ├── Dockerfile              # Docker 镜像配置
│   └── requirements.txt        # Python依赖
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── components/         # 组件
│   │   ├── pages/              # 页面
│   │   └── App.tsx             # 主应用
│   ├── Dockerfile              # Docker 镜像配置
│   └── package.json            # Node.js依赖
├── database/                   # 数据库脚本
│   ├── init_all_tables.sql     # 统一初始化脚本
│   └── *.sql                   # 其他 SQL 脚本
├── prompts/                    # 提示词模板
├── novel/                      # 生成的小说文件
├── docker-compose.yml          # Docker Compose 配置
├── env.example                 # 环境变量模板
├── start.sh                    # 启动脚本
├── DEPLOYMENT.md               # 部署文档
└── README.md                   # 项目说明
```

## 配置说明

### 环境变量
复制 `env.example` 为 `.env` 并配置必要的变量：

```bash
cp env.example .env
```

**必须配置的变量：**
- `ALIBABA_QWEN_API_KEY` 或 `AZURE_OPENAI_API_KEY` - AI 模型 API Key
- `DATABASE_URL` - 数据库连接字符串（Docker Compose 会自动配置）

**可选配置：**
- `LLM_PROVIDER` - LLM 提供商（azure 或 alibaba，默认 alibaba）
- `REDIS_URL` - Redis 连接（如果使用缓存）

详细配置说明请查看 `env.example` 文件。

### 自定义配置
- 修改 `backend/app/core/config.py` 调整系统配置
- 修改 `prompts/` 目录下的提示词模板
- 修改 `frontend/src/` 目录下的组件样式

## 故障排除

### 常见问题

1. **API调用失败**
   - 检查后端服务是否正常启动
   - 检查网络连接和端口占用
   - 查看控制台错误信息

2. **生成失败**
   - 检查LLM API配置是否正确
   - 检查环境变量是否设置
   - 查看后端日志获取详细错误信息

3. **前端页面无法访问**
   - 检查前端服务是否正常启动
   - 检查端口3001是否被占用
   - 清除浏览器缓存

4. **数据库连接失败**
   - 检查 PostgreSQL 服务是否运行
   - 检查 `DATABASE_URL` 配置是否正确
   - 确认数据库已初始化（执行 `init_all_tables.sql`）

5. **Docker 部署问题**
   - 查看服务日志：`docker-compose logs -f`
   - 检查端口是否被占用
   - 确认 `.env` 文件已正确配置

### 日志查看
- 后端日志：控制台输出
- 前端日志：浏览器开发者工具
- 生成文件：`novel/` 目录

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。