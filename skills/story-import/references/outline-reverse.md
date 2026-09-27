# 逐批反推细纲（长篇导入）

卷纲写定后，从章节摘要反推每章细纲，**每批 10–20 章**，从第一个还没有细纲的章接着排。负载按批计，不随全书章数增长；进度记在导入记录（`{书目录}/.story/work/导入记录.md`）的「细纲：已完成第 A–B 章」。

## Step 1：生成本批任务包

按当前平台探测 Python 3（`python3` → `python` → `py -3`），运行：

```text
{PYTHON} {story-import skill 根}/scripts/build_outline_brief.py --project {书目录} --chapters {A-B}
```

脚本把本批要用的反推规则与模板（[outline-reverse-rules.md](outline-reverse-rules.md) 全文）、每章的正文与摘要路径、按 `visible_chars_v1` 测好的历史长度，以及卷纲「剧情单元（反推）」表里覆盖本批的行，拼成 `{书目录}/.story/work/排纲/导入细纲_第AAA-BBB章.md`，stdout 输出一行 JSON（`brief` 为任务包路径）。长度必须由脚本测：找不到 Python 3 或脚本退出码为 2 时返回 `TOOL_UNAVAILABLE`/报错原文并停止，不得用模型估算或静默跳过。卷纲缺失时脚本报错，先回结构迁移补卷纲。

## Step 2：写本批细纲

- **有 story-architect**（导入记录写着可用，按 SKILL.md 顶部的 Agent 兼容性检查 canonical 目录）：主会话只取任务包路径，不读包的内容。Prompt：`项目目录：{dir}\n任务包：{任务包路径}\n先完整读取任务包，按包里的规则与模板完成；作者已定的事在 .story/work/导入记录.md，对话内容不会传给你\n交付后只回任务包开头要求的几项`。Antigravity 用 `invoke_subagent` + `TypeName: "story-architect"`。
- **没有**：主会话完整读取任务包，自己按包写本批；不另读本文件以外的规则。

## Step 3：验收与交接

每批写完由主会话运行 `node {story-import skill 根}/scripts/check-outline-contract.js --json <本批细纲路径...>`：exit 1 时只按报告补缺的字段或小节（有 story-architect 时把报错原样交回同一 agent 修一次）。通过后更新导入记录的细纲进度。还有下一批时，向作者一句话说到第几章了，末尾按 [SKILL.md 的换上下文规则](../SKILL.md#时刻表与交接) 建议新开对话说「继续导入」；没有子代理时每批都这样建议。全部章节细纲写完再进 Phase 4。
