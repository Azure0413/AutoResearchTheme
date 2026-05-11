import os
import re
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from groq import Groq, APIStatusError

# ===== 基本設定 =====
TAIPEI_TZ = ZoneInfo("Asia/Taipei")
STATE_FILE = "state.json"
HISTORY_FILE = "topic_history.json"
HISTORY_DAYS = 14
DISCORD_MAX_CHARS = 1900

today_str = datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d")
REPORT_FILE = f"reports/research_report_{today_str}.md"

client = Groq(api_key=os.environ["GROQ_API_KEY"])
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()

# ===== 模型分配 =====
MODEL_RESEARCH = "groq/compound-mini"          # Stage 1, 2 — 內建 web search
MODEL_REASONING = "llama-3.3-70b-versatile"    # Stage 3, 4, 5 — 純推理
MODEL_SUMMARY = "llama-3.1-8b-instant"         # 摘要壓縮 — 便宜快速

MAX_TOKENS_MAIN = 2048
MAX_TOKENS_SUMMARY = 600

# ===== 每日輪替焦點(用 day-of-year 旋轉,確保 14 天內不重複大方向) =====
DAILY_FOCUS_THEMES = [
    "Mechanistic Interpretability 與模型內部結構(Sparse Autoencoder、circuit analysis、emergent misalignment 偵測、internal feature vectors)",
    "非 Transformer 架構創新(Mamba/SSM 變體、Gated DeltaNet、Gated Attention、xLSTM、線性注意力新解法)",
    "推理模型的本質與限制(RLVR 為何難以引出新能力、test-time compute scaling laws、self-improvement 真實可行性)",
    "結構化 World Models(causal world model、object-centric representation、long-context state-space video model)",
    "Continual / Lifelong / Nested Learning(避免 catastrophic forgetting 的新訓練範式、Google DeepMind Nested Learning 路線)",
    "Discrete Diffusion / Flow Matching 在非影像領域(蛋白質、程式碼、分子、時間序列、tabular data)",
    "推論效率創新(KV cache 壓縮新策略、speculative decoding 變體、attention sink-free 設計、token routing)",
    "AI for Science 非主流子領域(材料設計、催化劑、晶體結構、量子化學、流體模擬)",
    "Agent 學習範式創新(非 prompting,而是 skill discovery、policy distillation、tool-use 從零學起)",
    "強化學習新探索方法(non-RLVR、curiosity-driven、unsupervised RL、emergent communication)",
    "稀疏專家(MoE)路由創新(expert choice、token choice、adaptive routing、heterogeneous experts)",
    "Equivariant / Geometric Deep Learning(對稱性、群論、relational reasoning、symbolic-neural hybrid)",
    "資料中毒、後門攻擊與防禦(post-training data poisoning、emergent misalignment 機制研究)",
    "Neural ODE / SDE / 連續時間模型在控制、物理模擬、機率密度估計的新應用",
]


def get_today_focus():
    """根據今天的 day-of-year 選擇一個焦點主題,確保 14 天內不重複大方向。"""
    doy = datetime.now(TAIPEI_TZ).timetuple().tm_yday
    return DAILY_FOCUS_THEMES[doy % len(DAILY_FOCUS_THEMES)]


# ===== System Prompt =====
SYSTEM_PROMPT = (
    "你是頂尖 AI/ML 研究員,對 NeurIPS/ICML/ICLR 2024-2026 最新進展瞭如指掌。"
    "你的任務是找出**真正具有突破潛力但研究人數還不算飽和**的方向。\n\n"
    "嚴格遵守以下原則:\n"
    "1. 拒絕安全保守的選題。**禁止**重複以下已被過度研究的方向:\n"
    "   - 通用 multimodal LLM / vision-language model 對齊\n"
    "   - text-to-image diffusion (Stable Diffusion 衍生改良、ControlNet 變體)\n"
    "   - LoRA / PEFT 一般性改良\n"
    "   - 標準 RAG pipeline\n"
    "   - 通用 chain-of-thought prompting 技巧\n"
    "   - 通用 Transformer 注意力 ablation\n"
    "2. 每個主題必須引用 2025-2026 年的具體 paper(NeurIPS 2025、ICLR 2026、ICML 2025/2026、arXiv 2025-2026)。\n"
    "3. 全程使用繁體中文。\n\n"
    "**Discord 輸出格式硬性要求**(違反會導致顯示損毀):\n"
    "- **嚴禁** LaTeX 數學公式($...$、$$...$$、\\frac、\\sum 等)。如需公式請用文字描述(例如「L 為交叉熵損失加上 KL 散度懲罰項」)。\n"
    "- **嚴禁** Markdown 表格(| col1 | col2 |)。需要結構化比較時改用條列。\n"
    "- 使用 **粗體** 標題,條列用 `-` 開頭,層級不超過 2 層。\n"
    "- 程式碼或變數名稱用 inline code(反引號)。"
)

STAGE_META = {
    1: {"name": "🔍 探索熱門議題", "color": 0x3498DB},
    2: {"name": "📖 深入相關方法", "color": 0x2ECC71},
    3: {"name": "💡 提出創新方法", "color": 0x9B59B6},
    4: {"name": "🔥 嚴格自我批判", "color": 0xE67E22},
    5: {"name": "✅ 完整研究提案", "color": 0xF1C40F},
}


def build_stage_prompts():
    """每次跑都動態生成,把今日焦點與歷史主題注入 Stage 1。"""
    today_focus = get_today_focus()
    history_block = build_history_avoid_block()

    return {
        1: (
            f"今日輪替焦點方向:**{today_focus}**\n\n"
            "請以該方向為主軸,搜尋 2025 年下半年至 2026 年的最新研究,"
            "整理 3 個**互不相同**且**尚未飽和**的具體子主題。\n\n"
            "**禁止選題**:任何以「multimodal LLM」、「vision-language alignment」、"
            "「text-to-image diffusion 改良」、「通用 LoRA/PEFT」、「standard RAG」、"
            "「standard chain-of-thought」為核心的題目。這些已過度競爭。\n"
            f"{history_block}\n"
            "**輸出格式**(嚴格遵守,不要表格、不要 LaTeX):\n\n"
            "**主題一:[精確的子主題名稱]**\n"
            "- 為何不飽和但有突破潛力(1-2 句具體說明,不要泛泛)\n"
            "- 代表 paper(2-3 篇,標題、第一作者、會議或 arXiv 編號、年份,**必須 2025 年以後**)\n"
            "- 核心技術問題與未解之處(2-3 句)\n\n"
            "**主題二:**...\n\n"
            "**主題三:**...\n"
        ),
        2: (
            "從前一階段三個主題中,挑出**最值得深入**的 1 個。"
            "評選標準:(a) 技術成熟到可動手實作 (b) 仍有明顯破綻可改進 (c) 學生級資源可進場。\n\n"
            "請深入剖析以下六個面向(用條列,不要表格):\n\n"
            "**1. 核心方法群**:列出至少 3 個代表方法,每個用 2-3 句描述其技術原理(文字,不用公式)\n"
            "**2. 模型架構細節**:輸入輸出、關鍵模組、訓練目標\n"
            "**3. 訓練策略**:資料規模、batch size、優化器、loss 設計、實作 tricks\n"
            "**4. 主要 benchmark 與資料集**:現行 SOTA 在哪個資料集評估?關鍵指標是什麼?\n"
            "**5. 方法優劣比較**:用條列(三個方法各列出 2-3 個優點 + 2-3 個缺點)\n"
            "**6. 明確的「未解破綻」**:目前方法在什麼條件下失效?哪些指標還很差?哪些 ablation 缺失?"
        ),
        3: (
            "基於前兩階段分析,請發揮**最大創意**提出 **3-5 個具體可實作的創新方法**。\n\n"
            "嚴格要求:\n"
            "- 每個方案必須能寫成一頁 method section,不能是模糊建議\n"
            "- **禁止**「加入注意力機制」、「結合 transformer」、「多模態融合」這類空泛口號\n"
            "- 必須明確指出與既有方法在**演算法層級**的差異(改了哪一行)\n"
            "- 必須說明為何此差異會帶來改善(因果鏈,不是 hand-waving)\n\n"
            "**每個方案輸出格式**(條列,不要表格、不要 LaTeX):\n\n"
            "**方案 X:[簡潔有力的名稱]**\n"
            "- **核心 idea(1 句話精確說明)**\n"
            "- **技術細節**:輸入流程、模組設計、訓練目標、損失函數(用文字描述,不用公式)\n"
            "- **與 SOTA 的差異**:明確指出哪個元件被改、改成什麼、為何這個改動具體會影響哪個指標\n"
            "- **預期改善的指標與原因**:在哪個 benchmark 預期提升?推理鏈是什麼?\n"
            "- **最小可行實驗(MVP)**:用什麼資料集、多大模型、單張 GPU 可不可以驗證?"
        ),
        4: (
            "扮演 NeurIPS area chair 等級的審稿人,對前一階段每個方案進行**毫不留情**的批判。\n\n"
            "每個方案至少給出 **5 個尖銳問題**,涵蓋以下五個角度:\n"
            "1. **理論假設**:假設成立的條件是什麼?有反例嗎?在什麼資料分布下會崩?\n"
            "2. **資料與訓練可行性**:資料夠嗎?訓練穩定嗎?有特定 hyperparameter 依賴嗎?\n"
            "3. **計算資源**:單卡 24G VRAM 學生可以做嗎?還是必須 8xH100?成本估算?\n"
            "4. **是否真優於 SOTA**:基準是否選太弱?有沒有 cherry-picking 嫌疑?差距是否來自非本方法的因素?\n"
            "5. **failure mode**:在哪些條件、資料分布、長度尺度下會徹底失敗?\n\n"
            "**每個批判點後面必須附「補救方向」**,不能只罵不給解法。\n\n"
            "**輸出格式**(條列,不要表格):\n\n"
            "**方案 X 批判**:\n"
            "- **批判 1(類別)**:具體問題敘述... | **補救**:具體補救方向...\n"
            "- **批判 2(類別)**:... | **補救**:...\n"
            "...(至少 5 條)"
        ),
        5: (
            "綜合前四階段,整合出**一個最完善、最值得執行**的研究提案。"
            "選擇標準:(a) 技術可行 (b) 創新性高 (c) 計算成本可控(單張 24-48G GPU 可開工)。\n\n"
            "**輸出格式**(嚴格遵守,不要 LaTeX、不要表格):\n\n"
            "## 1. 研究痛點與背景\n"
            "(為何重要?目前方法的具體缺陷?引用 1-2 篇 paper 支撐論點)\n\n"
            "## 2. 核心研究方法\n"
            "(一段 paragraph 說明 idea,再用條列列出 step-by-step 演算法、訓練目標、推論流程)\n\n"
            "## 3. 與既有方法的差異與創新性\n"
            "(條列至少 3 個層級的新穎性:演算法層、實作層、應用層)\n\n"
            "## 4. 實驗設計\n"
            "- **資料集**:\n"
            "- **baseline**:\n"
            "- **評估指標**:\n"
            "- **ablation study 設計**:\n"
            "- **計算需求估計**(GPU 數量 × 時間 × 成本):\n\n"
            "## 5. 預期貢獻與影響\n"
            "(科學價值 + 工程應用 + 為何 reviewer 會給高分)\n\n"
            "## 6. 風險與緩解\n"
            "(誠實列出 2-3 個最大風險與應對策略)"
        ),
    }


def get_model(stage: int) -> str:
    return MODEL_RESEARCH if stage in (1, 2) else MODEL_REASONING


# ===== 狀態管理 =====
def new_state() -> dict:
    return {"date": today_str, "step": 1, "summaries": []}


def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return new_state()
    with open(STATE_FILE, encoding="utf-8") as f:
        state = json.load(f)
    if state.get("date") != today_str:
        return new_state()
    return state


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ===== 主題歷史管理(避免日復一日重複題目) =====
def load_history() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_history_entry(date: str, stage1_summary: str, stage5_summary: str) -> None:
    history = load_history()
    # 移除同日舊條目(若有)
    history = [h for h in history if h.get("date") != date]
    history.append({
        "date": date,
        "stage1_topics": stage1_summary[:400],
        "final_proposal": stage5_summary[:300],
    })
    # 只保留最近 HISTORY_DAYS 天
    history = sorted(history, key=lambda x: x["date"])[-HISTORY_DAYS:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def build_history_avoid_block() -> str:
    """生成「過去 N 天已探討主題,請務必避開」prompt 區塊。"""
    history = load_history()
    if not history:
        return ""
    block = "\n**過去 14 天已探討的主題(請務必避開、提出全新角度)**:\n"
    for h in history:
        block += f"- `{h['date']}`: {h.get('stage1_topics', '')[:200]}\n"
    return block


# ===== Discord 格式轉換層 =====
GREEK_MAP = {
    r"\\alpha": "α", r"\\beta": "β", r"\\gamma": "γ", r"\\delta": "δ",
    r"\\epsilon": "ε", r"\\varepsilon": "ε", r"\\zeta": "ζ", r"\\eta": "η",
    r"\\theta": "θ", r"\\iota": "ι", r"\\kappa": "κ", r"\\lambda": "λ",
    r"\\mu": "μ", r"\\nu": "ν", r"\\xi": "ξ", r"\\pi": "π",
    r"\\rho": "ρ", r"\\sigma": "σ", r"\\tau": "τ", r"\\upsilon": "υ",
    r"\\phi": "φ", r"\\chi": "χ", r"\\psi": "ψ", r"\\omega": "ω",
    r"\\Gamma": "Γ", r"\\Delta": "Δ", r"\\Theta": "Θ", r"\\Lambda": "Λ",
    r"\\Pi": "Π", r"\\Sigma": "Σ", r"\\Phi": "Φ", r"\\Omega": "Ω",
    r"\\nabla": "∇", r"\\partial": "∂", r"\\infty": "∞",
    r"\\cdot": "·", r"\\times": "×", r"\\div": "÷",
    r"\\approx": "≈", r"\\neq": "≠", r"\\leq": "≤", r"\\geq": "≥",
    r"\\ll": "≪", r"\\gg": "≫", r"\\equiv": "≡", r"\\sim": "~",
    r"\\in": "∈", r"\\notin": "∉", r"\\subset": "⊂", r"\\supset": "⊃",
    r"\\cup": "∪", r"\\cap": "∩", r"\\emptyset": "∅",
    r"\\sum": "Σ", r"\\prod": "Π", r"\\int": "∫", r"\\oint": "∮",
    r"\\to": "→", r"\\rightarrow": "→", r"\\leftarrow": "←",
    r"\\Rightarrow": "⇒", r"\\Leftarrow": "⇐", r"\\Leftrightarrow": "⇔",
    r"\\forall": "∀", r"\\exists": "∃",
    r"\\pm": "±", r"\\mp": "∓",
    r"\\langle": "⟨", r"\\rangle": "⟩",
}


def _latex_to_text(s: str) -> str:
    """將常見 LaTeX 數學語法轉成可讀的 Unicode/純文字。"""
    # 結構性
    s = re.sub(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"(\1)/(\2)", s)
    s = re.sub(r"\\sqrt\s*\{([^{}]+)\}", r"√(\1)", s)
    s = re.sub(r"\\sum_\{([^{}]+)\}\^\{([^{}]+)\}", r"Σ_{\1}^{\2}", s)
    s = re.sub(r"\\prod_\{([^{}]+)\}\^\{([^{}]+)\}", r"Π_{\1}^{\2}", s)
    s = re.sub(r"\\int_\{([^{}]+)\}\^\{([^{}]+)\}", r"∫_{\1}^{\2}", s)

    # 字體
    s = re.sub(r"\\mathbb\s*\{([^{}]+)\}", r"\1", s)
    s = re.sub(r"\\mathbf\s*\{([^{}]+)\}", r"**\1**", s)
    s = re.sub(r"\\mathcal\s*\{([^{}]+)\}", r"\1", s)
    s = re.sub(r"\\mathrm\s*\{([^{}]+)\}", r"\1", s)
    s = re.sub(r"\\text\s*\{([^{}]+)\}", r"\1", s)
    s = re.sub(r"\\operatorname\s*\{([^{}]+)\}", r"\1", s)

    # 上下標(簡單版)
    s = re.sub(r"\^\{([^{}]+)\}", r"^(\1)", s)
    s = re.sub(r"_\{([^{}]+)\}", r"_(\1)", s)

    # 希臘字母與符號
    for pat, rep in GREEK_MAP.items():
        s = re.sub(pat + r"(?![a-zA-Z])", rep, s)

    # 剩餘 backslash 命令(沒處理到的)→ 移除 backslash
    s = re.sub(r"\\([a-zA-Z]+)", r"\1", s)

    # 清掉多餘 braces
    s = re.sub(r"\{([^{}]*)\}", r"\1", s)

    return s.strip()


def _convert_math_delims(text: str) -> str:
    """把 $...$、$$...$$、\\(...\\)、\\[...\\] 轉成 Discord 可讀格式。"""
    # $$...$$ → 獨立行的 inline code(放 backtick 比 code block 不會吃太多空間)
    def block(m):
        return "`" + _latex_to_text(m.group(1)) + "`"
    text = re.sub(r"\$\$(.+?)\$\$", block, text, flags=re.DOTALL)

    # \[...\] → 同上
    text = re.sub(r"\\\[(.+?)\\\]", block, text, flags=re.DOTALL)

    # $...$ → inline backtick
    def inline(m):
        return "`" + _latex_to_text(m.group(1)) + "`"
    text = re.sub(r"\$([^\$\n]+?)\$", inline, text)

    # \(...\) → inline backtick
    text = re.sub(r"\\\((.+?)\\\)", inline, text, flags=re.DOTALL)

    return text


def _convert_tables(text: str) -> str:
    """將 markdown 表格包進 code block(monospace 至少能對齊)。"""
    lines = text.split("\n")
    out, buf, in_table = [], [], False

    def is_table_row(line: str) -> bool:
        s = line.strip()
        return s.startswith("|") and s.count("|") >= 2

    for line in lines:
        if is_table_row(line):
            if not in_table:
                in_table = True
                buf = []
            buf.append(line)
        else:
            if in_table:
                out.append("```")
                out.extend(buf)
                out.append("```")
                in_table = False
                buf = []
            out.append(line)

    if in_table:
        out.append("```")
        out.extend(buf)
        out.append("```")

    return "\n".join(out)


def format_for_discord(text: str) -> str:
    """把模型輸出整理成 Discord 可正確顯示的格式。"""
    if not text:
        return text

    # 1. 先保護已存在的 code block 與 inline code,避免被後續正則破壞
    placeholders = {}

    def stash(prefix, m):
        key = f"\x00{prefix}{len(placeholders)}\x00"
        placeholders[key] = m.group(0)
        return key

    text = re.sub(r"```[\s\S]*?```", lambda m: stash("CB", m), text)
    text = re.sub(r"`[^`\n]+`", lambda m: stash("IC", m), text)

    # 2. 轉 LaTeX 公式
    text = _convert_math_delims(text)

    # 3. 轉表格
    text = _convert_tables(text)

    # 4. 移除過長連續換行
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 5. 還原 placeholders
    for key, original in placeholders.items():
        text = text.replace(key, original)

    return text


def chunk_text(text: str, size: int = DISCORD_MAX_CHARS):
    """智慧分塊:不切斷 code block,優先切在段落邊界。"""
    chunks, remaining = [], text

    while remaining:
        if len(remaining) <= size:
            chunks.append(remaining)
            break

        # 優先在段落邊界切
        cut = remaining.rfind("\n\n", 0, size)
        if cut < size // 3:
            cut = remaining.rfind("\n", 0, size)
        if cut < size // 3:
            cut = remaining.rfind(" ", 0, size)
        if cut <= 0:
            cut = size

        chunk = remaining[:cut]

        # 檢查是否有未閉合 code block,如有則自動補上
        if chunk.count("```") % 2 == 1:
            chunk = chunk.rstrip() + "\n```"
            rest = "```\n" + remaining[cut:].lstrip("\n")
        else:
            rest = remaining[cut:].lstrip("\n")

        chunks.append(chunk)
        remaining = rest

    return chunks


# ===== Discord 推送 =====
def _discord_json(payload: dict):
    if not DISCORD_WEBHOOK_URL:
        return
    requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=30).raise_for_status()


def _discord_file(filepath: str, message: str = ""):
    if not DISCORD_WEBHOOK_URL or not os.path.exists(filepath):
        return
    with open(filepath, "rb") as f:
        files = {"file": (os.path.basename(filepath), f, "text/markdown")}
        data = {"payload_json": json.dumps({"content": message})}
        requests.post(DISCORD_WEBHOOK_URL, data=data, files=files, timeout=30).raise_for_status()


def notify_discord(stage: int, model: str, reply: str):
    if not DISCORD_WEBHOOK_URL:
        print("[Discord] webhook 未設定,略過")
        return

    meta = STAGE_META[stage]
    ts = datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d %H:%M")

    _discord_json({"embeds": [{
        "title": f"Stage {stage}/5 — {meta['name']}",
        "description": f"**Date:** {today_str}\n**Time:** {ts}\n**Model:** `{model}`",
        "color": meta["color"],
    }]})

    formatted = format_for_discord(reply)
    chunks = chunk_text(formatted)

    for i, c in enumerate(chunks, 1):
        prefix = f"`[{i}/{len(chunks)}]`\n" if len(chunks) > 1 else ""
        _discord_json({"content": prefix + c})

    if stage == 5:
        _discord_file(REPORT_FILE, f"📎 **今日完整報告** ({today_str})")


# ===== API 呼叫(帶 fallback) =====
def safe_completion(messages, model, max_tokens, temperature=0.7):
    try:
        resp = client.chat.completions.create(
            model=model, messages=messages,
            temperature=temperature, max_tokens=max_tokens,
        )
        return resp, model
    except APIStatusError as e:
        if e.status_code in (413, 429) and model != MODEL_REASONING:
            print(f"[fallback] {model} 失敗 ({e.status_code}),改用 {MODEL_REASONING}")
            resp = client.chat.completions.create(
                model=MODEL_REASONING, messages=messages,
                temperature=temperature, max_tokens=max_tokens,
            )
            return resp, MODEL_REASONING
        raise


# ===== 摘要壓縮 =====
def generate_summary(stage: int, full_text: str) -> str:
    sys_msg = (
        "你是研究助理,擅長精煉長文,只保留最關鍵的事實、結論、技術細節。"
        "使用繁體中文。禁止 LaTeX 與表格,改用條列。"
    )
    user_msg = (
        f"請將以下 Stage {stage} ({STAGE_META[stage]['name']}) 內容濃縮為結構化摘要。"
        "用條列式列出最關鍵的事實、結論、技術細節、論點、引用的 paper 名稱。"
        "讓接續階段能在不讀原文的情況下精準延伸。字數 300–500 字。\n\n"
        f"=== 原始內容 ===\n{full_text}"
    )
    resp = client.chat.completions.create(
        model=MODEL_SUMMARY,
        messages=[{"role": "system", "content": sys_msg},
                  {"role": "user", "content": user_msg}],
        temperature=0.3,
        max_tokens=MAX_TOKENS_SUMMARY,
    )
    return resp.choices[0].message.content.strip()


# ===== 訊息組裝 =====
def build_messages(stage: int, summaries: list, prompts: dict) -> list:
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]

    if summaries:
        ctx = "以下是先前各階段的研究摘要,請依此延伸:\n\n"
        for s in summaries:
            ctx += f"### Stage {s['stage']} — {STAGE_META[s['stage']]['name']}\n{s['summary']}\n\n"
        msgs.append({"role": "user", "content": ctx.strip()})
        msgs.append({"role": "assistant",
                     "content": "了解,我已掌握前面各階段的研究內容,請給我下一個任務。"})

    msgs.append({"role": "user", "content": prompts[stage]})
    return msgs


# ===== 報告 =====
def append_report(stage, model, prompt, reply, summary):
    os.makedirs("reports", exist_ok=True)
    ts = datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d %H:%M:%S")
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"## Stage {stage} — {ts}\n\n"
            f"**Model:** `{model}`\n\n"
            f"**Prompt:**\n\n{prompt}\n\n"
            f"**Response (full):**\n\n{reply}\n\n"
            f"**Summary (passed to next stage):**\n\n{summary}\n\n---\n\n"
        )


# ===== 每階段 temperature 微調 =====
STAGE_TEMPERATURE = {
    1: 0.6,   # 探索:中等溫度,平衡多樣性與聚焦
    2: 0.5,   # 深入分析:偏低,要求精確
    3: 0.85,  # 創新發想:高溫,鼓勵跳躍
    4: 0.5,   # 嚴格批判:偏低,要求嚴謹
    5: 0.4,   # 整合提案:低溫,確保穩定整合
}


# ===== 主流程 =====
def main():
    state = load_state()
    step = state["step"]

    if step > 5:
        print(f"今天 ({state['date']}) 5 階段已完成")
        return

    print(f"=== Stage {step} | date={state['date']} ===")
    print(f"今日輪替焦點:{get_today_focus()}")

    prompts = build_stage_prompts()
    messages = build_messages(step, state["summaries"], prompts)
    primary = get_model(step)
    temp = STAGE_TEMPERATURE.get(step, 0.7)
    print(f"主模型: {primary} | temperature: {temp}")

    response, used_model = safe_completion(
        messages, primary, MAX_TOKENS_MAIN, temperature=temp,
    )
    reply = response.choices[0].message.content
    print(f"主模型回應完成 (實際用 {used_model}),長度 {len(reply)} 字")

    # 寫報告 + 推 Discord
    append_report(step, used_model, prompts[step], reply, summary="(產生中...)")
    try:
        notify_discord(step, used_model, reply)
    except Exception as e:
        print(f"[Discord] 推送失敗: {e}")

    # 壓縮摘要供下一階段使用
    print(f"產生 Stage {step} 摘要...")
    try:
        summary = generate_summary(step, reply)
    except Exception as e:
        print(f"[Warn] 摘要失敗 ({e}),使用截斷版內容")
        summary = reply[:1500]

    state["summaries"].append({"stage": step, "summary": summary})
    state["step"] = step + 1
    save_state(state)
    print(f"✓ Stage {step} 完成,摘要已存檔")

    # Stage 5 結束後,把今日主題寫進歷史,供未來避免重複
    if step == 5:
        stage1_summary = next(
            (s["summary"] for s in state["summaries"] if s["stage"] == 1), ""
        )
        save_history_entry(today_str, stage1_summary, summary)
        print(f"✓ 今日主題已寫入 {HISTORY_FILE}")


if __name__ == "__main__":
    main()
