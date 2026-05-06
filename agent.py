import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from groq import Groq, APIStatusError

# ===== 基本設定 =====
TAIPEI_TZ = ZoneInfo("Asia/Taipei")
STATE_FILE = "state.json"
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

SYSTEM_PROMPT = (
    "你是一位頂尖的 AI 演算法研究員,擅長深度學習與論文發想。"
    "回答必須專業、邏輯嚴密、有具體技術細節,避免空泛敘述。"
    "全程使用繁體中文。"
)

STAGE_META = {
    1: {"name": "🔍 探索熱門議題", "color": 0x3498DB},
    2: {"name": "📖 深入相關方法", "color": 0x2ECC71},
    3: {"name": "💡 提出創新方法", "color": 0x9B59B6},
    4: {"name": "🔥 嚴格自我批判", "color": 0xE67E22},
    5: {"name": "✅ 完整研究提案", "color": 0xF1C40F},
}

STAGE_PROMPTS = {
    1: ("請搜尋並整理近 1–2 年資訊科學領域(特別是生成式模型、影像處理、"
        "多模態、Diffusion、Transformer 改良等方向)最熱門的研究議題與代表性 paper。"
        "請列出 3 個具潛力的具體主題,每個主題包含:"
        "(a) 主題說明 (b) 2–3 篇代表 paper 標題與年份 (c) 為何此方向值得深入。"),

    2: ("根據前一階段的熱門議題,請挑選最值得深入的 1 個主題,"
        "詳細探討該主題下相關 paper 採用的核心方法、模型架構、訓練策略、資料集,"
        "並比較不同方法的優劣。"),

    3: ("基於前兩階段的議題與方法分析,請發揮創意提出 3–5 種「具體可實作」的"
        "創新研究方法或架構改良。每個方案包含:核心 idea、技術細節、與現有方法的差異、"
        "預期改善的指標。請避免空泛建議。"),

    4: ("扮演嚴格的學術審稿人,針對前一階段的每個創新方法給出嚴厲批判,"
        "從以下角度切入:(1) 理論假設 (2) 資料與訓練可行性 (3) 計算資源 "
        "(4) 是否真的優於 SOTA (5) 潛在 failure mode。每個批判同時提出補救方向。"),

    5: ("綜合前四階段,整合出「一個最完善、最值得執行」的研究提案。輸出格式:"
        "1. 研究痛點與背景  2. 核心研究方法與技術細節  3. 與既有方法的差異與創新性  "
        "4. 實驗設計(資料集、baseline、評估指標)  5. 預期貢獻與影響。")
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
    if state.get("date") != today_str:    # 跨日自動重置
        return new_state()
    return state


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ===== 從摘要組訊息(這是省 token 的關鍵) =====
def build_messages(stage: int, summaries: list) -> list:
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]

    if summaries:
        ctx = "以下是先前各階段的研究摘要,請依此延伸:\n\n"
        for s in summaries:
            ctx += f"### Stage {s['stage']} — {STAGE_META[s['stage']]['name']}\n{s['summary']}\n\n"
        msgs.append({"role": "user", "content": ctx.strip()})
        msgs.append({"role": "assistant",
                     "content": "了解,我已掌握前面各階段的研究內容,請給我下一個任務。"})

    msgs.append({"role": "user", "content": STAGE_PROMPTS[stage]})
    return msgs


# ===== 帶 fallback 的 API 呼叫 =====
def safe_completion(messages, model, max_tokens, temperature=0.7):
    try:
        resp = client.chat.completions.create(
            model=model, messages=messages,
            temperature=temperature, max_tokens=max_tokens,
        )
        return resp, model
    except APIStatusError as e:
        # 413 (太大) 或 429 (rate limit) → 降級重試
        if e.status_code in (413, 429) and model != MODEL_REASONING:
            print(f"[fallback] {model} 失敗 ({e.status_code}),改用 {MODEL_REASONING}")
            resp = client.chat.completions.create(
                model=MODEL_REASONING, messages=messages,
                temperature=temperature, max_tokens=max_tokens,
            )
            return resp, MODEL_REASONING
        raise


# ===== 用小模型壓縮摘要 =====
def generate_summary(stage: int, full_text: str) -> str:
    sys_msg = "你是研究助理,擅長精煉長文,只保留最關鍵的事實、結論與技術細節。使用繁體中文。"
    user_msg = (
        f"請將以下 Stage {stage} ({STAGE_META[stage]['name']}) 內容濃縮為結構化摘要。"
        "用條列式列出最關鍵的事實、結論、技術細節、論點。"
        "目標:讓接續的階段能在不讀原文的情況下接續推理。字數 300–500 字。\n\n"
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


# ===== Discord =====
def chunk_text(text: str, size: int = DISCORD_MAX_CHARS):
    chunks, remaining = [], text
    while remaining:
        if len(remaining) <= size:
            chunks.append(remaining); break
        cut = remaining.rfind("\n", 0, size)
        if cut < size // 2:
            cut = size
        chunks.append(remaining[:cut])
        remaining = remaining[cut:].lstrip("\n")
    return chunks


def _discord_json(payload: dict):
    if not DISCORD_WEBHOOK_URL: return
    requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=30).raise_for_status()


def _discord_file(filepath: str, message: str = ""):
    if not DISCORD_WEBHOOK_URL or not os.path.exists(filepath): return
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

    chunks = chunk_text(reply)
    for i, c in enumerate(chunks, 1):
        prefix = f"`{i}/{len(chunks)}`\n" if len(chunks) > 1 else ""
        _discord_json({"content": prefix + c})

    if stage == 5:
        _discord_file(REPORT_FILE, f"📎 **今日完整報告** ({today_str})")


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


# ===== 主流程 =====
def main():
    state = load_state()
    step = state["step"]

    if step > 5:
        print(f"今天 ({state['date']}) 5 階段已完成"); return

    print(f"=== Stage {step} | date={state['date']} ===")

    messages = build_messages(step, state["summaries"])
    primary = get_model(step)
    print(f"主模型: {primary}")

    response, used_model = safe_completion(messages, primary, MAX_TOKENS_MAIN)
    reply = response.choices[0].message.content
    print(f"主模型回應完成 (實際用 {used_model}),長度 {len(reply)} 字")

    # 寫報告 + 推 Discord(用完整內容)
    append_report(step, used_model, STAGE_PROMPTS[step], reply, summary="(產生中...)")
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


if __name__ == "__main__":
    main()
