# 诸子百家智囊团

基于 Python 3.12 与 CrewAI 的多智能体学习项目。用户提交一个问题，儒家、法家、道家、兵家四个智囊分别依据各自的思想框架给出建议。

## 功能

- 四个具有差异化立场的专家 Agent。
- CrewAI `Agent`、`Task`、`Crew` 与 `Process.sequential` 编排。
- 使用 Pydantic 定义结果模型。
- 输出目标长度为每家 50～100 个汉字，并要求采用总—分—总结构。
- 提供 CLI、Web UI、基础单元测试、Ruff 配置与 `.env.example`。

> 字数与文章结构通过提示词引导，并由程序做基础校验；大模型输出不保证每次都严格符合要求。项目会对字数异常发出警告，不会静默截断建议。

## 环境要求

- Python 3.12
- `uv`
- 可访问的模型 API 与对应 API Key

## 安装

```bash
uv sync --extra dev
cp .env.example .env
```

编辑 `.env`，配置模型提供商和密钥。例如，使用 OpenAI 兼容接口：

```dotenv
API_KEY=your-api-key
MODEL=qwen3.6-plus
BASE_URL=http://localhost:8000/v1
```

`MODEL` 使用 LiteLLM/CrewAI 支持的模型标识。不同提供商可能需要额外环境变量，具体请参照所用模型提供商及 CrewAI 文档。

## 运行

```bash
uv run hundred-schools "创业初期，应该优先追求增长还是控制风险？"
```

也可以交互式运行：

```bash
uv run hundred-schools
```

### Web UI

Web 界面为每家智囊提供独立的对话窗口，支持多轮追问，各学派对话历史互不影响。

```bash
uv run hundred-schools-web
```

启动后打开浏览器访问 `http://localhost:8000`。

## 开发与测试

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## 目录结构

```text
.
├── CLAUDE.md
├── pyproject.toml
├── README.md
├── .env.example
├── src/hundred_schools/
│   ├── agents/       # 专家 Agent 定义
│   ├── crews/        # Crew 编排
│   ├── tasks/        # Task 定义
│   ├── models/       # Pydantic 输出模型
│   ├── config.py
│   ├── main.py       # CLI 入口
│   ├── server.py     # Web UI 后端
│   └── static/       # Web UI 前端
│       └── index.html
└── tests/
```

## 设计边界

- CLI 使用顺序式执行，四家智囊分别完成建议任务。
- Web UI 为每家提供独立对话窗口，支持多轮追问，对话历史隔离。
- 暂不引入工具调用、RAG、长期记忆或多轮辩论。
- “诸子百家”的人物与思想设定是面向现代决策场景的概括，不代表对各学派思想的穷尽性解释。
