"""从试题库和习题册提取题目，生成problems.json"""
import pdfplumber
import json
import re
import os

BASE = "/Users/wangxiaoya/Downloads/数理统计B"

def extract_question_bank():
    """提取试题库题目并按章节分组"""
    pdf = pdfplumber.open(f"{BASE}/《数理统计》课程试题库.pdf")

    chapters = {
        "2": {"title": "统计量与抽样分布", "problems": []},
        "3": {"title": "估计理论", "problems": []},
        "4": {"title": "假设检验", "problems": []},
        "5": {"title": "贝叶斯统计与统计决策理论", "problems": []},
        "6": {"title": "方差分析与实验设计", "problems": []},
    }

    current_chapter = None
    current_problem = None
    full_text = ""

    for page in pdf.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    # 按章节分割
    chapter_markers = [
        ("统计量与抽样分布", "2"),
        ("估计理论", "3"),
        ("假设检验", "4"),
        ("贝叶斯统计与统计决策理论", "5"),
        ("方差分析与实验设计", "6"),
    ]

    # Find chapter boundaries
    positions = []
    for marker, ch_id in chapter_markers:
        pos = full_text.find(marker)
        if pos >= 0:
            positions.append((pos, marker, ch_id))

    positions.sort()

    for i, (pos, marker, ch_id) in enumerate(positions):
        start = pos + len(marker)
        end = positions[i+1][0] if i+1 < len(positions) else len(full_text)
        chapter_text = full_text[start:end].strip()

        # Split into problems - look for patterns like "设...", "证明...", numbering
        problems = split_into_problems(chapter_text, ch_id)
        chapters[ch_id]["problems"] = problems

    return chapters

def split_into_problems(text, chapter_id):
    """将章节文本拆分成单个题目"""
    problems = []

    # Clean up the text
    lines = text.strip().split('\n')

    # Try to identify individual problems
    # Problems typically start with 设, 证明, 试求, 设总体, etc.
    problem_starts = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        # Check if this looks like a problem start
        if (stripped.startswith('设') or
            stripped.startswith('证明') or
            stripped.startswith('试') or
            stripped.startswith('求') or
            stripped.startswith('从') or
            stripped.startswith('掷') or
            stripped.startswith('某') or
            re.match(r'^\d+[\.\、）\)]', stripped)):
            problem_starts.append(i)

    # Group lines into problems
    for idx, start_line in enumerate(problem_starts):
        end_line = problem_starts[idx+1] if idx+1 < len(problem_starts) else len(lines)
        problem_text = '\n'.join(lines[start_line:end_line]).strip()

        # Skip if too short or is just a continuation
        if len(problem_text) < 20:
            continue

        # Try to extract problem statement and solution
        # Look for "解：" or "解:" as separator
        sol_match = re.search(r'\n解[：:]', problem_text)
        if sol_match:
            statement = problem_text[:sol_match.start()].strip()
            solution = problem_text[sol_match.start():].strip()
        else:
            statement = problem_text
            solution = ""

        # Clean up statement
        statement = statement[:500]  # Limit length

        problems.append({
            "id": f"QB-{chapter_id}-{idx+1:02d}",
            "source": "试题库",
            "chapter": int(chapter_id),
            "statement": statement,
            "solution": solution[:800] if solution else "(解答请参照试题库原文)",
            "difficulty": guess_difficulty(statement),
            "tags": guess_tags(statement, chapter_id)
        })

    return problems[:30]  # Limit per chapter

def guess_difficulty(text):
    """简单推断题目难度"""
    text_lower = text
    if any(kw in text for kw in ['UMVUE', '似然比', '贝叶斯', '充分完备', 'C-R']):
        return 'hard'
    if any(kw in text for kw in ['极大似然', '假设检验', '置信区间', '方差分析']):
        return 'medium'
    return 'easy'

def guess_tags(text, chapter_id):
    """根据文本关键词推断知识点标签"""
    tag_map = {
        "2": [
            ("χ²分布", ["χ²", "卡方", "chi"]),
            ("t分布", ["t分布", "学生氏", "t("]),
            ("F分布", ["F分布", "F("]),
            ("次序统计量", ["次序", "X_{(1)}", "X_{(n)}", "X_{(k)}"]),
            ("抽样分布定理", ["样本均值", "样本方差", "正态总体"]),
        ],
        "3": [
            ("矩估计", ["矩估计", "矩法"]),
            ("极大似然估计", ["极大似然", "MLE", "似然函数"]),
            ("无偏估计", ["无偏", "UMVUE"]),
            ("充分统计量", ["充分", "因子分解"]),
            ("区间估计", ["置信区间", "置信度"]),
            ("相合性", ["相合", "一致"]),
        ],
        "4": [
            ("两类错误", ["第I类", "第II类", "两类错误"]),
            ("正态总体检验", ["U检验", "t检验", "N(μ"]),
            ("拟合优度", ["拟合优度", "列联表"]),
            ("似然比检验", ["似然比"]),
            ("p值", ["p值", "p-值"]),
        ],
        "5": [
            ("贝叶斯估计", ["贝叶斯", "先验", "后验"]),
            ("统计决策", ["决策函数", "风险", "损失"]),
            ("Minimax", ["Minimax", "最小最大"]),
        ],
        "6": [
            ("单因素方差分析", ["单因素", "one-way"]),
            ("双因素方差分析", ["双因素", "two-way"]),
            ("多重比较", ["多重比较"]),
            ("正交设计", ["正交"]),
        ],
    }

    tags = []
    if chapter_id in tag_map:
        for tag_name, keywords in tag_map[chapter_id]:
            for kw in keywords:
                if kw.lower() in text.lower():
                    tags.append(tag_name)
                    break

    return tags[:4]

def extract_exercise_book(ex_num, chapter_id):
    """提取习题册题目"""
    fname = f"{BASE}/数理统计习题与解答_习题 {ex_num}.pdf"
    if not os.path.exists(fname):
        return []

    pdf = pdfplumber.open(fname)
    problems = []
    current_text = ""

    for page in pdf.pages:
        text = page.extract_text()
        if text:
            current_text += text + "\n"

    # Split into numbered problems
    # Pattern: 1． or 1. or similar numbering
    parts = re.split(r'\n(?=\d+[\.\．\、])', current_text)

    for i, part in enumerate(parts):
        part = part.strip()
        if len(part) < 15:
            continue

        # Remove leading number
        part = re.sub(r'^\d+[\.\．\、]\s*', '', part)

        # Split statement and solution
        sol_match = re.search(r'\n解[：:]', part)
        if sol_match:
            statement = part[:sol_match.start()].strip()
            solution = part[sol_match.start():].strip()
        else:
            statement = part[:400].strip()
            solution = ""

        problems.append({
            "id": f"EX-{chapter_id}-{i+1:02d}",
            "source": f"习题{ex_num}",
            "chapter": chapter_id,
            "statement": statement[:500],
            "solution": solution[:800] if solution else "(解答请参照习题册原文)",
            "difficulty": guess_difficulty(statement),
            "tags": guess_tags(statement, str(chapter_id))
        })

    return problems[:25]

if __name__ == "__main__":
    all_problems = []

    # 从试题库提取
    print("提取试题库...")
    qb_chapters = extract_question_bank()
    for ch_id, ch_data in qb_chapters.items():
        print(f"  第{ch_id}章: {len(ch_data['problems'])}道题")
        all_problems.extend(ch_data["problems"])

    # 从习题册提取
    for ex_num, ch_id in [(2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]:
        print(f"提取习题{ex_num}...")
        problems = extract_exercise_book(ex_num, ch_id)
        print(f"  第{ch_id}章习题: {len(problems)}道题")
        all_problems.extend(problems)

    # 保存
    output_path = os.path.join(os.path.dirname(__file__), "problems.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"total": len(all_problems), "problems": all_problems}, f, ensure_ascii=False, indent=2)

    print(f"\n总计 {len(all_problems)} 道题目已保存至 {output_path}")

    # 统计
    ch_count = {}
    for p in all_problems:
        ch = p["chapter"]
        ch_count[ch] = ch_count.get(ch, 0) + 1
    for ch, cnt in sorted(ch_count.items()):
        print(f"  第{ch}章: {cnt}道")
