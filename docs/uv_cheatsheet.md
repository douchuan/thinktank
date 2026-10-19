# uv 常用命令手册

适用场景：macOS / Linux、Python 3.12、AI Agent 与 CrewAI 项目

官方文档：[uv 官方文档](https://docs.astral.sh/uv/?utm_source=chatgpt.com) · [CLI 命令完整参考](https://docs.astral.sh/uv/reference/cli/?utm_source=chatgpt.com)。

这份手册按日常开发流程组织，优先介绍最常用的命令。uv 的项目模式会自动处理锁文件和环境同步，因此大多数时候不必手动激活虚拟环境。


## 1. 安装与版本管理

| 命令                         | 用途                    |
| -------------------------- | --------------------- |
| `brew install uv`          | macOS 通过 Homebrew 安装  |
| `uv --version`             | 查看 uv 版本              |
| `uv self update`           | 更新 uv 自身              |
| `uv python list`           | 查看可用的 Python 版本       |
| `uv python install 3.12`   | 安装 Python 3.12        |
| `uv python find 3.12`      | 查找 Python 3.12 的路径    |
| `uv python pin 3.12`       | 为当前项目固定 Python 版本     |
| `uv python uninstall 3.12` | 卸载 uv 管理的 Python 3.12 |

注意：`uv python uninstall` 用于卸载 uv 管理的解释器，不应当用它来卸载系统或 Homebrew 管理的 Python。

## 2. 创建项目

| 命令                             | 用途                   |
| ------------------------------ | -------------------- |
| `uv init my-project`           | 创建新 Python 项目        |
| `uv init --package my-project` | 创建适合构建和安装的包项目        |
| `uv init --bare my-project`    | 创建最精简的项目骨架           |
| `uv init`                      | 在当前目录初始化项目           |
| `uv sync`                      | 创建环境并同步依赖            |
| `uv sync --extra dev`          | 同步项目及名为 `dev` 的可选依赖组 |

## 3. 虚拟环境管理

| 命令                          | 用途                                |
| --------------------------- | --------------------------------- |
| `uv venv`                   | 创建 `.venv` 虚拟环境                   |
| `uv venv --python 3.12`     | 使用 Python 3.12 创建环境               |
| `uv venv .venv-dev`         | 创建指定名称的环境                         |
| `source .venv/bin/activate` | 激活虚拟环境                            |
| `deactivate`                | 退出虚拟环境                            |
| `uv run python --version`   | 查看项目实际使用的 Python 版本               |
| `uv run which python`       | 查看项目运行时的 Python 路径（macOS / Linux） |

项目模式推荐： 优先执行 `uv sync`，让 uv 自动创建和维护 `.venv`。只有在需要手动控制环境时才直接使用 `uv venv`。

## 4. 依赖管理

这是日常开发中最重要的一组命令。

| 命令                    | 用途                  |
| --------------------- | ------------------- |
| `uv add requests`     | 添加运行时依赖             |
| `uv add crewai`       | 添加 CrewAI           |
| `uv add --dev pytest` | 添加开发依赖              |
| `uv remove requests`  | 移除依赖                |
| `uv sync`             | 同步项目依赖              |
| `uv sync --locked`    | 要求锁文件已是最新，否则报错      |
| `uv lock`             | 生成或更新锁文件            |
| `uv lock --upgrade`   | 更新依赖解析，尝试升级到允许的最新版本 |
| `uv tree`             | 查看依赖树               |
| `uv tree --outdated`  | 查看有更新版本的依赖          |
| `uv pip list`         | 查看当前环境安装的包          |
| `uv pip show crewai`  | 查看指定包的详细信息          |

例如，为项目添加 FastAPI 和开发依赖：

```
uv add fastapi
uv add --dev httpx
uv sync
```

`uv add` 会更新 `pyproject.toml`，并同步锁文件和环境；通常不需要额外再运行一次 `uv sync`。


## 5. 运行程序与脚本

| 命令                                     | 用途             |
| -------------------------------------- | -------------- |
| `uv run python main.py`                | 运行 Python 程序   |
| `uv run pytest`                        | 运行测试           |
| `uv run ruff check .`                  | 检查代码规范         |
| `uv run ruff format .`                 | 格式化代码          |
| `uv run mypy src/`                     | 执行类型检查         |
| `uv run -- python -c "print('hello')"` | 执行一段 Python 代码 |
| `uv run --no-sync python main.py`      | 不同步环境，直接运行程序   |
| `uv run --locked pytest`               | 锁文件过期时拒绝执行测试   |

针对诸子百家项目，常用命令如下：

```
# 运行智囊团
uv run hundred-schools "如何管理团队？"

# 运行测试
uv run pytest

# 检查代码
uv run ruff check .

# 检查格式是否符合规范
uv run ruff format --check .
```

`uv run` 不只是简单地调用 Python，它还会检查项目环境是否需要同步。`--no-sync` 可以跳过同步，但前提是当前环境已经准备好。


## 6. 锁文件与团队协作

`uv.lock` 的作用是记录解析后的依赖版本，帮助不同开发者和 CI 环境复现一致的依赖组合。

| 命令                                    | 用途                  |
| ------------------------------------- | ------------------- |
| `uv lock`                             | 更新锁文件               |
| `uv lock --check`                     | 检查锁文件是否为最新状态        |
| `uv sync --locked`                    | 锁文件不匹配时直接报错         |
| `uv sync --frozen`                    | 使用现有锁文件，不更新锁文件      |
| `uv export --format requirements.txt` | 导出 requirements.txt |
| `uv tree`                             | 查看依赖关系              |

建议团队开发时遵循：

- 将 `pyproject.toml` 和 `uv.lock` 提交到 Git。
- 不要提交 `.venv/`。
- 修改依赖后，检查锁文件是否同步更新。
- 在 CI 中使用 `uv sync --locked`，避免构建时意外修改锁文件。

注意，`--locked` 与 `--frozen` 不完全相同：前者会检查锁文件是否过期，后者则直接信任现有锁文件。

## 7. 工具安装与临时运行

uv 还可以代替部分 `pipx` 工作流，安装或临时运行独立的 Python 命令行工具。

| 命令                       | 用途                |
| ------------------------ | ----------------- |
| `uvx ruff check .`       | 在临时工具环境中运行 Ruff   |
| `uv tool install ruff`   | 安装 Ruff 作为全局命令行工具 |
| `uv tool list`           | 查看已安装工具           |
| `uv tool upgrade ruff`   | 更新指定工具            |
| `uv tool upgrade --all`  | 更新所有已安装工具         |
| `uv tool uninstall ruff` | 卸载指定工具            |

区别在于：

- `uv add --dev ruff`：将 Ruff 纳入当前项目的开发依赖，便于团队复现。
- `uv tool install ruff`：将 Ruff 安装为独立的全局工具。
- `uvx ruff`：临时运行工具，不要求将其加入当前项目依赖。

项目开发优先使用第一种；临时检查或个人全局工具可以使用后两种。

## 8. 传统 pip 工作流兼容命令

如果你维护的是尚未采用 `pyproject.toml` 项目模式的旧项目，可以使用 uv 的 pip 兼容接口。

| 命令                                                   | 用途             |
| ---------------------------------------------------- | -------------- |
| `uv pip install requests`                            | 安装 Python 包    |
| `uv pip install -r requirements.txt`                 | 按依赖清单安装        |
| `uv pip uninstall requests`                          | 卸载包            |
| `uv pip list`                                        | 列出已安装包         |
| `uv pip freeze`                                      | 导出当前环境的包版本     |
| `uv pip compile requirements.in -o requirements.txt` | 解析并生成锁定的依赖清单   |
| `uv pip sync requirements.txt`                       | 将环境同步到清单指定的包集合 |

这些命令适合传统的 `requirements.txt` 工作流。对于新项目，建议优先采用 `uv add`、`uv sync` 和 `uv.lock`，不要同时维护两套依赖管理方式。


## 9. 一页速查：最值得记住的 12 条命令

```bash

# 检查 uv 是否安装
uv --version

# 安装 Python 3.12
uv python install 3.12

# 固定项目 Python 版本
uv python pin 3.12

# 创建新项目
uv init my-project

# 安装并同步项目依赖
uv sync

# 添加项目依赖
uv add requests

# 添加开发依赖
uv add --dev pytest

# 移除项目依赖
uv remove requests

# 运行程序
uv run python main.py

# 运行测试
uv run pytest

# 查看依赖树
uv tree

# 严格按最新锁文件同步
uv sync --locked

```

最后记住这条核心工作流即可：

新项目

`uv init` → `uv add` → `uv run`

已有项目

`uv sync` → `uv run` → `uv lock`

团队协作

提交 `pyproject.toml` 和 `uv.lock`，用 `uv sync --locked` 验证环境。

完整命令可随时查阅 [uv 官方 CLI 参考手册](https://docs.astral.sh/uv/reference/cli/?utm_source=chatgpt.com)。