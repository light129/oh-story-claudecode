#!/usr/bin/env python3
"""build_outline_brief.py — 拼出导入长篇「逐批反推细纲」的任务包。

用法:
    python build_outline_brief.py --project <书目录> --chapters A-B [--analysis <拆文库/导入书名>]

导入按作者时间线分时刻（见 SKILL.md「时刻表与交接」）。细纲按批反推，每批 10–20 章，负载不随全书
章数增长。有 story-architect 时主会话只跑本脚本、把任务包路径交给它（它没有执行命令的权限），
没有时主会话自己读包写本批。任务包写在书内 `.story/work/排纲/`，是这次任务的输入数据，不是 reference。

包里只有本批需要的东西：
- 反推规则与细纲模板：references/outline-reverse-rules.md 全文；
- 本批每章的正文路径、拆文库摘要路径，以及按 visible_chars_v1 测好的历史长度（与写作时
  章节检查同一口径，story-architect 不能自己跑测量）；
- 卷纲「剧情单元（反推）」表里与本批章节重叠的行。
本书设定与作者已定的事不进包，执行者按规则定点读项目文件与 `.story/work/导入记录.md`。

stdout 输出一行 JSON：任务包路径、字数（去空白）、本批每章长度、没找到摘要的章。
Exit: 0 = 已写出；2 = 参数错误、正文或卷纲缺失、长度测不出。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wordcount_core import METRIC, WordcountError, find_chapter_file, measure_wordcount  # noqa: E402

RULES = Path(__file__).resolve().parent.parent / "references" / "outline-reverse-rules.md"
WORK_DIR = (".story", "work", "排纲")
MIN_BATCH, MAX_BATCH = 10, 20
SPAN_RE = re.compile(r"(\d+)\s*(?:-|~|～|—|–|－|至|到)\s*(\d+)")


def emit(text: str, stream) -> None:
    """统一按 UTF-8 写出：Windows 控制台默认 GBK/ASCII 时直接 print 中文会崩。"""
    stream.buffer.write((text + "\n").encode("utf-8"))
    stream.flush()


def weight(text: str) -> int:
    return len(re.sub(r"\s", "", text))


def parse_range(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d+)\s*(?:-\s*(\d+))?\s*", value or "")
    if not match:
        raise SystemExit("ERROR: --chapters 写成 A-B，如 1-20")
    first = int(match.group(1))
    last = int(match.group(2) or first)
    if first < 1 or last < first:
        raise SystemExit("ERROR: --chapters 范围无效")
    return first, last


def last_body_chapter(project: Path) -> int:
    numbers = [int(m.group(1)) for p in (project / "正文").glob("第*章*.md")
               if "_原稿_" not in p.name and (m := re.match(r"^第0*(\d+)章", p.name))]
    return max(numbers, default=0)


def check_batch_size(first: int, last: int, final: int) -> None:
    size = last - first + 1
    if size > MAX_BATCH:
        raise SystemExit(f"ERROR: 一批细纲最多 {MAX_BATCH} 章，拆成两批")
    # 只有全书最后一批可以不足 10 章。
    if size < MIN_BATCH and last < final:
        raise SystemExit(f"ERROR: 一批细纲至少 {MIN_BATCH} 章（全书最后一批除外），把范围扩到第{first}-{min(final, first + MIN_BATCH - 1)}章")


def shown_path(path: Path, base: Path) -> str:
    """项目根下的路径写相对路径（story-architect 从项目根解析），在外面的写绝对路径。"""
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return str(path)


def measure(project: Path, chapter: int) -> tuple[Path, int]:
    try:
        body = find_chapter_file(project / "正文", chapter, outline=False)
        text = body.read_bytes().decode("utf-8")
    except (WordcountError, OSError, UnicodeError) as exc:
        raise SystemExit(f"ERROR: 第{chapter}章正文读不到（{exc}），先完成正文迁移")
    result = measure_wordcount(text, chapter=chapter)
    if result["status"] != "measured":
        raise SystemExit(f"ERROR: 第{chapter}章长度测不出（{result['invalid_reason']}）")
    return body, result["actual"]


def unit_rows(project: Path, first: int, last: int) -> list[str]:
    """从各卷纲的「剧情单元」表里取与本批章节重叠的行，连同表头。"""
    volumes = sorted((project / "大纲").glob("卷纲_第*卷.md"))
    if not volumes:
        raise SystemExit("ERROR: 大纲/ 下没有卷纲，先在结构迁移时刻写定卷纲")
    out: list[str] = []
    for volume in volumes:
        lines = volume.read_text(encoding="utf-8").splitlines()
        start = next((i for i, line in enumerate(lines) if re.match(r"^#+\s*剧情单元", line)), None)
        if start is None:
            continue
        table: list[str] = []
        for line in lines[start + 1:]:
            if line.lstrip().startswith("|"):
                table.append(line)
            elif table or line.strip():
                break  # 表格结束，或标题下先出现了非表格内容
        if len(table) < 3:
            continue
        hits = []
        for row in table[2:]:
            cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
            span = next((SPAN_RE.search(cell) for cell in cells[1:2] + cells if SPAN_RE.search(cell)), None)
            if span and int(span.group(1)) <= last and int(span.group(2)) >= first:
                hits.append(row)
        if hits:
            out += [f"来源：`{project.name}/大纲/{volume.name}`", "", *table[:2], *hits, ""]
    if not out:
        raise SystemExit(f"ERROR: 卷纲「剧情单元」表里找不到覆盖第{first}-{last}章的行（章节范围写成「第X-Y章」），先补卷纲")
    return out


def build(project: Path, analysis: Path, first: int, last: int) -> tuple[str, dict[int, int], list[int]]:
    if not RULES.is_file():
        raise SystemExit(f"ERROR: 缺少 reference：{RULES}")
    lengths: dict[int, int] = {}
    missing: list[int] = []
    rows = ["| 章 | 正文 | 摘要 | 字数目标（visible_chars_v1） |", "|---|---|---|---|"]
    for chapter in range(first, last + 1):
        body, actual = measure(project, chapter)
        lengths[chapter] = actual
        summary = analysis / "章节" / f"第{chapter}章_摘要.md"
        if summary.is_file():
            shown = f"`{shown_path(summary, project.parent)}`"
        else:
            missing.append(chapter)
            shown = "未找到摘要：按正文与卷纲反推，证据不足处写 [待补充]"
        rows.append(f"| {chapter} | `{shown_path(body, project.parent)}` | {shown} | {actual} |")
    head = (f"# 任务包：反推第{first}-{last}章细纲（导入）\n\n"
            f"只交付 `{project.name}/大纲/细纲_第{first:03d}章.md` 到 `细纲_第{last:03d}章.md`，每章一个文件；不改正文、卷纲和 `设定/`，"
            f"不建 `追踪/`。证据读下表的摘要（必要时回看该章正文），作者已定的事在 `{project.name}/.story/work/导入记录.md`；"
            "不要另读本包以外的写作技法文件。交付后只回：写了哪些文件、每章一句核心事件、"
            "证据不足标了 [待补充] 的要点（没有写「无」）。\n\n"
            "包里提到的检查由主会话在你交付后跑，你不执行命令；需要的测量结果已放进包里。")
    body = [head, f"\n## 本批章节\n\n路径相对项目根（`{project.parent}`）。\n\n" + "\n".join(rows),
            "\n## 卷纲剧情单元（覆盖本批）\n\n" + "\n".join(unit_rows(project, first, last)).rstrip(),
            "\n---\n\n<!-- 资料：outline-reverse-rules.md -->\n\n" + RULES.read_text(encoding="utf-8").lstrip("﻿").strip()]
    return "\n".join(body) + "\n", lengths, missing


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="拼出导入长篇逐批反推细纲的任务包")
    parser.add_argument("--project", required=True, type=Path, help="书目录（{导入书名}/）")
    parser.add_argument("--chapters", required=True, help="章节范围 A-B，每批 10–20 章")
    parser.add_argument("--analysis", type=Path, help="拆文库目录，默认 书目录的上一级/拆文库/{书目录名}")
    args = parser.parse_args(argv)
    try:
        project = args.project.resolve()
        if not project.is_dir():
            raise SystemExit(f"ERROR: 书目录不存在：{args.project}")
        first, last = parse_range(args.chapters)
        final = last_body_chapter(project)
        if last > final:
            raise SystemExit(f"ERROR: 正文只迁到第{final}章，范围超出")
        check_batch_size(first, last, final)
        analysis = (args.analysis or project.parent / "拆文库" / project.name).resolve()
        text, lengths, missing = build(project, analysis, first, last)
    except SystemExit as exc:
        emit(str(exc), sys.stderr)
        return 2
    out_dir = project.joinpath(*WORK_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"导入细纲_第{first:03d}-{last:03d}章.md"
    out.write_text(text, encoding="utf-8")
    emit(json.dumps({"brief": str(out), "chars": weight(text), "metric": METRIC,
                     "lengths": {str(k): v for k, v in lengths.items()}, "missing_summaries": missing},
                    ensure_ascii=False), sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
