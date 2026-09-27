# 拆文产出怎么用

对标上下文要用 `拆文库/{书名}/` 的短篇拆文产出时读本文件；产出的文件树、`_meta.json` schema 与 Stage→文件映射见 [output-contract.md](output-contract.md)。

## 下游消费规范（story-short-write 怎么用）

> `story-short-write` 当前硬编码读 `拆文报告.md / 情节节点.md / 写作手法.md` 三个 markdown。
> `_meta.json` 是可选增强：read 容忍，不存在不阻塞写作。

| 文件 | 角色 | 怎么读 |
|------|------|--------|
| `_meta.json`（可选）| 数字门面 + 题材识别 | 看 `genre_detected` 决定哪个题材标尺，读 `structure_counts` 确认拆文完整性，读 `structure_counts.reversal_type` 选反转骨架 |
| `拆文报告.md` | 分析叙事主体 | 读「故事核」「结构」「情感曲线」「爆点」「反转分析」「人物」「五维评分」「共鸣分析」「可复用结构」「同类型写作动作」段，是 writer 的主输入 |
| `情节节点.md` | 节奏锚点 | 看每个节点的字数位置 + 功能 + 触发事件，给新故事排节奏 |
| `写作手法.md` | 手法库 | POV / 对话 / 时间 / 信息控制 等具体手法 + 原文示例，新篇里复用 |
| `原文/` | 语感源 | 抄对话调子、节奏、画面感、打脸张力。**不抄具体情节**，抄写法。 |

### 写作流程建议

1. 看 `_meta.json.genre_detected` 和 `structure_counts.reversal_type` 选骨架。
2. 读 `拆文报告.md` 的「核心手法」「共鸣分析」「可复用结构」段，决定要保留 / 调整哪些。
3. 读 `情节节点.md` 把节奏锚点抄到新故事的字数位置上。
4. 写场景时翻 `写作手法.md` + `原文/`，参考具体写法。
5. 写完后（可选）在新文档 frontmatter 写 `derived_from: 拆文库/{书名}/` 追溯。

### 维护者本地烟雾测试

维护者改拆文或写作契约后用，写作时跳过。

```bash
ls 拆文库/{书名}/   # 应有：原文/ 拆文报告.md 情节节点.md 写作手法.md _meta.json
/story-short-write 拆文库/{书名}/
# 通过：输出 8000+ 字同题材新短篇，prose 有源文对话节奏和画面感
# 失败：写得像填空 / 或 short-write 找不到三个 markdown
```
