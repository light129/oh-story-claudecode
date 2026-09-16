# De-AI comparison — the deterministic checks in `/story-deslop`

[中文](README.md)

The local check in `story-deslop` is a **writing lint**. It does not guess whether a passage "feels
AI-written"; it matches known AI sentence templates one by one and returns the line, the matched
span and a rewrite direction. Blocking findings stop the write; advisory findings go to human judgement.

| File | What it is |
|---|---|
| [`改前.md`](改前.md) | A **hand-constructed** AI-flavored sample, written to show what the checker catches. Not skill output. |
| [`改后.md`](改后.md) | The same scene written clean, taken from the prose of [`第021章_离别开出花`](../长篇/让你管账号，你高燃混剪炸全网/正文/第021章_离别开出花.md). |
| This file | The full output of both real scans. |

Reproduce with:

```bash
node skills/story-deslop/scripts/check-ai-patterns.js --check --fail-on=blocking demo/去AI味对照/改前.md
```

## Scanning `改前.md`: 9 findings (7 blocking / 2 advisory), exit 1

| Line | Severity | Rule | Matched span |
|---|---|---|---|
| 3:1 | advisory | `cliche-density-tic` — 10 high-risk stock phrases (26.2 per 1k chars); do not rotate synonyms, replace with visible action, objects, dialogue and concrete consequence | 一丝 深吸一口气 仿佛 缓缓 轻轻 |
| 5:29 | blocking | `em-dash` — rewrite by function: interruption → action beat, drawn-out sound → ellipsis or action, parenthetical → comma/colon | 的告别意味着什么——不是遗憾，而是一 |
| 5:31 | blocking | `not-is-comparison` — high-frequency AI contrast template; drop the negative setup and write the second half directly | 不是遗憾，而是一种被时间掩埋的沉重 |
| 9:3 | blocking | `voice-contrast` — "voice was not loud… yet…"; drop the volume setup, write what the sound actually did to the room | 声音不高，却 |
| 11:1 | blocking | `negation-parade` — "no X, no Y…" parade; write what is actually there, keep at most one informative negation | 没有华丽的技巧，没有刻意的煽情， |
| 17:1 | advisory | `stock-reaction-tic` — fingertips / knuckles / throat / reddened eyes and similar generic reactions, 4 occurrences (10.5 per 1k); delete-test each one | 喉结滚动了一下 ｜ 指节攥紧了椅背 ｜ 抿了下唇 |
| 23:2 | blocking | `not-is-comparison` | 不是一场演出，而是一场迟到了四十年的仪式 |
| 31:6 | blocking | `trailer-ending` — chapter-trailer voice; end on a concrete action, image or line and let the event carry the suspense | 才刚刚开始 |
| 33:1 | blocking | `trailer-ending` | 没人知道 |

## Scanning `改后.md`: zero findings, exit 0

```
(no output)
```

## The two passages

| 改前 (blocked) | 改后 (shipped) |
|---|---|
| 这一刻，他终于明白了老人口中那场没能完成的告别意味着什么——不是遗憾，而是一种被时间掩埋的沉重。 | 前奏出来的时候，活动室里还有人在说话。<br>第三小节，说话的声音低下去了。<br>第一句唱出来，没人再出声。 |
| 他的声音不高，却像一把钝刀，缓缓割开了在场每一个人心里那道结痂了四十年的伤口。 | 到副歌，前排有个老人跟着哼了两声。<br>跑调跑得厉害，边上没人笑。 |
| 而这一切，才刚刚开始。<br>没人知道，这段被悄悄录下的视频，会在接下来的二十四小时里掀起怎样的惊涛骇浪。 | 护工小刘举着手机，站在活动室门口，从头到尾没放下来。<br>江晨看见了。<br>他没说话，也没走过去。 |

The two passages are nearly the same length (452 vs 497 characters). The difference is not brevity:
**the first tells the reader what to feel, the second hands the same beat to visible action and objects.**

> The checker only handles deterministic sentence and punctuation patterns; how a passage reads is
> still a human call. External AI detectors are a self-test reference, not the target of this check.
