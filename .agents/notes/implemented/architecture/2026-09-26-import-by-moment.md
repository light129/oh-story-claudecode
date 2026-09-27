# Agent Note: 导入按作者时刻分文件加载，作者决定落盘到导入记录

Status: implemented
Date: 2026-09-26
Related: [35K 加载上限](2026-09-26-per-call-load-ceiling-35k.md)、`skills/story-long-write/references/workflow-setup.md` 开头的开书时刻表

## Problem

story-import 的入口 SKILL.md 有 20.3K（去空白字数），从确认来源到最后汇报每一步都常驻：

- 流程答疑、旧追踪迁移、超过 200 章这类只在特定情况用的节（约 1.8K）写在入口里；追踪初始化读整份 tracking-transaction.md（7.7K），其中过半是续写时的逐章事务。
- 残稿怎么处理、要不要先装写作环境、原文怎么分卷，都写「记入上下文」：作者定下的事只在对话里，一换上下文就丢。
- 细纲从章节摘要逐章反推，不分批，模板写在入口；负载随章数线性增长，长书只能在一个上下文里硬扛。
- 入口重抄了 long-analyze 的拆文库结构与 Stage 0-6 流程（约 2.2K），又与自家 references 重复了细纲模板、追踪步骤和一份参考资料索引。
- 结构迁移（长篇）时刻要读入口 + structure-mapping-long + 追踪三份，约 40.4K；深度分析时刻入口 + long-analyze 入口与 pipeline-ops 约 36.2K，都超过 35K 上限。
- 入口对作者说「部署 hooks/agents/AGENTS」，作者看不懂。

## Decision

- 入口 SKILL.md 只留角色、Agent 兼容性、名词边界、时刻表与交接规则、Phase 1 的五个 Step 和每个时刻的指路（6.0K）。时刻表：Phase 1 确认来源与范围 → Phase 2 深度分析 → Phase 3 结构迁移（长篇末尾逐批反推细纲）→ Phase 4 追踪初始化（仅长篇）→ Phase 5 汇报与激活，每行写明作者确认什么、读什么、落盘到哪。
- 时刻之间只靠落盘文件交接。Phase 1 建立 `{书目录}/.story/work/导入记录.md`：原文位置、篇幅、范围、最后一章状态与残稿决定、题材与平台、外部对标、写作环境、卷划分、作者交代，以及各时刻进度勾选。每个时刻开头先读它，交付前写回；贴入的原文同时存到同目录。作者说「继续导入」时从第一个未勾的进度接着做。导入记录里的作者交代在结构迁移时写进 `设定/题材定位.md` 新增的「作者已定」小节（短篇写进续写基线），续写时也看得到。
- 深度分析、每批细纲、追踪初始化读得多：每个时刻交付后建议作者新开对话说「继续导入」。
- 新增时刻文件：`deep-analysis.md`（只写导入场景怎么驱动 long/short-analyze，结构、流程、恢复、质量都交回 analyze 自己）、`import-tracking.md`（初始化事务的语义准备、条目形状与容量、伏笔/时间线提取、验收，替代整读 tracking-transaction.md）、`import-report.md`（收尾自检、两份作者报告模板、激活）、`import-special-cases.md`（流程答疑、旧追踪迁移、超过 200 章）、`outline-reverse.md`（逐批细纲的编排）与 `outline-reverse-rules.md`（反推原则、字段映射、细纲模板，只作任务包正文）。
- structure-mapping-long.md 成为结构迁移时刻的唯一文件：开头加 10 步迁移步骤（原入口 Phase 3-L 的内容），卷划分是本时刻的作者确认点；追踪与细纲规则挪出。题材定位、对标同步、文风同步排在卷划分之前，让卷划分成为本时刻的收尾确认。structure-mapping-short.md 开头同样加迁移步骤。
- 细纲每批 10–20 章：新增 `skills/story-import/scripts/build_outline_brief.py --project {书目录} --chapters A-B`，把反推规则、本批每章的正文与摘要路径、按 `visible_chars_v1` 测好的历史长度（复用本 skill 自带的 wordcount_core，与写作时章节检查同口径）、卷纲「剧情单元（反推）」里与本批重叠的行拼成 `.story/work/排纲/导入细纲_第AAA-BBB章.md`。有 story-architect 时把包交给它（它没有执行命令的权限，所以长度由脚本先测），没有时主会话自己读包写本批；验收 `check-outline-contract.js` 由主会话跑。批大小超 20、非末批少于 10、超出已迁正文、没有卷纲都退出码 2。
- 守卫随内容移动改锚点，不删：作者报告模板检查从 SKILL.md（至少 1 块）改到 import-report.md（至少 2 块）；schema_version 锚点回归从 SKILL.md 改到 deep-analysis.md；story-setup 部署检查保留入口的「导入续写入口顺序」断言，另加特殊情况文件里的推荐顺序与只重建追踪、入口的导入记录、细纲分批四条；test-writer-pipeline.py 新增任务包的回归。

各时刻主会话规则部分（去空白字数）：确认来源 22.6K→8.3K；深度分析导入部分 20.3K→8.4K（连 long-analyze 入口与 pipeline-ops 36.2K→24.4K）；结构迁移长篇 40.4K→15.2K；细纲一批主会话 9.3K + 本批数据表；追踪初始化 12.0K；结构迁移短篇 27.8K→14.4K；汇报 29.4K→7.6K。

## Alternatives considered

- **只删入口的重复节，不拆时刻**：改动最小，入口能降到 11K 左右，也不引入新文件。但结构迁移仍要叠追踪三份，作者决定仍只在对话里，细纲仍不分批——换上下文照样丢信息，长书照样线性膨胀，所以不采用。
- **导入细纲直接复用 story-long-write 的 build_architect_brief.py**：同一个 story-architect、同一种任务包，维护一份脚本更省。但跨 skill 引用文件违反仓库规矩，而且导入是从摘要反推历史章、要带测好的长度，和开书往前设计细纲的流程与模板不同，所以本 skill 自带脚本。
- **导入记录写进拆文库或项目根**：拆文库是 analyze 的产物目录，混进导入进度会干扰它的旧成果识别；项目根可能同时有多本书。放在书目录的 `.story/work/` 与追踪事务、排纲任务包同处，和已有工作目录约定一致。
- **tracking-transaction.md 拆出初始化部分**：它是 story-long-write 的共享副本，改它要动三处副本与续写流程。导入需要的只是初始化字段、条目形状和容量，写进 import-tracking.md 更小；整份文件保留，排查报错时再查。

## Consequences

- 每个时刻主会话规则部分都在 35K 以内，最重的是结构迁移长篇 15.2K；细纲负载按批计，与全书章数无关。
- 作者在确认点定下的事（残稿、环境、卷划分、偏好红线）都落盘，换对话、隔天继续都能接上；「继续导入」成为新的入口话术。
- 行为变化：结构迁移里题材定位与对标同步提前到卷划分之前；追踪初始化从结构迁移里独立成 Phase 4、排在全部细纲之后；细纲从一次写完改为每批 10–20 章，没有子代理时每批都建议新开对话，长书的导入对话轮次变多。
- 代价：story-import 多了 6 个 reference 和 1 个脚本；import-tracking.md 摘录了 tracking-transaction.md 的初始化约束，追踪协议改容量或字段时要同步这里。
- story-import 还没有登记进 `scripts/doc-budget.json` 的路径预算，时刻加载目前靠本笔记的数字，未由 CI 锁住。
