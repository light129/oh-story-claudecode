# agent-calls.md：spawn 子代理的调用方式

只在要 spawn 对应 agent 时读；主会话自己写正文、自己排纲时不读。何时调用由各流程文件决定，这里只放 prompt 与必须附带的内容。Antigravity 用 `invoke_subagent` + 同名 `TypeName`。

## story-architect：定设定、出卷纲、出一批细纲（换新上下文）

先跑 `{PYTHON} {skill 根}/scripts/build_architect_brief.py --project {书目录} --task world`（卷纲 `--task volume --volume {N}`，细纲 `--task outline --chapters {A-B}`，一批最多 10 章），只取输出里的任务包路径，不读包的内容。交接前确认作者在对话里定下的方向、偏好和否掉的方案都已写进 `设定/`。

Prompt：`项目目录：{dir}\n任务包：{任务包路径}\n先完整读取任务包，按包里的流程与模板完成；作者已定的方向、设定和要求都在 设定/，对话内容不会传给你\n交付后只回任务包开头要求的几项`

收回后主会话：设定提案拿给作者逐项确认，按作者意见改文件；卷纲跑 `outline_view.py --check {卷纲路径}`，细纲每章跑 `check-outline-contract.js`；失败把报错原样交回同一 agent 修一次。按 workflow-volume.md / workflow-outline.md 的汇报模板用故事话告诉作者，不转述任务包。

## story-architect、character-designer：题材定位与角色细化（可选）

定方向以和作者来回讨论为主，默认主会话自己做；复杂世界观、多线结构、强反转工程或作者明确要求时才派：
- `Agent(subagent_type: "story-architect", prompt: "项目目录：{dir}\n任务类型：题材定位\n查询参数：{作者选定的方向与对标信息}")`
- `Agent(subagent_type: "character-designer", prompt: "项目目录：{dir}\n任务类型：角色设定\n查询参数：{主角设定信息}")` — 辅助角色设定和语言风格档案

## consistency-checker：写正文后的事实核对

Prompt：`项目目录：{dir}\n检查范围：{本次写作的章节}\n检查类型：事实冲突+伏笔断线+角色属性不一致\n本章新增申报：{申报表原样粘贴，无则写 0}；同时核对正文有无未申报的跨章事实，逐处列原文和细纲出处。只读与新增项和本章出场角色相关的设定、角色卡与追踪条目。冲突按 S1-S4 报出`

## narrative-writer：审查+去AI味

Prompt：`项目目录：{dir}\n任务描述：审查+去AI味\n检查分工：你负责语义去味及原定自检；最终文件扫描由主会话执行\n检查范围：{本次写作的章节}\n文风路径：{设定/文风.md 全文路径}\nstyle_resolution：{与写作一致的裁决}\n作者偏好：{本章 query 命中的 prose_style/story_design 项}\nAI味等级：{轻度/中度/重度；未分级按轻度}\n删除优先：每条 AI 味项先判能否删除，删后不丢伏笔/钩子/角色/情节/必要信息的直接删，会丢才润色\n按你的 7 Gate 与对话自检执行，台词里的工整否定不因脚本豁免而跳过\n删除测试：按 deslop-gates.md「写法抽查」执行，报告列候选数/删改数/保留理由`
