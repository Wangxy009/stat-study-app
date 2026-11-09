"""全面修复 + 智能补全数学符号"""
import json, os, re

# 完整PUA映射表（基于实测+标准符号字体编码）
FIX = {
    # --- 运算符 (U+F020-F03F) ---
    '': '+', '': '−', '': '=', '': '<',
    '': '>', '': '≠', '': '≤', '': '≥',
    '': '±', '': '×', '': '·', '': '÷',
    # --- 小写希腊 (U+F060-F07F) ---
    '': 'α', '': 'β', '': 'γ', '': 'δ',
    '': 'ε', '': 'φ', '': 'γ', '': 'η',
    '': 'λ', '': 'μ', '': 'π', '': 'θ',
    '': 'σ', '': 'τ', '': 'ω',
    # --- 大写希腊 (U+F040-F05F) ---
    '': 'Δ', '': 'Φ', '': 'Γ', '': 'Θ',
    '': 'Λ', '': 'N', '': 'Θ', '': 'Σ',
    '': 'Π', '': 'Ψ', '': 'Ω',
    # --- 符号 ---
    '': '∑', '': '∏', '': '∫', '': '√',
    '': '∞', '': '∂', '': '→', '': '←',
    '': '∈', '': '∉',
    '': '…', '': '…',
    # --- 括号 ---
    '': '(', '': ')',
    '': '{', '': '}',
    '': '[', '': ']',
    # --- 杂项 ---
    '': "'", '': '°',
    '': '…', '': '',
    # --- 全角→半角 ---
    '！': '!', '（': '(', '）': ')',
    '，': ',', '．': '.', '：': ':',
    '；': ';', '？': '?',
    # --- 其他垃圾字符→删除 ---
    '': '', '': '', '': '', '': '',
    '': '', '': '', '': '', '': '',
    '': '', '': '', '': '',
    '': '', '': '', '': '', '': '',
    '': '', '': '', '': '', '': '',
    '': '', '': '', '': '√',
    # Circle numbers
    '①': '1', '②': '2', '③': '3',
    # accent
    'ˆ': '^',
}

def clean(text):
    if not text: return text
    for bad, good in FIX.items():
        text = text.replace(bad, good)
    # Clean whitespace
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove repeated garbage chars
    text = re.sub(r'[ˆ]{2,}', '', text)
    text = text.strip()
    return text

if __name__ == '__main__':
    base = os.path.dirname(__file__)
    fpath = os.path.join(base, 'problems.json')
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for p in data['problems']:
        p['statement'] = clean(p.get('statement', ''))
        p['solution'] = clean(p.get('solution', ''))

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Cleaned {data['total']} problems")

    # Verify samples
    for p in data['problems'][:4]:
        print(f"\n[{p['id']}] {p['source']}")
        stmt = p['statement']
        # Show clean version
        print(stmt[:250])
        print("---")
