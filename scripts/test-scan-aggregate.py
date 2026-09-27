#!/usr/bin/env python3
"""扫榜聚合脚本 aggregate-rank.js 的行为回归。

夹具按各采集脚本的实际 Markdown 渲染格式手写（番茄/起点/七猫/晋江/刺猬猫/点众/黑岩），
经公开 CLI 断言：题材计数与去重、热度口径、字数分桶、标签热词、多榜重合、采集问题上浮、
样本够不够、抽样取回原始条目、非榜单文件被跳过，以及聚合结果远小于原始榜单。
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LONG = ROOT / "skills" / "story-long-scan" / "scripts" / "aggregate-rank.js"
SHORT = ROOT / "skills" / "story-short-scan" / "scripts" / "aggregate-rank.js"
NODE = shutil.which("node")

FAILURES: list[str] = []


def check(cond: bool, message: str) -> None:
    if not cond:
        FAILURES.append(message)


def run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [NODE, str(script), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )


# ---------------------------------------------------------------------------
# 夹具：逐平台模仿采集脚本 renderMarkdown 的输出
# ---------------------------------------------------------------------------

DESC = "他本是宗门弃徒，一朝觉醒系统，从此踏上逆天之路。可无人知道，那场灭门惨案背后另有其人，而真相就藏在他随身携带的那枚玉佩里。"


def fanqie(channel: str, list_name: str, genres: dict[str, list[tuple]], quality: str = "[OK]") -> str:
    total = sum(len(v) for v in genres.values())
    resolved = sum(1 for v in genres.values() for b in v if b[0] != "（标题待解析）")
    lines = [
        f"# 番茄 · {channel}{list_name} · 全 {len(genres)} 题材",
        "",
        "- 频道参数：channel=1，type=2",
        "- 抓取时间：2026-09-26T03:00:00.000Z",
        "- 每题材上限 ≈ 20",
        f"- 标题解析：成功 {resolved} / 共 {total}",
        f"- 数据质量：{quality}",
        "",
        "---",
        "",
    ]
    for genre, books in genres.items():
        if not books:
            lines += [f"## {genre} — 采集失败", "", "---", ""]
            continue
        lines += [f"## {genre} — {len(books)} 本", ""]
        for i, (title, author, reads, words, tags) in enumerate(books, 1):
            lines.append(f"### #{i} {title}")
            lines.append(f"*{author} · {genre} · 连载中 · {reads} 在读 · {words}字*")
            if tags:
                lines.append(f"**标签：** {tags}")
            lines += ["**最新更新：** 第88章 风起", f"**bookId：** 7{i:06d}", f"[作品页](https://fanqienovel.com/page/7{i:06d})"]
            lines += ["", "**简介**", "", DESC, ""]
        lines += ["---", ""]
    return "\n".join(lines)


def qidian(list_name: str, books: list[tuple]) -> str:
    lines = [f"# 起点 · {list_name}", "", "- 来源：https://m.qidian.com/rank/yuepiao/", "- 抓取方式：mobile-ssr",
             "- 抓取时间：2026-09-25T10:00:00.000Z", f"- 条目数：{len(books)}", "", "---", ""]
    for i, (title, author, genre, words, rec, tags) in enumerate(books, 1):
        lines.append(f"## #{i} {title}")
        lines.append(f"*{author} · {genre} · 连载*")
        lines += [f"**字数：{words}**", f"**总推荐：{rec}**", "**签约：签约**", "**收费模式：VIP**"]
        if tags:
            lines.append(f"**标签：** {tags}")
        lines += [f"[作品页](https://m.qidian.com/book/{i}/)", "", "**简介**", "", DESC[:60], "", "---", ""]
    return "\n".join(lines)


def qimao(books: list[tuple]) -> str:
    lines = ["# 七猫 · 女生榜 · 大热榜日榜", "", "- 数据质量：[存在问题]", f"- 有效条目：{len(books)} / 22",
             "- 问题摘要：热度命中 3/4", "- 来源：https://www.qimao.com/paihang", "- 抓取时间：2026-09-26T01:00:00.000Z",
             f"- 条目数：{len(books)}", "", "---", ""]
    for i, (title, author, genre, sub, words, heat) in enumerate(books, 1):
        lines.append(f"### #{i} {title}")
        lines.append(f"*{author} · {genre} · {sub} · 连载中 · {words} · {heat + '热度' if heat else '[待补]'}*")
        lines += ["**最新更新：** 2026-09-25 · 第12章", "", "---", ""]
    return "\n".join(lines)


def jjwxc() -> str:
    return "\n".join([
        "# 晋江 · 收入金榜", "", "- 来源：https://www.jjwxc.net/topten.php?orderstr=12&t=0",
        "- 抓取时间：2026-09-26T02:00:00.000Z", "- 频道数：2", "- 总条目数：3",
        "- 详情采集：3 / 3（每频道前 10，上限 100）", "- 数据质量：[OK]", "", "---", "",
        "## 言情 — 2 本", "",
        "### #1 春日宴", "*甲作者 · 收藏 12.5万 · 营养液 30.1万 · 积分 998877 · 字数 45.2万字 · 连载*",
        "[作品页](https://www.jjwxc.net/onebook.php?novelid=1)", "",
        "### #2 月下归", "*乙作者 · 收藏 8.0万 · 营养液 9.9万 · 积分 12345 · 字数 21.0万字 · 完结*",
        "[作品页](https://www.jjwxc.net/onebook.php?novelid=2)", "",
        "---", "",
        "## 纯爱 — 1 本", "",
        "### #1 长夜", "*丙作者 · 收藏 20.0万 · 字数 80.0万字 · 连载*",
        "[作品页](https://www.jjwxc.net/onebook.php?novelid=3)", "",
        "---", "",
    ])


def ciweimao() -> str:
    return "\n".join([
        "# 刺猬猫 · 月票榜", "", "- 来源：https://www.ciweimao.com/rank-index", "- 抓取时间：2026-09-26T02:00:00.000Z",
        "- 条目数：3", "- 作品页链接：1 / 3", "", "---", "",
        "### #1 我的二次元", "*猫作者 · 1.2万*", "[作品页](https://www.ciweimao.com/book/1)", "", "---", "",
        "### #2 次元旅人", "*同人 · 9876*", "", "---", "",
        "### #3 轻小说物语", "*轻小说 · 5432*", "", "---", "",
    ])


def dianzhong() -> str:
    return "\n".join([
        "# 点众 · 女频短篇", "", "- 来源：https://www.ishugui.com/browse/on3", "- 抓取时间：2026-09-26T02:00:00.000Z",
        "- 条目数：3", "- 书名解析：2 / 3", "- 数据质量：[OK]", "", "---", "",
        "### #1 假千金她杀疯了", "*短作者 · 家庭复仇 · 已完结 · 12345字 · 9.1分*", "**最新：** 第8章", "[作品页](https://www.ishugui.com/book/1)",
        "", "> 真千金回家第一天，就被全家人当成了骗子。", "", "---", "",
        "### #2 弹幕说我是恶毒女配", "*二作者 · 弹幕流 · 已完结 · 8000字 · 8.7分*", "", "---", "",
        "### #3 （书名待解析）", "*三作者 · 家庭复仇 · 已完结 · 25000字*", "", "---", "",
    ])


def heiyan() -> str:
    return "\n".join([
        "# 黑岩 · 书库列表", "", "- 来源：https://manage.zhangwenpindu.cn/books/booklist", "- 抓取时间：2026-09-26T02:00:00.000Z",
        "- 总条目：40", "- 已采集：2 条（1 页）", "- 含详情（标签、简介）", "", "---", "",
        "## 女频短篇 — 2 本", "",
        "### #1 离婚后前夫跪求复合", "*岩作者 · 女频/虐恋 · 32,000字 · 99钻 · 公开*", "**标签：** 追妻火葬场、虐恋", "",
        "> 结婚三年，他心里只有白月光。", "",
        "### #2 重生后我不当保姆了", "*岩二 · 女频/复仇 · 15,000字 · 公开*", "",
        "---", "",
    ])


def big_fanqie(genre_count: int = 37, per_genre: int = 20) -> str:
    genres = {}
    for g in range(genre_count):
        genres[f"题材{g:02d}"] = [
            (f"第{g}类样书{i}号", f"作者{g}_{i}", f"{(per_genre - i) * 1.3 + g:.1f}万", f"{50 + i * 7}.{g % 10}万", "系统、逆袭、爽文")
            for i in range(per_genre)
        ]
    return fanqie("男频", "阅读榜", genres)


def write_fixture(tmp: Path) -> Path:
    scan = tmp / "scan"
    scan.mkdir()
    (scan / "番茄男频阅读榜_全题材_20260926.md").write_text(fanqie("男频", "阅读榜", {
        "都市日常": [
            ("开局签到神豪系统", "甲", "88.2万", "120.5万", "系统、神豪"),
            ("都市之最强奶爸", "乙", "35.0万", "80.0万", "奶爸、系统"),
            ("（标题待解析）", "未知", "未知", "未知", ""),
        ],
        "东方仙侠": [
            ("我在仙门当杂役", "丙", "120.0万", "210.3万", "修仙、苟道"),
        ],
        "悬疑脑洞": [],
    }), encoding="utf-8")
    (scan / "番茄男频新书榜_全题材_20260926.md").write_text(fanqie("男频", "新书榜", {
        "都市日常": [
            ("开局签到神豪系统", "甲", "90.0万", "121.0万", "系统、神豪、爽文"),
            ("重生之我是首富", "丁", "5.5万", "8.8万", "重生"),
        ],
    }), encoding="utf-8")
    (scan / "起点月票榜_20260925.md").write_text(qidian("月票榜", [
        ("诡秘之主续", "乌贼", "玄幻·东方玄幻", "1234567", "12.3万", "克系、群像"),
        ("赤心巡天续", "情何以甚", "仙侠·古典仙侠", "3500000", "30.0万", ""),
    ]), encoding="utf-8")
    (scan / "七猫女生榜大热榜日榜_20260926.md").write_text(qimao([
        ("总裁的替身娇妻", "猫一", "现代言情", "豪门总裁", "123.4万字", "567.8万"),
        ("宫阙", "猫二", "古代言情", "宫斗宅斗", "45.0万字", ""),
    ]), encoding="utf-8")
    (scan / "晋江收入金榜_全站_20260926.md").write_text(jjwxc(), encoding="utf-8")
    (scan / "刺猬猫月票榜_20260926.md").write_text(ciweimao(), encoding="utf-8")
    (scan / "点众女频短篇_20260926.md").write_text(dianzhong(), encoding="utf-8")
    (scan / "黑岩书库列表_female_20260926.md").write_text(heiyan(), encoding="utf-8")
    # 作者手动提供、按 manual-rank-input.md 格式整理的榜单
    (scan / "知乎盐言热门榜_20260926.md").write_text("\n".join([
        "# 知乎盐言 · 热门榜", "",
        "### #1 替嫁后我成了首辅夫人", "*盐一 · 古言 · 已完结 · 12000字 · 2.3万收藏*", "**标签：** 先婚后爱、追妻",
        "", "> 嫁过去的第一晚，他递来一纸和离书。", "",
        "### #2 我妈的第二个女儿", "*盐二 · 现实 · 已完结 · 9000字 · 8000收藏*", "",
    ]), encoding="utf-8")
    # 非榜单文件：自家产物与作者笔记，都不该被当成榜单
    (scan / "选题决策.md").write_text("# 选题决策：番茄男频\n\n### #1 不是榜单\n", encoding="utf-8")
    (scan / "扫榜聚合.md").write_text("# 扫榜聚合\n", encoding="utf-8")
    (scan / "短篇扫榜结论.md").write_text("# 短篇扫榜结论：点众 · 女频\n\n### #1 不是榜单\n", encoding="utf-8")
    (scan / "笔记.md").write_text("# 随手记\n\n- 想写都市\n", encoding="utf-8")
    return scan


def platform(result: dict, name: str) -> dict:
    for p in result["platforms"]:
        if p["platform"] == name:
            return p
    raise AssertionError(f"missing platform {name}: {[p['platform'] for p in result['platforms']]}")


def genre(p: dict, name: str) -> dict:
    for g in p["genres"]:
        if g["name"] == name:
            return g
    raise AssertionError(f"missing genre {name}: {[g['name'] for g in p['genres']]}")


def test_json_aggregate(scan: Path) -> None:
    proc = run(LONG, str(scan), "--json", "--sparse", "2")
    check(proc.returncode == 0, f"json run failed: {proc.stderr}")
    result = json.loads(proc.stdout)

    names = sorted(f["name"] for f in result["files"])
    check(not {"选题决策.md", "扫榜聚合.md", "短篇扫榜结论.md", "笔记.md"} & set(names),
          f"non-rank files must be skipped: {names}")
    check(len(names) == 9, f"expected 9 rank files, got {names}")
    check(result["platforms"][0]["platform"] == "番茄", "platforms ordered by sample size")

    fq = platform(result, "番茄")
    check(fq["metric"] == "在读", f"fanqie metric should be 在读, got {fq['metric']}")
    check(fq["entryCount"] == 6, f"fanqie raw entries 6, got {fq['entryCount']}")
    check(fq["bookCount"] == 5, f"same title+author across lists counts once, got {fq['bookCount']}")
    city = genre(fq, "都市日常")
    check(city["count"] == 4, f"都市日常 unique books 4, got {city['count']}")
    check(city["newCount"] == 2, f"都市日常 new-list books 2, got {city['newCount']}")
    check(fq["compareNew"] is True, "new-list comparison should be on when both list kinds exist")
    check(city["reps"][0]["title"] == "开局签到神豪系统", f"top rep by 在读: {city['reps'][0]}")
    check(city["reps"][0]["heat"] == 900000, f"merged heat takes the max across lists: {city['reps'][0]['heat']}")
    check(city["reps"][0]["lists"] == 2, "overlapping book should carry 2 lists")
    check("爽文" in city["reps"][0]["tags"], "tags merge across lists")
    check(genre(fq, "东方仙侠")["sparse"] is True, "genre under --sparse must be flagged")
    check(city["sparse"] is False, "genre at/above --sparse must not be flagged")
    tag_counts = dict(fq["tags"])
    check(tag_counts.get("系统") == 2, f"tag counted per unique book: {fq['tags']}")
    check([o["title"] for o in fq["overlap"]] == ["开局签到神豪系统"], f"overlap: {fq['overlap']}")
    buckets = {b["label"]: b["count"] for b in fq["words"]["buckets"]}
    check(buckets["200万字以上"] == 1 and buckets["100-200万字"] == 1 and buckets["10万字以下"] == 1,
          f"long word buckets: {buckets}")

    fq_files = [f for f in result["files"] if f["platform"] == "番茄" and "阅读榜" in f["list"]]
    probs = " ".join(fq_files[0]["problems"])
    check("悬疑脑洞" in probs, f"failed section must surface: {probs}")
    check("书名待解析 1" in probs, f"unresolved titles must surface: {probs}")

    qd = platform(result, "起点")
    check(qd["metric"] == "总推荐", f"qidian metric: {qd['metric']}")
    check({g["name"] for g in qd["genres"]} == {"玄幻", "仙侠"}, f"qidian main category as genre: {qd['genres']}")
    check("东方玄幻" in dict(qd["tags"]), "qidian sub-category becomes a tag")
    check(genre(qd, "仙侠")["wordsMedian"] == 3500000, "qidian 字数 line parsed")

    qm = platform(result, "七猫")
    check(qm["metric"] == "热度", f"qimao metric: {qm['metric']}")
    check(genre(qm, "现代言情")["heatMedian"] == 5678000, "qimao heat parsed from 万热度")
    check("豪门总裁" in dict(qm["tags"]), "qimao sub-genre becomes a tag")
    qm_file = next(f for f in result["files"] if f["platform"] == "七猫")
    check("存在问题" in qm_file["quality"], "non-OK quality must surface")
    check(any("热度命中" in p for p in qm_file["problems"]), "header problem summary must surface")

    jj = platform(result, "晋江")
    check(jj["metric"] == "收藏", f"jjwxc metric: {jj['metric']}")
    check(genre(jj, "言情")["count"] == 2 and genre(jj, "纯爱")["count"] == 1, "jjwxc channel as genre")
    check(genre(jj, "纯爱")["reps"][0]["author"] == "丙作者", "jjwxc author parsed")

    cw = platform(result, "刺猬猫")
    check({g["name"] for g in cw["genres"]} == {"未分类", "同人", "轻小说"}, f"ciweimao genres: {cw['genres']}")
    check(genre(cw, "未分类")["reps"][0]["author"] == "猫作者", "ciweimao rank-1 carries author, not genre")

    dz = platform(result, "点众")
    check(dz["scale"] == "short", "short platforms use short word buckets")
    check(dz["metric"] == "评分", f"dianzhong metric: {dz['metric']}")
    check(genre(dz, "家庭复仇")["count"] == 2, "dianzhong tag field is the genre")
    check(all(r["title"] != "（书名待解析）" for r in genre(dz, "家庭复仇")["reps"]), "unresolved titles never become representatives")
    dz_buckets = {b["label"]: b["count"] for b in dz["words"]["buckets"]}
    check(dz_buckets["1-2万字"] == 1 and dz_buckets["5千-1万字"] == 1 and dz_buckets["2-4万字"] == 1,
          f"short word buckets: {dz_buckets}")

    zh = platform(result, "知乎盐言")
    check(zh["scale"] == "short" and zh["metric"] == "收藏", f"manual list metric/scale: {zh['metric']} {zh['scale']}")
    check(genre(zh, "古言")["heatMedian"] == 23000, "「数字+口径」heat parsed from manual list")
    check("2.3万收藏" not in dict(zh["tags"]), "heat segment must not leak into tags")
    check("先婚后爱" in dict(zh["tags"]), "manual list tags parsed")

    hy = platform(result, "黑岩")
    check({g["name"] for g in hy["genres"]} == {"虐恋", "复仇"}, f"heiyan genre after slash: {hy['genres']}")
    check(genre(hy, "虐恋")["wordsMedian"] == 32000, "heiyan comma words parsed")
    check("追妻火葬场" in dict(hy["tags"]), "heiyan tags parsed")


def test_markdown_and_out(scan: Path, tmp: Path) -> None:
    out = tmp / "out" / "扫榜聚合.md"
    proc = run(LONG, str(scan / "番茄男频阅读榜_全题材_20260926.md"), str(scan / "番茄男频新书榜_全题材_20260926.md"),
               "--out", str(out), "--top", "1", "--desc", "8")
    check(proc.returncode == 0, f"markdown run failed: {proc.stderr}")
    check(out.exists(), "--out must write the aggregate file")
    text = out.read_text(encoding="utf-8")
    check(text == proc.stdout, "--out content equals stdout")
    check(text.startswith("# 扫榜聚合"), "aggregate heading")
    check("| 都市日常 | 4 |" in text, "genre row present")
    check("新书榜" in text.split("\n## 番茄")[1].split("\n")[2], "new-list column shown when both list kinds exist")
    check("- 《开局签到神豪系统》" in text, "representative line present")
    check("- 《都市之最强奶爸》" not in text, "--top 1 keeps only the leader per genre")
    check("｜他本是宗门弃徒，…" in text and DESC not in text, "--desc truncates blurbs")
    check("悬疑脑洞" in text, "failed genre surfaces in 采集情况")

    rerun = run(LONG, str(out.parent), "--json")
    check(rerun.returncode == 1, "a directory holding only the aggregate is not a rank source")


def test_sample(scan: Path) -> None:
    proc = run(LONG, str(scan), "--sample", "都市日常", "--n", "2")
    check(proc.returncode == 0, f"sample failed: {proc.stderr}")
    check("命中 5 条，显示 2 条" in proc.stdout, f"sample counts raw entries across lists: {proc.stdout[:200]}")
    check("### #1 开局签到神豪系统" in proc.stdout, "sample returns raw entry blocks")
    check(DESC in proc.stdout, "sample keeps the full raw blurb")
    by_tag = run(LONG, str(scan), "--sample", "追妻火葬场")
    check("离婚后前夫跪求复合" in by_tag.stdout, "sample matches tags")


def test_errors(tmp: Path) -> None:
    empty = tmp / "empty"
    empty.mkdir()
    (empty / "笔记.md").write_text("# 随手记\n", encoding="utf-8")
    proc = run(LONG, str(empty))
    check(proc.returncode == 1 and "没有找到可聚合的榜单文件" in proc.stderr, f"empty input: {proc.returncode} {proc.stderr}")
    proc = run(LONG, str(tmp / "missing"))
    check(proc.returncode == 2 and "找不到输入" in proc.stderr, "missing path must fail clearly")
    proc = run(LONG, str(empty), "--top")
    check(proc.returncode == 2 and "--top 需要一个值" in proc.stderr, "valued flag without value must fail")
    proc = run(LONG)
    check(proc.returncode == 2 and "用法" in proc.stderr, "no input prints usage")


def test_compression(tmp: Path) -> None:
    big = tmp / "big"
    big.mkdir()
    raw = big_fanqie()
    (big / "番茄男频阅读榜_全题材_20260926.md").write_text(raw, encoding="utf-8")
    proc = run(LONG, str(big))
    check(proc.returncode == 0, f"big run failed: {proc.stderr}")
    result = json.loads(run(LONG, str(big), "--json").stdout)
    check(platform(result, "番茄")["bookCount"] == 740, "37 genres x 20 books aggregate to 740 unique books")
    check(len(proc.stdout) * 5 < len(raw), f"aggregate must be far smaller than raw: {len(proc.stdout)} vs {len(raw)}")


def test_short_copy_identical() -> None:
    check(SHORT.read_bytes() == LONG.read_bytes(), "short-scan copy must stay byte-identical (shared-assets)")


def main() -> int:
    if not NODE:
        print("SKIP: node not found")
        return 0
    tmp = Path(tempfile.mkdtemp(prefix="scan-aggregate-"))
    try:
        scan = write_fixture(tmp)
        test_json_aggregate(scan)
        test_markdown_and_out(scan, tmp)
        test_sample(scan)
        test_errors(tmp)
        test_compression(tmp)
        test_short_copy_identical()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if FAILURES:
        for failure in FAILURES:
            print(f"FAIL: {failure}")
        return 1
    print("PASS: scan aggregate behavior")
    return 0


if __name__ == "__main__":
    sys.exit(main())
