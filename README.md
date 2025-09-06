# Python 课程小组项目库

这是一个用于Python（英语）课程的小组项目库，我们将在这里进行协作开发和学习。

## 小组成员

| 姓名 | GitHub 用户名 |
|------|--------------|
| 游尹哲郡 | @LeoAndJellyfish |
| 李科翰 | @Sakura975 |
| 杨帆 | @YangFan |
| 马俊怡 | @Goodnight886 |
| 陈发英 | @FaEingChen |
| 李沛瑾 | @HaDock-Harriet |

## 项目目标

- 协作完成Python课程相关的编程任务和项目
- 学习和实践Python编程技能
- 通过团队合作提高软件开发能力
- 建立一个可维护和可扩展的代码库

## 项目结构

```
├── README.md          # 项目说明文档
├── requirements.txt   # 项目依赖清单
├── src/               # 源代码目录
│   ├── __init__.py
│   └── ...
├── tests/             # 测试代码目录
│   ├── __init__.py
│   └── ...
└── docs/              # 文档目录
    └── ...
```

## 环境设置

本项目使用 [uv](https://github.com/astral-sh/uv) 进行Python环境管理。

### 安装 uv

```bash
# Windows (PowerShell)
iwr -useb https://astral.sh/uv/install.ps1 | iex

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 创建虚拟环境

```bash
# 在项目根目录下创建虚拟环境
uv venv

# 激活虚拟环境
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 安装依赖

```bash
uv pip install -r requirements.txt
```

## 使用指南

1. 将项目克隆到本地
   ```bash
   git clone https://github.com/你的用户名/stunning-octo-dollop.git
   cd stunning-octo-dollop
   ```

2. 按照上面的环境设置步骤配置开发环境

3. 在 `src/` 目录下开始开发你的代码

4. 提交代码前，请确保你的代码符合项目的代码规范

## 贡献指南

1. 创建新的分支进行开发
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. 提交你的代码更改
   ```bash
   git add .
   git commit -m "描述你的更改"
   ```

3. 将你的分支推送到远程仓库
   ```bash
   git push origin feature/your-feature-name
   ```

4. 创建 Pull Request 请求合并你的代码

## 代码规范

- 遵循 PEP 8 代码风格指南
- 使用有意义的变量和函数名
- 添加适当的注释和文档字符串
- 确保代码可以正常运行并通过测试

## 联系方式

如有任何问题或建议，请联系小组成员。

---

最后更新："+new Date().toLocaleDateString('zh-CN')+"