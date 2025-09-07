# VisionScribe 项目开发规范

## 1. 使用中文
- 所有文档、注释、日志输出使用中文
- 错误提示和用户界面使用中文
- 代码注释使用中文解释复杂的业务逻辑

## 2. 本项目功能说明
VisionScribe 是一个基于 AI 的视频转代码/文档转换工具，核心功能包括：
- 🎬 视频帧提取：从视频中提取带时间戳的关键帧
- 🔤 OCR 文字识别：从图像中提取文字内容
- 🧠 AI 智能分析：使用 AI 分析和去重提取的文字
- 💻 代码生成：根据分析结果生成可执行的项目文件
- 📄 文档生成：自动生成项目文档

## 3. 不同阶段的设计
### 4-Stage 工作流程

**阶段 1: 视频切片**
- 命令：`visionscribe slice`
- 功能：将视频切片为带时间戳的图片
- 输出：图片文件 + frames_metadata.json

**阶段 2: 读取文字**
- 命令：`visionscribe read`
- 功能：从图片中读取文字，生成结构化 JSON
- 输出：包含文字、置信度、位置信息的 JSON 文件

**阶段 3: AI分析**
- 命令：`visionscribe analyze`
- 功能：使用 AI 分析内容，去除重复文字
- 输出：经过 AI 处理的精简 JSON 数据

**阶段 4: 重建项目**
- 命令：`visionscribe rebuild`
- 功能：将分析结果重建为实际项目文件
- 输出：代码文件、文档文件、重建摘要

### 一键提取完整流程
**完整处理**
- 命令：`visionscribe extract`
- 功能：一键完成 slice → read → analyze → rebuild 的完整流程
- 输出：完整的项目文件和文档

## 4. Python 3 + 类型提示 + 代码风格

### Python 3 要求
- 必须使用 Python 3.11+
- 避免使用 Python 2.7 语法
- 使用现代 Python 特性

### 类型提示规范
```python
from typing import List, Dict, Optional, Union, Tuple
from pathlib import Path

def extract_frames(
    video_path: str, 
    fps: int, 
    output_dir: Optional[Path] = None
) -> List[Frame]:
    """
    从视频中提取帧
    
    Args:
        video_path: 视频文件路径
        fps: 提取帧率
        output_dir: 输出目录，默认为 None
    
    Returns:
        List[Frame]: 提取的帧列表
    """
    pass
```

### 代码风格规范
- 使用 `black` 格式化，行长度 88 字符
- 使用 `mypy` 进行类型检查
- 使用 `flake8` 进行代码质量检查
- 函数和类使用完整的类型提示
- 错误处理使用具体的异常类型

## 5. 使用 uv 管理

### 项目依赖管理
```bash
# 同步依赖
uv sync

# 开发依赖
uv sync --dev

# 添加新依赖
uv add package_name
uv add --group dev package_name
```

### uv 验证示例

#### 验证 CLI 命令可用性
```bash
# 在项目根目录下操作
cd /Users/zhihu/output/github/visionscribe

# 验证主命令
uv run visionscribe --help

# 验证特定命令
uv run visionscribe slice --help
uv run visionscribe read --help
uv run visionscribe analyze --help
uv run visionscribe rebuild --help
uv run visionscribe extract --help

# 直接运行模块
uv run python3 -m visionscribe.main --help

# 测试完整工作流
uv run visionscribe slice tests/examples/firstdemo.mov ./test_output --fps 2
uv run visionscribe read ./test_output/frames/ ./test_text.json
uv run visionscribe analyze ./test_text.json ./test_analysis.json
uv run visionscribe rebuild ./test_analysis.json ./test_project --format both
```

#### 开发环境验证
```bash
# 类型检查
uv run mypy src/

# 代码格式化
uv run black src/

# 代码质量检查
uv run flake8 src/

# 运行测试
uv run pytest tests/
```

### 避免 pip 安装问题
- 使用 `uv run` 而非 `pip install` 进行验证
- 在项目根目录下运行所有命令
- 使用 `python3` 明确指定 Python 版本（避免 Python 2.7）
- 不依赖全局包安装，使用 uv 的虚拟环境

## 项目结构约定
```
src/
├── visionscribe/
│   ├── main.py              # CLI 主入口
│   ├── video_processor.py   # 视频处理模块
│   ├── text_extractor.py    # OCR 文字提取
│   ├── text_deduplicator.py # 文字去重
│   ├── ai_reconstructor.py  # AI 重构
│   ├── output_generator.py  # 输出生成
│   └── models.py           # 数据模型
├── tests/                  # 测试文件
│   ├── examples/          # 演示和示例数据
│   │   └── workflow_demo/ # CLI 工作流演示
│   └── *.py               # 单元测试
└── README.md
```

### 测试和示例数据

#### CLI 工作流演示目录
`tests/examples/workflow_demo/` 包含完整的 4-Stage 工作流演示数据：

```bash
# 在项目根目录下测试工作流
cd /Users/zhihu/output/github/visionscribe

# 测试各个阶段
uv run visionscribe slice tests/examples/demo.mp4 ./demo_output --fps 2
uv run visionscribe read ./demo_output/frames/ ./demo_text.json
uv run visionscribe analyze ./demo_text.json ./demo_analysis.json
uv run visionscribe rebuild ./demo_analysis.json ./demo_project --format both
```

#### 演示文件结构
```
tests/examples/workflow_demo/
├── stage1/                # 视频切片结果
│   ├── frames/           # 切片图片
│   └── frames_metadata.json  # 切片元数据
├── stage2/                # 读取文字结果
│   └── text_data.json    # 文字识别结果
└── stage3/                # AI 分析结果
    └── ai_analysis.json   # AI 分析结果
```

#### 注意事项
- 所有测试数据都在 `.gitignore` 中，不会提交到 git
- 使用 `uv run` 进行测试，避免依赖全局安装
- 测试数据为模拟数据，用于验证 CLI 功能
- 演示使用 `firstdemo.mov` 作为示例视频文件