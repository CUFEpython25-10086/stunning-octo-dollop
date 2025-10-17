这是一个很棒的想法！开发一个能根据音乐情绪（如“伤心的钢琴旋律”）自动生成和弦走向、演奏建议甚至旋律片段的应用，需要精心设计 **Prompt（提示词）结构** 和 **格式化输出（Structured Output）**，以便模型稳定、一致地返回结构化数据，便于前端展示或后续处理（如 MIDI 生成、乐谱渲染等）。

下面我为你提供一套实用的设计方案，分为 **Prompt 设计** 和 **输出格式设计** 两部分，并附上示例。

---

## 一、Prompt 设计原则

目标：**引导大模型（如 GPT、Claude、本地 LLM）生成结构清晰、内容准确、风格统一的音乐建议。**

### 推荐 Prompt 模板：

```text
你是一位专业的作曲家兼钢琴教师。请根据用户指定的【音乐情绪主题】，生成一段适合钢琴演奏的和弦走向及相关创作建议。

要求如下：
1. 调性必须为自然小调或和声小调，以营造忧郁/伤感氛围；
2. 和弦走向应包含8小节以内，使用罗马数字或标准和弦标记（如 Am、F、C、G）；
3. 提供调性、建议速度（BPM）、和弦进行列表；
4. 附加演奏建议（左手织体、右手旋律思路、情感表达提示）；
5. 所有输出必须严格遵循以下 JSON 格式，不要包含任何额外文本。

【音乐情绪主题】：{{用户输入，如“伤心的钢琴旋律”}}

请直接输出 JSON，不要解释。
```

> ✅ 关键点：
> - 明确角色（专业作曲家）提升生成质量；
> - 限定调性、小节数、风格，避免随意发挥；
> - 强制结构化输出（JSON），便于程序解析；
> - 使用 `{{}}` 占位符，方便程序动态替换用户输入。

---

## 二、格式化输出设计（JSON Schema）

定义清晰的数据结构，确保前后端一致。

### 推荐 JSON 输出格式：

```json
{
  "theme": "伤心的钢琴旋律",
  "key": "A minor",
  "bpm": 65,
  "chord_progression": [
    "Am",
    "F",
    "C",
    "G",
    "Am",
    "Dm",
    "E7",
    "Am"
  ],
  "analysis": "以A小调为主，F与C带来短暂温暖回忆，E7制造张力后解决回Am，强化失落感。",
  "performance_tips": {
    "left_hand": "使用缓慢的分解琶音（低音-五度-三度-七度），每小节一个和弦，保持连贯。",
    "right_hand": "可叠加旋律音如 C–E–G–A，强调小七度（G）营造忧郁色彩。",
    "expression": "整体力度控制在 p 到 mp 之间，E7→Am 处可稍作渐慢（ritardando）增强情感张力。"
  }
}
```

### 对应的 JSON Schema（可用于验证）：

```json
{
  "type": "object",
  "properties": {
    "theme": {"type": "string"},
    "key": {"type": "string"},
    "bpm": {"type": "integer", "minimum": 40, "maximum": 120},
    "chord_progression": {"type": "array", "items": {"type": "string"}},
    "analysis": {"type": "string"},
    "performance_tips": {
      "type": "object",
      "properties": {
        "left_hand": {"type": "string"},
        "right_hand": {"type": "string"},
        "expression": {"type": "string"}
      },
      "required": ["left_hand", "right_hand", "expression"]
    }
  },
  "required": ["theme", "key", "bpm", "chord_progression", "analysis", "performance_tips"]
}
```

---

## 三、工程实现建议

### 1. 前端（用户输入）
- 用户输入框：`请输入音乐情绪（如：孤独的雨夜、离别的车站、深夜的思念...）`
- 提交后发送请求到后端 API

### 2. 后端（调用 LLM）
```python
# 伪代码示例（Python + OpenAI API）
prompt = f"""
你是一位专业的作曲家...（如上完整 prompt）
【音乐情绪主题】：{user_input}
请直接输出 JSON，不要解释。
"""

response = openai.ChatCompletion.create(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"}  # 强制 JSON 输出（GPT-4 支持）
)
```

> 💡 提示：使用 `response_format={"type": "json_object"}` 可大幅提高 JSON 合法性。

### 3. 客户端解析与展示
- 解析 JSON，渲染：
  - 调性 + BPM
  - 和弦走向（可做成可点击的和弦卡片）
  - 演奏建议分点展示
  - 甚至调用 Web Audio API 或 MIDI.js 播放示例

---

## 四、进阶扩展方向

- 支持用户指定调性（如“用 D 小调”）
- 增加“旋律生成”字段（返回音符序列，如 `[A4, C5, E5, G5]`）
- 输出 MusicXML 或 ABC Notation，供乐谱软件导入
- 添加“情绪强度”滑块（轻度忧伤 vs 深度悲痛）

---

## 总结

| 模块 | 关键设计 |
|------|--------|
| **Prompt** | 角色设定 + 约束条件 + 强制 JSON 输出 |
| **输出格式** | 结构化 JSON，含和弦、调性、BPM、演奏建议 |
| **工程实现** | 使用 LLM 的 JSON 模式 + 前端结构化解析 |
| **用户体验** | 可听、可看、可导出，增强互动性 |

如果你需要，我还可以帮你生成完整的 API 接口文档、前端组件代码，或适配特定 LLM（如 Claude、Llama 3）的 prompt 模板。欢迎继续提问！🎹