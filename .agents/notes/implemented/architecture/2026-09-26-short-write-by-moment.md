# Agent Note: 短篇按作者时刻加载，构思与写正文靠设计文件交接

Status: implemented
Date: 2026-09-26
Related: [35K 加载上限](2026-09-26-per-call-load-ceiling-35k.md)、[开书按作者确认点分时刻](../../proposed/architecture/2026-09-26-opening-by-author-moments.md)、[短篇写前验收回归](../bug-fix/2026-09-24-short-write-precheck-regression.md)

## Problem

story-short-write 的构思（Phase 2）和写正文（Phase 3–4）默认在同一个上下文里做完：

- 构思读 workflow-design、writing-workflow、submission-craft、short-craft、short-reversal、题材包，可能再加反派与对标召回，本身 27.5–35K；接着写正文又读 workflow-draft、short-format、short-deslop、workflow-revision，并且入口规定每个阶段都要完整回读 short-craft 和题材包。同一对话累计约 42.6–60K，再加情感方法和钩子文件可到 68K。
- 写正文时刻的真实加载没登记：doc-budget 只有「短篇执行指令（入口+Phase 3/4，不含技法参考）」13.4K，写正文实际读的格式协议、通用底座、题材包、去味清单都不在内。单看写正文时刻，最重的题材包就有 34.1K，冷门题材读公式全文 35.8K，加反派与情感方法 39.3K，再加对标召回与两份钩子文件约 49K。
- 写正文依赖构思时读过的方法论：workflow-draft 让写作时再去 villain-and-reveal 查揭露方式、去 hooks-chapter / hooks-paragraph 选钩子、去 genre-writing-formulas 看题材、按 submission-craft 写导语、按 benchmark-recall / cross-book-recall 重新召回对标。这些在构思时已经做出决定，却没有要求写进设计文件，换上下文就得整份重读。作者口头定下的人称、偏好、红线也只在对话里。
- 规则打架：入口 Phase 3 完成门槛写「「像/好像/仿佛/如同」超过 10 处逐处复核功能，不机械全删」，精修清单写「「像」全文不超 10 处」。
- 给作者看的话里要求直接「报告 `Fallback: ... -> solo`」「报告 `Notice: agents bundle 版本不匹配…`」，story-deslop 同样。

## Decision

- **三个作者时刻**：SKILL.md 首屏「写前必读」改为一张时刻表——定情绪（Phase 1，只读入口）→ 构思（Phase 2，读法不变）→ 写正文（Phase 3–4，workflow-draft 的写前加载 + workflow-revision），每行写明作者确认什么、读什么、落盘什么。check-reference-gates.js 钉的三条路由原样保留在首屏 12 行内。
- **交接只靠落盘**：构思交付前把写正文要用的都写进 `设定.md`——基本信息加「平台基调」（取自 submission-craft 平台表）、新增「作者已定」（人称、偏好、红线、否掉的方案）、冷门题材把所用公式的情绪节拍、必选场景与规则要点写进「题材招式」区、揭露方式写进反派设计区；作者在确认点改的先写回两份文件并重跑构思门禁。writing-workflow 的「设定.md 内容构成」写明写正文只读它与小节大纲。
- **写正文不再依赖构思方法论**：workflow-draft 开头声明本时刻只靠落盘文件接上构思，反转、反派、揭露、付费点、平台基调都以两份设计文件为准，不重读 workflow-design、writing-workflow、short-reversal、submission-craft、villain-and-reveal 与公式全文；写前加载只剩 short-format、short-craft、设定.md 指定的一个题材包（冷门题材不读公式），写羁绊或余韵时按需读 emotional-methods。开篇钩子从本文件表或题材包「开篇范式」选，段落钩子按小节大纲「结尾承接/钩子」列落地，对标从「对标摘要」召回（正文阶段不新增副对标召回，与 cross-book-recall 正文阶段预算 0 一致），导语要点写进本文件不再指向 submission-craft。short-deslop 移到 Phase 4 去味时读，写作中的 AI 腔由完成门槛检测器兜底（与长篇主会话写正文同一做法）。
- **换上下文**：构思汇报末尾建议作者新开一个对话说「写正文」；新对话里两份设计文件已过构思门禁就直接进入写正文。作者要在本对话接着写也照做。写正文仍默认由主会话按批写完整篇（短篇一般一次写完），不拆成多次对话，也不默认交给 narrative-writer。
- **去重**：写正文时刻同时加载 short-craft、short-format 与 workflow-draft，workflow-draft 的九条「写作指令」和「场景信息揉进」段逐条复述 short-craft 第 2/3/10/11 节与 short-format 标点规则，改为一段指向加两条独有要求（不照搬大纲腔、情绪宁烈不温与任务卡点）；精修清单的「格式」六条改指 short-format 文末快速检查，「删减原则」前三条改指入口执行规则 3；格式规范从入口移到 workflow-draft 开头（构思时刻用不上）。
- **「像」裁定**：以入口为准——「像/好像/仿佛/如同」不成片堆叠，超过 10 处或检测器报比喻密度时逐处复核功能，有功能的留，不设全文硬上限、不机械全删；精修清单改成同一口径。检测器本来就按密度报提示，不按固定次数拦。
- **作者可见用语**：story-short-write 与 story-deslop 的 Agent 兼容与版本提示改为「一句白话告诉作者 + `Fallback` / `Notice` 原文只进最后一行「技术备注：」」，写法同 story-review；current-contract 守卫要求的锚文本保留。story-deslop 的润色结果模板末尾加技术备注行；短篇交付说明写明执行细节只进技术备注行。
- **守卫**：`check-reference-gates.js` 加钉——入口写明「交接只靠落盘」；workflow-draft 不再出现构思时刻的十份方法论文件名（旧版因含 villain-and-reveal.md 等失败）；workflow-design 模板含「平台基调」「作者已定」；workflow-revision 不得再出现「全文不超 10 处」。`check-current-skill-contracts.py` 新增 `author-note-preflight`：story-short-write 与 story-deslop 的入口不得出现「报告 `Fallback:` / 报告 `Notice:`」这种直接念给作者的写法，且必须有技术备注去向（两份旧入口都被拦下），`test-current-skill-contracts.py` 补正反例回归。
- **预算**：「短篇 Phase 2」改名「短篇构思（Phase 1–2，主会话）」，分支不变；「短篇执行指令」换成「短篇写正文（Phase 3–4，主会话）」，按题材包 × 去味由谁做 × 情感桥段登记 13 条分支，short-format、short-deslop、emotional-methods 补登文件预算。

各时刻主会话加载（去空白字数，不含设定/大纲等项目资料）：

| 时刻 | 之前 | 之后 |
|---|---|---|
| 构思 | 27.5–34.9K | 27.5–35.0K（内容多了交接字段，删掉等量重复） |
| 写正文（单独一个对话） | 未登记；实际 32.3–35.8K，加反派与情感 39.3K，加对标召回与钩子约 49K | 26.1K（冷门）–32.1K（最重题材包）；加情感桥段 31.9K（去味交给写手）/ 34.9K（主会话自己去味，最重组合） |
| 构思后同一对话接着写 | 约 42.6–60K，加情感与钩子到 68K | 仍会累计到约 46K 以上，所以在确认点建议新开对话 |

## Alternatives considered

- **短篇也做 story-architect 任务包**（像长篇 build_architect_brief.py 那样把构思交给架构师）：最强理由是构思是最重的时刻，交给子代理后主会话只和作者对话，加载最轻。不做：短篇构思本身已在 35K 内；构思是和作者来回确认故事核、人物、反转、付费点的过程，交出去作者就插不上话；题材包、submission-craft、workflow-design 都是 story-short-write 私有 references，要给架构师读就得把十个题材包同步进 agent-references，部署面和维护成本都大；现有「可 spawn 架构师辅助框架设计」保留为可选。
- **写正文默认交给 narrative-writer**：最强理由是写正文天然在新上下文里，主会话不用付写作手法。不做：写手按 agent-references 读长篇的 writing-craft，读不到 short-craft 与题材包，短篇腔调会漂；短篇一般一次写完，一个新对话就够隔开构思，不必多一层委派。用户明确要求或上下文不足时仍可派写手，规则不变。
- **只登记写正文的真实路径，不改流程**：最强理由是改动最小。不做：最重题材包加反派与情感方法已到 39K，冷门题材读公式全文 35.8K，不改依赖关系就只能删技法本身；同一对话的累计问题也不会变。
- **把导语挪到构思时刻、让作者先确认导语**：最强理由是导语是投稿门面，作者在构思确认点看一眼很自然。不做：导语就是正文开头几段，要和正文同一口气写；挪到构思会改变成稿形态，需要实测。本次只把导语要点写进 workflow-draft，不改写作顺序。
- **精修（Phase 4）也拆成单独时刻**：最强理由是写完初稿让作者先看再精修，加载更松。不做：现在精修是交付前的自动收尾，不是作者确认点；加一个确认点会多一轮来回，而写正文加精修已在 35K 内。

## Consequences

- 收益：写正文时刻有了登记的真实路径，每条 ≤35K；构思定下的事（含作者口头决定）都在 `设定.md`，换对话、隔天接着写都能接上；写正文少读约 5 份构思方法论；「像」只剩一个口径；作者看到的是白话，执行细节集中在最后一行技术备注。
- 行为变化（作者会感到的）：构思确认后会收到「建议新开对话说『写正文』」的建议；新对话里说「写正文」直接开写，不再重新构思；`设定.md` 多出「平台基调」「作者已定」，冷门题材的公式要点也写在里面；写羁绊或余韵时才会读情感方法；精修不再因为「像」超过 10 处就机械删。
- 代价：写正文不再预读 short-deslop，写作中只靠检测器兜住 AI 腔，Phase 4 去味照旧；冷门题材写正文依赖构思写进 `设定.md` 的公式要点，写得太简就会丢公式细节；workflow-draft 的写作指令改为指向 short-craft 各节，模型要真的读到那几节才生效。作者不换对话时累计仍会超 35K。最重组合余量 55 字、构思最重分支余量 36 字，后续改入口或 workflow 要同步删字。
- 未做实测：本次没有跑真实模型对照（额度与指令限制），行为以文本契约为准；复测建议在 v0.8 的短篇评测里用同一题材前提对比「同对话写完」与「新开对话写正文」的成稿与交付契约通过率。
