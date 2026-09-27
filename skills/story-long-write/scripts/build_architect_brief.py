#!/usr/bin/env python3
"""build_architect_brief.py — 把「出卷纲」「出一批细纲」这一时刻要用的流程与模板拼成任务包。

用法:
    python build_architect_brief.py --project <书目录> --task world
    python build_architect_brief.py --project <书目录> --task volume [--volume N]
    python build_architect_brief.py --project <书目录> --task outline --chapters A-B

开书与规划按作者确认点分时刻（见 references/workflow-setup.md）。卷纲与每批细纲最重，
有子代理时交给 story-architect 在新上下文里做：主会话只跑本脚本、把任务包路径交给它，
自己不读包里的内容。任务包写在书内 `.story/work/排纲/`，是这次任务的输入数据，不是 reference。

包里只有该时刻需要的东西：
- world：workflow-setup.md 的 Phase 2 与设定模板、character-basics.md、long-genre-mechanics.md 的
  「核心梗三层递进设计」、character-relations.md 的「人物关系类型」、reader-contract-and-progression.md。
- volume：workflow-volume.md（卷纲流程、排纲自查、节奏锚与对标迁移）、artifact-protocols.md
  （大纲与卷纲模板）、emotional-methods.md（排纲自查第 1 项）、reader-contract-and-progression.md
  （第 4 项契约四问）。
- outline：workflow-outline.md（批次步骤、细纲模板与验收、补纲、设定补全、排纲底稿模板）、
  character-basics.md 的主角卡与配角卡模板；首章在范围内时加 opening-design.md。
本书的方向、设定与作者口头定下的事都在 `设定/`，不进包，由执行者按包里的流程定点读。

stdout 输出一行 JSON：任务包路径、字数（去空白）、包含的资料。
Exit: 0 = 已写出；2 = 参数或资料缺失。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REFERENCES = Path(__file__).resolve().parent.parent / "references"
WORK_DIR = (".story", "work", "排纲")


def read_reference(name: str) -> str:
    path = REFERENCES / name
    if not path.is_file():
        raise SystemExit(f"ERROR: 缺少 reference：{path}")
    return path.read_text(encoding="utf-8").lstrip("﻿")


def section(text: str, start: str, end: str | None = None) -> str:
    """取 start 标题行到 end 标题行之前（end 省略则到文末）；找不到 start 就报错，不静默给空。"""
    match = re.search(rf"^#+\s*{re.escape(start)}.*$", text, re.M)
    if match is None:
        raise SystemExit(f"ERROR: reference 里找不到小节「{start}」")
    stop = re.search(rf"^#+\s*{re.escape(end)}.*$", text[match.end():], re.M) if end else None
    return text[match.start(): match.end() + stop.start() if stop else len(text)].rstrip()


def emit(text: str, stream) -> None:
    """统一按 UTF-8 写出：Windows 控制台默认 GBK/ASCII 时直接 print 中文会崩。"""
    stream.buffer.write((text + "\n").encode("utf-8"))
    stream.flush()


def weight(text: str) -> int:
    return len(re.sub(r"\s", "", text))


def build(task: str, volume: int | None, chapters: tuple[int, int] | None) -> tuple[str, list[str]]:
    if task == "world":
        head = ("# 任务包：出核心设定提案\n\n"
                "按下面 Phase 2 的流程，把核心设定写成文件：`设定/题材定位.md`（在定方向时已写的部分上补全，不删作者已定的内容）、"
                "`设定/关系.md`、主角与关键角色的 `设定/角色/{名}.md`、影响全书的 `设定/世界观/{主题}.md`。"
                "作者在定方向时说过的话都在 `设定/题材定位.md`，先读它；拿不准的写成二选一的候选留给作者定，不替作者拍板。"
                "不出卷纲、不写正文。不要另读本包以外的写作技法文件。交付后只回：写了哪些文件、主角与核心冲突各一句、"
                "要作者定的事（没有写「无」）。")
        setup = read_reference("workflow-setup.md")
        parts = [("workflow-setup.md（Phase 2 与设定模板）",
                  section(setup, "Phase 2：核心设定", "Agent 调用：story-architect + character-designer") + "\n\n"
                  + section(setup, "定设定时建的文件模板")),
                 ("character-basics.md", read_reference("character-basics.md")),
                 ("long-genre-mechanics.md（核心梗三层递进设计）",
                  section(read_reference("long-genre-mechanics.md"), "核心梗三层递进设计", "微创新与差异化设计")),
                 ("character-relations.md（人物关系类型）",
                  section(read_reference("character-relations.md"), "人物关系类型", "感情流人设核心法")),
                 ("reader-contract-and-progression.md", read_reference("reader-contract-and-progression.md"))]
    elif task == "volume":
        label = f"第{volume}卷" if volume else "本卷"
        head = (f"# 任务包：出{label}卷纲\n\n"
                f"只交付全书体量与阶段总览（`大纲/大纲.md`，已有就只补本卷相关部分）和 `大纲/卷纲_第{volume or 'X'}卷.md`，"
                "不出细纲、不写正文、不建 `追踪/`。本书方向、设定、对标登记与作者已定的事读 `设定/`（先读 "
                "`设定/题材定位.md`），不要另读本包以外的写作技法文件。交付后只回：写了哪些文件、排纲自查 1–4 "
                "的结论各一句、要作者定的事（没有写「无」）。")
        parts = [("workflow-volume.md", read_reference("workflow-volume.md")),
                 ("artifact-protocols.md", read_reference("artifact-protocols.md")),
                 ("emotional-methods.md", read_reference("emotional-methods.md")),
                 ("reader-contract-and-progression.md", read_reference("reader-contract-and-progression.md"))]
    else:
        first, last = chapters
        head = (f"# 任务包：出第{first}-{last}章细纲\n\n"
                f"只交付 `大纲/细纲_第{first:03d}章` 到第{last:03d}章，以及排纲底稿与必要的设定补全，不写正文、"
                "不建 `追踪/`。卷纲只用 `outline_view.py --unit {单元ID}` 取本单元闭包；设定从 `设定/` 定点读；"
                "不要另读本包以外的写作技法文件。每章落盘后按包里的验收命令检查。交付后只回：写了哪些文件、"
                "每章一句核心事件、要作者定的事（没有写「无」）。")
        basics = read_reference("character-basics.md")
        parts = [("workflow-outline.md", read_reference("workflow-outline.md")),
                 ("character-basics.md（主角卡、配角卡）", section(basics, "第1节：主角卡", "第3节"))]
        if first <= 3:
            parts.append(("opening-design.md", read_reference("opening-design.md")))
    skill_root = REFERENCES.parent
    body = [head + (f"\n\n包里命令的 `scripts/…` 与 `{{skill 根}}/scripts/…` 都指 `{skill_root / 'scripts'}`；"
                    "`{PYTHON}` 用本机可用的 python3（没有就 python）；`{书目录}` 是本书目录。")]
    for name, text in parts:
        body.append(f"\n---\n\n<!-- 资料：{name} -->\n\n{text.strip()}\n")
    return "\n".join(body), [name for name, _ in parts]


def parse_range(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d+)\s*(?:-\s*(\d+))?\s*", value or "")
    if not match:
        raise SystemExit("ERROR: --chapters 写成 A-B，如 1-10")
    first = int(match.group(1))
    last = int(match.group(2) or first)
    if first < 1 or last < first:
        raise SystemExit("ERROR: --chapters 范围无效")
    return first, last


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="拼出 story-architect 出卷纲/细纲的任务包")
    parser.add_argument("--project", required=True, type=Path, help="书目录")
    parser.add_argument("--task", required=True, choices=("world", "volume", "outline"))
    parser.add_argument("--volume", type=int, help="卷号（volume 任务）")
    parser.add_argument("--chapters", help="章节范围 A-B（outline 任务）")
    args = parser.parse_args(argv)
    try:
        if not args.project.is_dir():
            raise SystemExit(f"ERROR: 书目录不存在：{args.project}")
        chapters = parse_range(args.chapters) if args.task == "outline" else None
        if args.task == "outline" and chapters[1] - chapters[0] >= 10:
            raise SystemExit("ERROR: 一批细纲最多 10 章，拆成两批")
        text, included = build(args.task, args.volume, chapters)
    except SystemExit as exc:
        emit(str(exc), sys.stderr)
        return 2
    out_dir = args.project.joinpath(*WORK_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.task == "world":
        name = "核心设定.md"
    elif args.task == "volume":
        name = f"卷纲_第{args.volume}卷.md" if args.volume else "卷纲.md"
    else:
        name = f"细纲_第{chapters[0]:03d}-{chapters[1]:03d}章.md"
    out = out_dir / name
    out.write_text(text, encoding="utf-8")
    emit(json.dumps({"brief": str(out), "chars": weight(text), "includes": included}, ensure_ascii=False), sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
