# 项目详细结构设计

## 目录结构

```
visionscribe/
├── README.md                    # 项目说明文档
├── requirements.txt            # 依赖包列表
├── setup.py                    # 安装脚本
├── main.py                     # 主程序入口
├── project_structure.md        # 项目结构说明
├── .env.example               # 环境变量示例
├── .gitignore                 # Git忽略文件
│
├── src/                       # 源代码目录
│   ├── __init__.py
│   ├── main.py               # 主程序逻辑
│   ├── video_processor.py     # 视频处理模块
│   ├── text_extractor.py     # 文本提取模块
│   ├── text_deduplicator.py  # 文本去重模块
│   ├── ai_reconstructor.py   # AI重建模块
│   ├── output_generator.py   # 输出生成模块
│   └── models.py             # 数据模型定义
│
├── config/                    # 配置文件目录
│   ├── __init__.py
│   ├── ocr_config.py         # OCR配置
│   ├── ai_config.py          # AI模型配置
│   ├── video_config.py       # 视频处理配置
│   └── logging_config.py     # 日志配置
│
├── utils/                     # 工具函数目录
│   ├── __init__.py
│   ├── text_similarity.py    # 文本相似度计算
│   ├── file_utils.py         # 文件操作工具
│   ├── image_utils.py        # 图像处理工具
│   ├── text_utils.py         # 文本处理工具
│   └── video_utils.py        # 视频处理工具
│
├── tests/                     # 测试目录
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_video_processor.py
│   ├── test_text_extractor.py
│   ├── test_text_deduplicator.py
│   ├── test_ai_reconstructor.py
│   ├── test_output_generator.py
│   ├── test_integration.py
│   └── sample_data/          # 测试样本数据
│       ├── sample_video.mp4
│       ├── expected_output/
│       │   ├── project_structure/
│       │   └── documentation/
│
├── data/                      # 数据目录
│   ├── cache/                # 缓存数据
│   ├── logs/                 # 日志文件
│   ├── temp/                 # 临时文件
│   └── models/              # 模型文件
│
├── examples/                  # 示例代码
│   ├── basic_usage.py
│   ├── advanced_usage.py
│   ├── custom_config.py
│   └── batch_processing.py
│
├── scripts/                  # 脚本目录
│   ├── setup.sh              # 安装脚本
│   ├── run_tests.sh         # 运行测试脚本
│   ├── build.sh             # 构建脚本
│   └── deploy.sh            # 部署脚本
│
├── docs/                     # 文档目录
│   ├── api/                 # API文档
│   ├── user_guide/          # 用户指南
│   ├── developer_guide/     # 开发者指南
│   ├── architecture.md      # 架构设计
│   └── troubleshooting.md   # 故障排除
│
└── assets/                   # 资源文件
    ├── icons/               # 图标文件
    ├── templates/           # 模板文件
    └── samples/             # 样例文件
```

## 核心模块详细设计

### 1. 视频处理模块 (video_processor.py)

```python
class VideoProcessor:
    def __init__(self, config):
        self.config = config
        self.frame_cache = []
        
    def extract_frames(self, video_path, fps=1):
        """按指定FPS截取视频帧"""
        
    def filter_frames(self, frames):
        """过滤低质量帧"""
        
    def deduplicate_frames(self, frames, threshold=0.95):
        """去重相似帧"""
        
    def process_video(self, video_path):
        """完整视频处理流程"""
```

### 2. 文本提取模块 (text_extractor.py)

```python
class TextExtractor:
    def __init__(self, config):
        self.config = config
        self.ocr_engine = None
        
    def batch_ocr(self, frames):
        """批量OCR识别"""
        
    def clean_text(self, text):
        """清洗和格式化文本"""
        
    def extract_text_from_video(self, frames):
        """从视频帧中提取文本"""
```

### 3. 文本去重模块 (text_deduplicator.py)

```python
class TextDeduplicator:
    def __init__(self, config):
        self.config = config
        
    def cluster_texts(self, texts, threshold=0.8):
        """文本聚类"""
        
    def merge_duplicate_texts(self, clusters):
        """合并重复文本"""
        
    def extract_unique_content(self, texts):
        """提取唯一内容"""
```

### 4. AI重建模块 (ai_reconstructor.py)

```python
class AIReconstructor:
    def __init__(self, config):
        self.config = config
        self.ai_client = None
        
    def analyze_project_structure(self, texts):
        """分析项目结构"""
        
    def classify_files_by_content(self, texts):
        """文件内容分类"""
        
    def generate_file_contents(self, file_structure):
        """生成文件内容"""
        
    def create_project_hierarchy(self, project_structure):
        """创建项目目录结构"""
```

### 5. 输出生成模块 (output_generator.py)

```python
class OutputGenerator:
    def __init__(self, config):
        self.config = config
        
    def generate_codebase(self, project_data, output_dir):
        """生成代码库"""
        
    def generate_documentation(self, project_data, output_file):
        """生成文档"""
        
    def save_project_files(self, project_data, output_dir):
        """保存项目文件"""
```

## 数据模型设计

### models.py

```python
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Frame:
    id: int
    image_path: str
    timestamp: float
    text_content: str
    confidence: float

@dataclass
class TextBlock:
    id: int
    content: str
    confidence: float
    source_frames: List[int]
    category: str

@dataclass
class File:
    name: str
    path: str
    content: str
    file_type: str
    size: int

@dataclass
class Project:
    name: str
    structure: Dict[str, File]
    metadata: Dict[str, str]
    created_at: str

@dataclass
class ProcessResult:
    success: bool
    message: str
    project_data: Optional[Project]
    processing_time: float
    frame_count: int
    text_blocks: int
```

## 配置文件设计

### ocr_config.py

```python
CONFIG = {
    'languages': ['eng', 'chi_sim'],  # 支持语言
    'psm': 6,                        # 页面分割模式
    'oem': 3,                        # OCR引擎模式
    'min_confidence': 0.8,           # 最小置信度
    'whitelist': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,-_()[]{}:;#@$%^&*+=<>/\\!?\'" ',  # 白名单字符
    'blacklist': '',                # 黑名单字符
    'preprocessing': {               # 预处理设置
        'resize': True,
        'denoise': True,
        'threshold': True,
        'scale': 2.0
    }
}
```

### ai_config.py

```python
CONFIG = {
    'model': 'gpt-4',               # AI模型选择
    'temperature': 0.7,              # 温度参数
    'max_tokens': 4000,             # 最大token数
    'top_p': 0.9,                   # 核心采样参数
    'frequency_penalty': 0.1,       # 频率惩罚
    'presence_penalty': 0.1,        # 存在惩罚
    'api_key': None,                # API密钥（从环境变量读取）
    'timeout': 30,                  # 请求超时时间
    'max_retries': 3,               # 最大重试次数
    'system_prompt': """            # 系统提示词
        你是一个专业的代码重构专家，能够从视频截图和文本内容中重建项目结构。
        请仔细分析提供的文本内容，识别文件类型、目录结构，并生成相应的代码。
        
        输出格式：
        {
            "project_structure": {
                "directory1": {
                    "file1": "content",
                    "file2": "content"
                },
                "directory2": {
                    "file3": "content"
                }
            },
            "file_types": {
                "file1": ".py",
                "file2": ".js",
                "file3": ".md"
            }
        }
    """
}
```

### video_config.py

```python
CONFIG = {
    'fps': 1,                       # 截帧FPS
    'quality': 95,                 # 图像质量
    'frame_size': None,            # 帧大小（None保持原始大小）
    'skip_blurry': True,           # 跳过模糊帧
    'blur_threshold': 100,         # 模糊阈值
    'format': 'jpg',              # 图像格式
    'cache_frames': True,          # 缓存帧
    'max_frames': 1000,           # 最大帧数
    'temp_dir': './data/temp'     # 临时目录
}
```

## 工具函数设计

### text_similarity.py

```python
def calculate_similarity(text1, text2, method='cosine'):
    """计算文本相似度"""
    
def cluster_texts(texts, threshold=0.8, method='hierarchical'):
    """文本聚类"""
    
def extract_keywords(texts, max_keywords=20):
    """提取关键词"""
```

### file_utils.py

```python
def create_directory_structure(structure, base_path):
    """创建目录结构"""
    
def save_file_with_encoding(file_path, content, encoding='utf-8'):
    """保存文件（自动处理编码）"""
    
def get_file_type(filename):
    """获取文件类型"""
    
def estimate_file_size(content):
    """估算文件大小"""
```

### image_utils.py

```python
def is_blurry(image, threshold=100):
    """检测图像是否模糊"""
    
def preprocess_image(image, config):
    """预处理图像"""
    
def resize_image(image, size=None, maintain_aspect=True):
    """调整图像大小"""
```

### video_utils.py

```python
def extract_frames_ffmpeg(video_path, output_dir, fps=1):
    """使用FFmpeg提取帧"""
    
def get_video_info(video_path):
    """获取视频信息"""
    
def calculate_duration(video_path):
    """计算视频时长"""
```

## 测试设计

### test_video_processor.py

```python
def test_extract_frames():
    """测试帧提取功能"""
    
def test_filter_frames():
    """测试帧过滤功能"""
    
def test_deduplicate_frames():
    """测试帧去重功能"""
```

### test_text_extractor.py

```python
def test_batch_ocr():
    """测试批量OCR功能"""
    
def test_clean_text():
    """测试文本清洗功能"""
    
def test_extract_text_from_video():
    """测试从视频提取文本"""
```

### test_integration.py

```python
def test_full_pipeline():
    """测试完整处理流程"""
    
def test_end_to_end():
    """测试端到端功能"""
```

## 性能优化

1. **内存管理**
   - 使用生成器处理大文件
   - 及时清理临时文件
   - 实现缓存机制

2. **并行处理**
   - 多线程处理OCR识别
   - 多进程处理视频帧
   - 异步处理AI请求

3. **缓存机制**
   - 缓存处理后的帧
   - 缓存OCR结果
   - 缓存AI响应

4. **错误处理**
   - 重试机制
   - 日志记录
   - 异常恢复