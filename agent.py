import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from groq import Groq

# ===== 基本設定 =====
TAIPEI_TZ = ZoneInfo("Asia/Taipei")
STATE_FILE = "state.json"
DISCORD_MAX_CHARS = 1900   # Discord 訊息上限 2000，預留 buffer

today_str = datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d")
REPORT_FILE = f"reports/research_report_{today_str}.md"

client = Groq(api_key=os.environ["GROQ_API_KEY"])
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()

# ===== 五階段元資料（Discord embed 顏色 + emoji）=====
STAGE_META = {
    1: {"name": "🔍 探索熱門議題", "color": 0x3498DB},
    2: {"name": "📖 深入相關方法", "color": 0x2ECC71},
    3: {"name": "💡 提出創新方法", "color": 0x9B59B6},
    4: {"name": "🔥 嚴格自我批判", "color": 0xE67E22},
    5: {"name": "✅ 完整研究提案", "color": 0xF1C40F},
}

STAGE_PROMPTS = {
    1: ("請搜尋並整理近 1–2 年資訊科學領域（特別是生成式模型、影像處理、"
        "多模態、Diffusion、Transformer 改良等方向）最熱門的研究議題與代表性 paper。"
        "請列出 3 個具潛力的具體主題，每個主題須包含："
        "(a) 主題說明 (b) 2–3 篇代表 paper 標題與年份 (c) 為何此方向值得深入。"
        "你可以使用網路搜尋工具確認最新性。"),

    2: ("根據你上一輪提出的熱門研究議題，請挑選你判斷最值得深入的 1 個主題，"
        "詳細探討該主題下相關 paper 採用的核心方法、模型架構、訓練策略、資料集,"
        "並比較不同方法的優劣。可使用網路搜尋找最新方法。"),

    3: ("基於前兩輪累積的研究議題與現有方法分析,請發揮創意,"
        "提出 3–5 種「具體可實作」的創新研究方法或架構改良。"
        "每個方案須包含:核心 idea、技術細節、與現有方法的差異、預期改善的指標。"
        "請避免空泛建議。"),

    4: ("現在請扮演嚴格的學術審稿人。針對你上一輪提出的每一個創新方法,"
        "從以下角度給出嚴厲批判:(1) 理論假設是否成立 (2) 資料集與訓練可行性 "
        "(3) 計算資源與硬體需求 (4) 是否真的優於既有 SOTA (5) 潛在的 failure mode。"
        "對每個批判同時提出可能的補救方向。"),

    5: ("綜合前面四輪的議題探索、方法分析、創新發想與自我批判,"
        "整合出「一個最完善、最值得執行」的研究提案。輸出格式:"
        "1. 研究痛點與背景  2. 核心研究方法與技術細節  3. 與既有方法的差異與創新性  "
        "4. 實驗設計(資料集、baseline、評估指標)  5. 預期貢獻與影響。"
        "請寫成可直接拿去做提案的完整版本。")
}


def get_model(stage: int) -> str:
    """Stage 1, 2 需要找最新 paper → 用內建網路搜尋的 compound;其餘純推理。"""
    return "groq/compound" if stage in (1, 2) else "llama-3.3-70b-versatile"


# ===== Discord 推送 =====
def chunk_text(text: str, size: int = DISCORD_MAX_CHARS):
    """以換行為優先切點分塊,避免從句子中間斷掉。"""
    chunks, remaining = [], text
    while remaining:
        if len(remaining) <= size:
            chunks.append(remaining)
            break
        cut = remaining.rfind("\n", 0, size)
        if cut < size // 2:        # 找不到合理斷點就硬切
            cut = size
        chunks.append(remaining[:cut])
        remaining = remaining[cut:].lstrip("\n")
    return chunks


def _discord_json(payload: dict):
    if not DISCORD_WEBHOOK_URL:
        return
    r = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=30)
    r.raise_for_status()


def _discord_file(filepath: str, message: str = ""):
    if not DISCORD_WEBHOOK_URL or not os.path.exists(filepath):
        return
    with open(filepath, "rb") as f:
        files = {"file": (os.path.basename(filepath), f, "text/markdown")}
        data = {"payload_json": json.dumps({"content": message})}
        r = requests.post(DISCORD_WEBHOOK_URL, data=data, files=files, timeout=30)
        r.raise_for_status()


def notify_discord(stage: int, model: str, reply: str):
    if not DISCORD_WEBHOOK_URL:
        print("[Discord] webhook 未設定,略過推送")
        return

    meta = STAGE_META[stage]
    ts = datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d %H:%M")

    # 1. 階段 header(embed)
    _discord_json({
        "embeds": [{
            "title": f"Stage {stage}/5 — {meta['name']}",
            "description": f"**Date:** {today_str}\n**Time:** {ts}\n**Model:** `{model}`",
            "color": meta["color"],
        }]
    })

    # 2. 內容切塊送
    chunks = chunk_text(reply)
    for i, c in enumerate(chunks, 1):
        prefix = f"`{i}/{len(chunks)}`\n" if len(chunks) > 1 else ""
        _discord_json({"content": prefix + c})

    # 3. Stage 5 完成後,附上整份 Markdown 檔
    if stage == 5:
        _discord_file(REPORT_FILE, f"📎 **今日完整報告** ({today_str})")


# ===== 狀態管理 =====
def new_state() -> dict:
    return {
        "date": today_str,
        "step": 1,
        "messages": [{
            "role": "system",
            "content": ("你是一位頂尖的 AI 演算法研究員,擅長深度學習與論文發想。"
                        "回答必須專業、邏輯嚴密、有具體技術細節,避免空泛敘述。"
                        "全程使用繁體中文。")
        }]
    }


def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return new_state()
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
    if state.get("date") != today_str:    # 跨日自動重置
        return new_state()
    return state


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def append_report(stage: int, model: str, prompt: str, reply: str) -> None:
    os.makedirs("reports", exist_ok=True)
    ts = datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d %H:%M:%S")
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"## Stage {stage} — {ts}\n\n"
            f"**Model:** `{model}`\n\n"
            f"**Prompt:**\n\n{prompt}\n\n"
            f"**Response:**\n\n{reply}\n\n---\n\n"
        )


# ===== 主流程 =====
def main():
    state = load_state()
    step = state["step"]

    if step > 5:
        print(f"今天 ({state['date']}) 五階段已完成。")
        return

    model = get_model(step)
    prompt = STAGE_PROMPTS[step]
    print(f"=== Stage {step} | model={model} | date={state['date']} ===")

    state["messages"].append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        messages=state["messages"],
        model=model,
        temperature=0.7,
        max_tokens=4096,
    )
    reply = response.choices[0].message.content

    state["messages"].append({"role": "assistant", "content": reply})

    append_report(step, model, prompt, reply)

    try:
        notify_discord(step, model, reply)
    except Exception as e:
        # Discord 失敗不要影響整體流程
        print(f"[Discord] 推送失敗: {e}")

    state["step"] = step + 1
    save_state(state)
    print(f"Stage {step} 完成")


if __name__ == "__main__":
    main()
