"""
Daily Research Agent — robust edition.

主要改動(全部目的:不要再卡在 stage 3/4/5):

1. State 推進提前:拿到主 API 回應立刻存 state,後續所有步驟(report/discord/summary)
   都允許失敗,不會回頭影響進度。

2. safe_completion 強化:transient errors (429, 5xx, timeout, connection error)
   走指數退避重試;重試耗盡才走 fallback ladder。

3. Fallback ladder:reasoning → research → summary 三層,最後一層 8b 模型
   幾乎不會掛,確保至少有東西產出。

4. Per-stage max_tokens:stage 3 從 2048 提到 4096(原本對 3-5 個方案根本不夠,
   被 truncate 也算半失敗)。

5. 失敗計數 + 降級 prompt:同一階段累積失敗 ≥ 2 次,自動切到簡化 prompt,
   保證每天能跑完五階段。

6. Top-level error handler:任何 pre-state-advancement 失敗都會推到 Discord,
   並把失敗計數寫回 state.json(然後 return 而不是 raise,確保 GitHub Actions
   的 commit 步驟還能跑、把計數推到遠端)。

7. Groq client timeout 拉長到 180s(預設過短)。
"""

import os
import re
import json
import time
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from groq import Groq

# Groq error 類別 — 防禦式 import(版本可能略有差異)
try:
    from groq import APIStatusError
except ImportError:
    APIStatusError = Exception
try:
    from groq import APITimeoutError
except ImportError:
    APITimeoutError = Exception
try:
    from groq import APIConnectionError
except ImportError:
    APIConnectionError = Exception


# ===== 基本設定 =====
TAIPEI_TZ = ZoneInfo("Asia/Taipei")
STATE_FILE = "state.json"
HISTORY_FILE = "topic_history.json"
HISTORY_DAYS = 14
DISCORD_MAX_CHARS = 1900

today_str = datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d")
REPORT_FILE = f"reports/research_report_{today_str}.md"

# timeout 拉長 — stage 3 配 4096 tokens 在 Groq 上有可能跑 1-2 分鐘
client = Groq(api_key=os.environ["GROQ_API_KEY"], timeout=180.0)
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()


# ===== 模型分配 =====
MODEL_RESEARCH = "groq/compound-mini"          # Stage 1, 2 — 內建 web search
MODEL_REASONING = "llama-3.3-70b-versatile"    # Stage 3, 4, 5 — 純推理
MODEL_SUMMARY = "llama-3.1-8b-instant"         # 摘要壓縮 / 最後 fallback

# Per-stage max_tokens(關鍵修正:stage 3 本來 2048 嚴重不夠)
STAGE_MAX_TOKENS = {
    1: 2048,
    2: 2048,
    3: 4096,   # 要產出 3-5 個詳細方案
    4: 3072,   # 每個方案 5+ 個批判點
    5: 4096,   # 完整最終提案
}
MAX_TOKENS_SUMMARY = 600

# 重試 / fallback 設定
MAX_RETRIES = 3                       # 每個模型的最大重試次數
MAX_FAILURES_BEFORE_DEGRADE = 2       # 同階段累積失敗幾次後切到降級 prompt


# ===== 每日輪替焦點 =====
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


# Stage 3 的降級 prompt — 連續失敗後用這個確保能跑完
DEGRADED_STAGE_3_PROMPT = (
    "前面已分析過主題與方法。**注意:之前用完整 prompt 失敗過,本次採用精簡版。**\n\n"
    "請提出 **2 個** 具體可實作的創新方法,每個方案精簡輸出,避免冗長:\n\n"
    "**方案 X:[名稱]**\n"
    "- 核心 idea(1 句話)\n"
    "- 技術細節(3-4 句話,具體說明改了哪個元件)\n"
    "- 與 SOTA 的差異(2 句話)\n"
    "- 預期改善的指標(1 句話)\n"
    "- MVP 設計(1 句話)\n\n"
    "**禁止**任何 LaTeX 與表格。每個方案總字數控制在 200-300 字。"
)


def get_model(stage: int) -> str:
    return MODEL_RESEARCH if stage in (1, 2) else MODEL_REASONING


# ===== 狀態管理 =====
def new_state() -> dict:
    return {
        "date": today_str,
        "step": 1,
        "summaries": [],
        "failures": {},  # str(stage) -> 連續失敗次數
    }


def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return new_state()
    with open(STATE_FILE, encoding="utf-8") as f:
        state = json.load(f)
    if state.get("date") != today_str:
        return new_state()
    state.setdefault("failures", {})  # 舊版 state 沒有這欄
    return state


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ===== 主題歷史管理 =====
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
    history = [h for h in history if h.get("date") != date]
    history.append({
        "date": date,
        "stage1_topics": stage1_summary[:400],
        "final_proposal": stage5_summary[:300],
    })
    history = sorted(history, key=lambda x: x["date"])[-HISTORY_DAYS:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def build_history_avoid_block() -> str:
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
    s = re.sub(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"(\1)/(\2)", s)
    s = re.sub(r"\\sqrt\s*\{([^{}]+)\}", r"√(\1)", s)
    s = re.sub(r"\\sum_\{([^{}]+)\}\^\{([^{}]+)\}", r"Σ_{\1}^{\2}", s)
    s = re.sub(r"\\prod_\{([^{}]+)\}\^\{([^{}]+)\}", r"Π_{\1}^{\2}", s)
    s = re.sub(r"\\int_\{([^{}]+)\}\^\{([^{}]+)\}", r"∫_{\1}^{\2}", s)
    s = re.sub(r"\\mathbb\s*\{([^{}]+)\}", r"\1", s)
    s = re.sub(r"\\mathbf\s*\{([^{}]+)\}", r"**\1**", s)
    s = re.sub(r"\\mathcal\s*\{([^{}]+)\}", r"\1", s)
    s = re.sub(r"\\mathrm\s*\{([^{}]+)\}", r"\1", s)
    s = re.sub(r"\\text\s*\{([^{}]+)\}", r"\1", s)
    s = re.sub(r"\\operatorname\s*\{([^{}]+)\}", r"\1", s)
    s = re.sub(r"\^\{([^{}]+)\}", r"^(\1)", s)
    s = re.sub(r"_\{([^{}]+)\}", r"_(\1)", s)
    for pat, rep in GREEK_MAP.items():
        s = re.sub(pat + r"(?![a-zA-Z])", rep, s)
    s = re.sub(r"\\([a-zA-Z]+)", r"\1", s)
    s = re.sub(r"\{([^{}]*)\}", r"\1", s)
    return s.strip()


def _convert_math_delims(text: str) -> str:
    def block(m):
        return "`" + _latex_to_text(m.group(1)) + "`"
    text = re.sub(r"\$\$(.+?)\$\$", block, text, flags=re.DOTALL)
    text = re.sub(r"\\\[(.+?)\\\]", block, text, flags=re.DOTALL)

    def inline(m):
        return "`" + _latex_to_text(m.group(1)) + "`"
    text = re.sub(r"\$([^\$\n]+?)\$", inline, text)
    text = re.sub(r"\\\((.+?)\\\)", inline, text, flags=re.DOTALL)
    return text


def _convert_tables(text: str) -> str:
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
    if not text:
        return text
    placeholders = {}

    def stash(prefix, m):
        key = f"\x00{prefix}{len(placeholders)}\x00"
        placeholders[key] = m.group(0)
        return key

    text = re.sub(r"```[\s\S]*?```", lambda m: stash("CB", m), text)
    text = re.sub(r"`[^`\n]+`", lambda m: stash("IC", m), text)
    text = _convert_math_delims(text)
    text = _convert_tables(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    for key, original in placeholders.items():
        text = text.replace(key, original)
    return text


def chunk_text(text: str, size: int = DISCORD_MAX_CHARS):
    chunks, remaining = [], text
    while remaining:
        if len(remaining) <= size:
            chunks.append(remaining)
            break
        cut = remaining.rfind("\n\n", 0, size)
        if cut < size // 3:
            cut = remaining.rfind("\n", 0, size)
        if cut < size // 3:
            cut = remaining.rfind(" ", 0, size)
        if cut <= 0:
            cut = size
        chunk = remaining[:cut]
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


def notify_error_to_discord(stage: int, exc_text: str):
    """把失敗 traceback 推到 Discord,方便排查。"""
    if not DISCORD_WEBHOOK_URL:
        return
    truncated = exc_text[-1500:]
    msg = (
        f"❌ **Stage {stage}/5 失敗 — {today_str}**\n"
        f"```\n{truncated}\n```\n"
        f"(失敗計數會自動累積,連續失敗 {MAX_FAILURES_BEFORE_DEGRADE} 次後切換為簡化 prompt)"
    )
    try:
        _discord_json({"content": msg})
    except Exception as e:
        print(f"[Discord] 連推錯誤通知都失敗了: {e}")


# ===== API 呼叫(強化版) =====
def safe_completion(messages, model, max_tokens, temperature=0.7):
    """
    強化的 Groq chat completion:
    1. transient errors (429, 5xx, timeout, connection) 走指數退避重試
    2. 重試耗盡後沿 fallback ladder 換模型
    3. ladder 都用完才 raise — 這時上層會記錄失敗、推 Discord、return(不 raise)
    """
    if model == MODEL_RESEARCH:
        ladder = [MODEL_RESEARCH, MODEL_REASONING, MODEL_SUMMARY]
    elif model == MODEL_REASONING:
        ladder = [MODEL_REASONING, MODEL_RESEARCH, MODEL_SUMMARY]
    else:
        ladder = [model]

    last_error = None

    for m in ladder:
        for attempt in range(MAX_RETRIES):
            try:
                resp = client.chat.completions.create(
                    model=m,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                if m != model:
                    print(f"[Fallback OK] 用 {m} 替代 {model} 成功")
                return resp, m

            except APIStatusError as e:
                last_error = e
                status = getattr(e, "status_code", None)
                if status == 429:
                    wait = min((2 ** attempt) * 15, 90)
                    print(f"[429] {m} rate limit,等 {wait}s 重試 "
                          f"({attempt + 1}/{MAX_RETRIES})")
                    time.sleep(wait)
                    continue
                if status in (500, 502, 503, 504):
                    wait = (2 ** attempt) * 5
                    print(f"[{status}] {m} server error,等 {wait}s 重試 "
                          f"({attempt + 1}/{MAX_RETRIES})")
                    time.sleep(wait)
                    continue
                if status == 413:
                    print(f"[413] {m} payload 過大,直接換 ladder 下一個模型")
                    break  # 換模型,不重試
                # 其他 4xx
                print(f"[{status}] {m} 不可重試的錯誤: {e}")
                break

            except (APITimeoutError, APIConnectionError) as e:
                last_error = e
                wait = (2 ** attempt) * 5
                print(f"[Network] {m} {type(e).__name__}: {e},等 {wait}s 重試")
                time.sleep(wait)
                continue

            except Exception as e:
                last_error = e
                wait = (2 ** attempt) * 5
                print(f"[Unknown] {m} {type(e).__name__}: {e},等 {wait}s 重試")
                time.sleep(wait)
                continue

        print(f"[Exhausted] {m} 已用盡 {MAX_RETRIES} 次重試,改試 ladder 下一個")

    raise RuntimeError(
        f"所有 fallback 模型都失敗。最後錯誤: "
        f"{type(last_error).__name__}: {last_error}"
    )


# ===== 摘要壓縮(走 safe_completion 確保也有重試) =====
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
    resp, _ = safe_completion(
        messages=[{"role": "system", "content": sys_msg},
                  {"role": "user", "content": user_msg}],
        model=MODEL_SUMMARY,
        max_tokens=MAX_TOKENS_SUMMARY,
        temperature=0.3,
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


# ===== 每階段 temperature =====
STAGE_TEMPERATURE = {
    1: 0.6,
    2: 0.5,
    3: 0.85,
    4: 0.5,
    5: 0.4,
}


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


def get_active_prompt(stage: int, state: dict, prompts: dict) -> str:
    """若此階段累積失敗 >= 門檻,回傳降級 prompt。"""
    fc = int(state.get("failures", {}).get(str(stage), 0))
    if stage == 3 and fc >= MAX_FAILURES_BEFORE_DEGRADE:
        print(f"[Degraded] Stage 3 已連續失敗 {fc} 次,改用簡化 prompt")
        try:
            _discord_json({
                "content": f"⚠️ Stage 3 已連續失敗 {fc} 次,本次改用簡化 prompt 以求完成。"
            })
        except Exception:
            pass
        return DEGRADED_STAGE_3_PROMPT
    return prompts[stage]


# ===== 主流程 =====
def main():
    state = load_state()
    step = state["step"]

    if step > 5:
        print(f"今天 ({state['date']}) 5 階段已完成")
        return

    print(f"=== Stage {step} | date={state['date']} ===")
    print(f"今日輪替焦點:{get_today_focus()}")
    print(f"歷史失敗計數:{state.get('failures', {})}")

    # ===== 區段 A: 計算 prompt / 取得主回應(失敗會記錄失敗計數) =====
    primary = get_model(step)
    temp = STAGE_TEMPERATURE.get(step, 0.7)
    max_tok = STAGE_MAX_TOKENS.get(step, 2048)
    print(f"主模型: {primary} | temperature: {temp} | max_tokens: {max_tok}")

    try:
        prompts = build_stage_prompts()
        active_prompt = get_active_prompt(step, state, prompts)
        prompts_to_use = dict(prompts)
        prompts_to_use[step] = active_prompt
        messages = build_messages(step, state["summaries"], prompts_to_use)

        response, used_model = safe_completion(
            messages, primary, max_tok, temperature=temp,
        )
        reply = response.choices[0].message.content
        print(f"主模型回應完成 (實際用 {used_model}),長度 {len(reply)} 字")

    except Exception:
        tb = traceback.format_exc()
        print(f"[FATAL] Stage {step} 取得主回應失敗:\n{tb}")
        # 失敗計數 +1 然後存檔(關鍵:不要 raise,否則 workflow commit 步驟不會跑)
        state["failures"][str(step)] = int(
            state.get("failures", {}).get(str(step), 0)
        ) + 1
        try:
            save_state(state)
        except Exception as save_err:
            print(f"[Warn] 連 state 都存不下: {save_err}")
        notify_error_to_discord(step, tb)
        return  # 結束本次執行,等下次排程重試

    # ===== 區段 B: 主回應已取得 → 立刻推進 state(這之後失敗都不影響進度) =====
    state["summaries"].append({"stage": step, "summary": reply[:1500]})  # 暫存截斷版
    state["step"] = step + 1
    state["failures"][str(step)] = 0  # 此階段成功,清空失敗計數
    save_state(state)
    print(f"✓ State 已推進到 step {step + 1}")

    # ===== 區段 C: best-effort 後處理(每個獨立 try/except) =====
    try:
        append_report(step, used_model, active_prompt, reply, summary="(generating...)")
    except Exception as e:
        print(f"[Warn] append_report 失敗: {e}")

    try:
        notify_discord(step, used_model, reply)
    except Exception as e:
        print(f"[Warn] Discord 推送失敗: {e}")

    # 摘要生成 — 失敗就保留截斷版
    summary = reply[:1500]
    try:
        print(f"產生 Stage {step} 摘要...")
        summary = generate_summary(step, reply)
        state["summaries"][-1]["summary"] = summary
        save_state(state)
        print(f"✓ Stage {step} 摘要已存檔")
    except Exception as e:
        print(f"[Warn] 摘要失敗 ({e}),保留截斷版內容")

    # 歷史寫入(僅 stage 5)
    if step == 5:
        try:
            stage1_summary = next(
                (s["summary"] for s in state["summaries"] if s["stage"] == 1), ""
            )
            save_history_entry(today_str, stage1_summary, summary)
            print(f"✓ 今日主題已寫入 {HISTORY_FILE}")
        except Exception as e:
            print(f"[Warn] history 寫入失敗: {e}")


if __name__ == "__main__":
    main()
