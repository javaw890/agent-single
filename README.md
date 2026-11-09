# agent-single

基于 LangChain / LangGraph + DeepSeek 的**元数据知识库**问答项目：把业务数仓的表结构、字段含义、同义词别名沉淀成可检索的知识库，让自然语言问题能准确落到表和字段上。

> **当前状态：知识库搭建已完成大部分，检索与问答链路仍需完善。**
>
> 已完成：元数据配置、向量化写入、ES / Qdrant 双路检索的基础设施。
> 待完善：检索召回效果调优、结果融合重排、问答智能体编排、评测与兜底策略。

## 技术栈

| 分类 | 选型 |
|---|---|
| 语言 / 包管理 | Python 3.11 + uv |
| Web 服务 | FastAPI |
| 大模型 | DeepSeek（langchain-deepseek） |
| 编排 | LangChain 1.x / LangGraph |
| 向量库 | Qdrant（1024 维） |
| 全文检索 | Elasticsearch 8.x |
| 元数据库 | MySQL 8.0（asyncmy + SQLAlchemy 2.0） |
| Embedding | BAAI/bge-large-zh-v1.5（本地部署） |
| 中文分词 | jieba |
| 配置 | OmegaConf |
| 日志 | loguru |

## 目录结构

```
secodezhanggui/
├── app/
│   ├── clients/            # ES / MySQL / Qdrant / Embedding 客户端管理
│   ├── conf/               # 配置加载（app_config / meta_config）
│   ├── core/               # 上下文与日志
│   ├── models/             # 数据模型
│   ├── respsitionries/     # 仓储层（待补充）
│   ├── scripts/            # 构建脚本
│   │   └── build_meta_knowledge.py   # 元数据知识库构建入口
│   └── services/
│       └── meta_knowledge_service.py # 元数据知识服务
├── conf/
│   ├── app_config.yaml     # 服务、数据库、向量库连接配置
│   ├── meta_config.yaml    # 表 / 字段 / 别名定义（知识库的源数据）
│   └── text_config.yaml    # 配置类定义
├── docker/                 # 依赖服务编排
│   ├── docker-compose.yaml # MySQL + Elasticsearch + Kibana
│   ├── elasticsearch/      # ES 镜像（含中文分词插件）
│   ├── mysql/              # 初始化 SQL（meta / dw 库）
│   └── embedding/          # bge-large-zh-v1.5 模型（已 gitignore）
├── src/secodezhanggui/     # 包入口
├── pyproject.toml
└── uv.lock
```

## 快速开始

### 1. 起依赖服务

```bash
cd docker
docker compose up -d
```

MySQL 端口 `3307`（root / atguigu，密码见 `docker-compose.yaml`），ES 端口 `9200`，Kibana 端口 `5601`。

### 2. 准备 embedding 模型

`docker/embedding/bge-large-zh-v1.5` 体积过大未入库，需要自行下载：

```bash
# 方式一：huggingface-cli
huggingface-cli download BAAI/bge-large-zh-v1.5 --local-dir docker/embedding/bge-large-zh-v1.5
```

### 3. 安装依赖

```bash
uv sync
```

### 4. 构建元数据知识库

```bash
uv run python -m app.scripts.build_meta_knowledge
```

## 配置说明

`conf/app_config.yaml` 是主配置：数据库连接、Qdrant / ES 地址、embedding 服务地址、LLM 模型与 API Key。

`conf/meta_config.yaml` 是知识库的源数据：按「表 → 字段 → 别名」组织，每个字段带 `role`（primary_key / dimension / measure）和 `alias`（中文同义词，用于召回），`sync` 控制是否同步进检索库。

## TODO

- [ ] 检索召回效果调优（Top-K、阈值、embedding 模型选型）
- [ ] ES + Qdrant 双路召回的结果融合与重排
- [ ] 假设性文档（HyDE）与查询改写
- [ ] 问答智能体编排（意图识别 → 检索 → 生成 → 兜底）
- [ ] 评测集与准确率 / 幻觉率指标
- [ ] 仓储层（respsitionries）补全与接口封装

## License

个人学习项目，未指定开源协议。
