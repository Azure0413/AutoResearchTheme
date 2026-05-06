# AutoResearchTheme — AI 自動研究議題助理

每天晚上自動完成 **「探索議題 → 深挖方法 → 創新發想 → 自我批判 → 完整提案」** 的 5 階段研究循環，並將每階段結果即時推送到你的 Discord 頻道。

底層使用 Groq 的 LLM API + GitHub Actions cron 排程，**完全免費可運作**（在 Groq 與 GitHub 的 free tier 內）。

---

## 目錄

- [系統運作概念](#系統運作概念)
- [Pipeline 流程](#pipeline-流程)
- [使用的模型與分工](#使用的模型與分工)
- [檔案結構](#檔案結構)
- [部署步驟](#部署步驟)
- [排程設定](#排程設定)
- [Discord 呈現方式](#discord-呈現方式)
- [自訂與調整](#自訂與調整)
- [疑難排解](#疑難排解)

---

## 系統運作概念

GitHub Actions 是 **stateless** 的——每次跑完容器就銷毀，沒辦法像本機程式一樣把對話歷史留在記憶體。所以這個系統用三件事保留狀態：

1. **`state.json`**：記錄「今天跑到第幾階段」、「前面階段的濃縮摘要」。
2. **`reports/research_report_YYYY-MM-DD.md`**：當天完整對話紀錄（人類閱讀用）。
3. **每次跑完自動 git commit + push**：把 state 與 report 推回 repo，下一個小時的 Action 才能讀到上一輪的進度。

跨日（台北時間日期變動）會自動重置 step 為 1，並開新的 report 檔。

---

## Pipeline 流程

```
[ 21:00 ]  Stage 1  🔍 探索熱門議題
              ↓ (本階段完整輸出 → 推 Discord + 存 report)
              ↓ (用 8B 小模型壓成 ~400 字摘要 → 存 state.json)
[ 22:00 ]  Stage 2  📖 深入相關方法
              ↓ (吃 Stage 1 的摘要,延伸分析)
[ 23:00 ]  Stage 3  💡 提出創新方法
              ↓ (吃 Stage 1+2 的摘要)
[ 00:00 ]  Stage 4  🔥 嚴格自我批判
              ↓ (吃 Stage 1+2+3 的摘要)
[ 01:00 ]  Stage 5  ✅ 完整研究提案
              ↓ (吃 Stage 1+2+3+4 的摘要,整合輸出)
              ↓ (附上整份 report.md 推到 Discord)
```

**為什麼用「摘要傳遞」而不是「完整對話傳遞」？**

最初設計是把完整對話歷史每次都重送，但會發生兩個問題：
1. Stage 4–5 時 input token 累積到 30k+，超過 free tier 的單次請求大小，**直接 413 Request Entity Too Large**。
2. 浪費大量 token，每天用量翻倍。

解法：每階段結束後用便宜的 `llama-3.1-8b-instant` 把該階段的完整輸出壓成 ~400 字結構化摘要，下一階段只吃摘要。整體 input token 從原本累積式增長變成幾乎恆定（~2k–3k tokens），徹底避開 413。

---

## 使用的模型與分工

| 用途 | 模型 | 為什麼選它 |
|------|------|-----------|
| Stage 1, 2（找最新 paper） | `groq/compound-mini` | 內建 Tavily web search，能即時搜尋論文。比 `groq/compound` 延遲低 3×、payload 較小，避開 413 |
| Stage 3, 4, 5（純推理） | `llama-3.3-70b-versatile` | 不需要網路搜尋，70B 推理品質好，128k context 充裕 |
| 摘要壓縮（每階段結束後） | `llama-3.1-8b-instant` | 8B 模型快又便宜，壓縮文本綽綽有餘 |
| Fallback（出錯時降級） | `llama-3.3-70b-versatile` | 當 compound-mini 遇到 413/429 時自動切換 |

**自動 fallback 機制**：如果 Stage 1 或 2 在呼叫 compound-mini 時拿到 413（payload 太大）或 429（rate limit），程式會自動改用 `llama-3.3-70b-versatile` 重試。代價是該階段拿不到當下最新的 paper（只能用模型訓練截止前的知識），但流程不會中斷。

---

## 檔案結構

```
AutoResearchTheme/
├── .github/
│   └── workflows/
│       └── research_agent.yml      # GitHub Actions 排程設定
├── reports/                        # 每日完整報告(自動產生)
│   ├── research_report_2026-05-07.md
│   └── research_report_2026-05-08.md
├── state.json                      # 狀態檔(自動產生),跨日自動重置
├── agent.py                        # 主程式
├── requirements.txt
└── README.md
```

`state.json` 範例：

```json
{
  "date": "2026-05-07",
  "step": 3,
  "summaries": [
    { "stage": 1, "summary": "今日找到的 3 大熱門議題:..." },
    { "stage": 2, "summary": "Stage 1 中的 Diffusion 主題..." }
  ]
}
```

---

## 部署步驟

### 1. 準備 API Keys

- **Groq API Key**：到 [console.groq.com/keys](https://console.groq.com/keys) 註冊（免費），建立 key
- **Discord Webhook URL**：
  1. 你的 Discord 伺服器 → 建立或選一個頻道
  2. 頻道設定（⚙️）→ 整合 → Webhooks → 新增
  3. 取名後複製 Webhook URL
  4. 本機用 curl 測試：
     ```bash
     curl -H "Content-Type: application/json" \
          -d '{"content":"hello"}' \
          "<你的 webhook URL>"
     ```

### 2. 建立 GitHub Repo

建議設為 **Private**（state.json 會包含完整研究內容）。

### 3. 加入 Secrets

Repo → **Settings → Secrets and variables → Actions → New repository secret**：

| Name | Value |
|------|-------|
| `GROQ_API_KEY` | 你的 Groq key |
| `DISCORD_WEBHOOK_URL` | 你的 Discord webhook |

### 4. 開啟寫權限

Repo → **Settings → Actions → General** → 滾到底 **Workflow permissions** → 選 **Read and write permissions** → Save

（沒這步驟 Action 沒辦法 push 回 repo，state 會無法保存）

### 5. 推上三個檔案

`agent.py`、`requirements.txt`、`.github/workflows/research_agent.yml` commit 並 push。

### 6. 手動測試

Repo → **Actions** 頁籤 → 選 *Daily Research Agent* → **Run workflow** 按鈕。

預期：
- Discord 頻道收到 Stage 1 的彩色 embed + 內文
- Repo 多出 `state.json` 和 `reports/research_report_YYYY-MM-DD.md`

連續手動觸發 5 次，驗證 Stage 2–5 都能正確接續，最後一次 Stage 5 會多附一個完整的 .md 檔到 Discord。

---

## 排程設定

預設台北時間 **晚上 9:00 → 凌晨 1:00**，每整點觸發一次（共 5 次）。

`.github/workflows/research_agent.yml` 內的 cron：

```yaml
- cron: '0 13,14,15,16,17 * * *'   # UTC 時間
```

**換算說明**（台北 = UTC+8）：

| 台北時間 | UTC 時間 |
|---------|---------|
| 21:00 | 13:00 |
| 22:00 | 14:00 |
| 23:00 | 15:00 |
| 00:00 | 16:00 |
| 01:00 | 17:00 |

**想改時間範例**：

```yaml
# 22:00–02:00（晚一小時）
- cron: '0 14,15,16,17,18 * * *'

# 21:00–02:00 跑 6 階段(需自己加 Stage 6 邏輯)
- cron: '0 13,14,15,16,17,18 * * *'

# 早上 9–13 點
- cron: '0 1,2,3,4,5 * * *'
```

> **重要**：GitHub Actions 排程**不保證準時**，高峰期可能延遲 30 分鐘到數小時。間距 1 小時設計是有意預留 buffer——即使 Stage 1 延遲 30 分鐘，Stage 2 仍有半小時空間執行。

---

## Discord 呈現方式

每階段你會在頻道看到（範例）：

```
┌─────────────────────────────────────┐
│ Stage 1/5 — 🔍 探索熱門議題         │   ← 藍色 embed header
│ Date: 2026-05-07                    │
│ Time: 21:00                         │
│ Model: groq/compound-mini           │
└─────────────────────────────────────┘
1/3
（AI 回應第一段...）

2/3
（AI 回應第二段...）

3/3
（AI 回應第三段...）
```

**5 個階段顏色不同**：藍 → 綠 → 紫 → 橘 → 金。

**Stage 5 結束**多送一個 message，附上整天的完整 Markdown 報告檔，可直接從 Discord 下載。

**訊息分塊邏輯**：Discord 單則訊息上限 2000 字元，程式會以「換行」為優先切點分塊，避免從句中切斷。

---

## 自訂與調整

### 改提示詞（最常需要調整的）

修改 `agent.py` 裡的 `STAGE_PROMPTS` 字典。建議在 Stage 1 prompt 中**指定具體子領域、年份、會議名**，比換模型有用：

```python
STAGE_PROMPTS = {
    1: ("請搜尋 NeurIPS 2024 與 CVPR 2025 中關於 "
        "Diffusion model 在 video generation 領域的最新研究..."),
    # ...
}
```

### 改回應長度

`agent.py` 開頭：

```python
MAX_TOKENS_MAIN = 2048      # 每階段主回應的最大 tokens
MAX_TOKENS_SUMMARY = 600    # 摘要最大 tokens
```

### 改模型

也在 `agent.py` 開頭：

```python
MODEL_RESEARCH = "groq/compound-mini"
MODEL_REASONING = "llama-3.3-70b-versatile"
MODEL_SUMMARY = "llama-3.1-8b-instant"
```

可選的 Groq 模型清單：[console.groq.com/docs/models](https://console.groq.com/docs/models)。

### 強制重置今日進度

刪掉 `state.json`，下次 Action 跑時會自動從 Stage 1 開始。

---

## 疑難排解

### 1. `413 Request Entity Too Large`

**原因**：單次 request 的 input + max_tokens 超過 tier 上限。

**已實作的對策**：
- 用 `groq/compound-mini` 而非 `groq/compound`
- 摘要傳遞而非完整歷史
- 自動 fallback 到 `llama-3.3-70b-versatile`

如果還是發生，把 `MAX_TOKENS_MAIN` 從 2048 降到 1500，或直接把所有 stage 改成 `llama-3.3-70b-versatile`（放棄 web search）。

### 2. `429 Too Many Requests`

Free tier 的 RPM (requests per minute) 或 TPM (tokens per minute) 達上限。我們一小時才一個 request，正常不會碰到，除非你手動連續觸發測試。等 1 分鐘再試。

### 3. Discord 沒收到訊息

依序檢查：
- `DISCORD_WEBHOOK_URL` Secret 有沒有設？
- Webhook URL 用 curl 測試有效嗎？
- Action log 裡 `notify_discord` 步驟有錯誤訊息嗎？

### 4. Action 沒按時觸發

GitHub 排程不保證準時，特別是熱門時段。對策：
- **Repo 不能太久沒活動**：超過 60 天沒 push 會自動停用排程。每天的 Action commit 其實已經自動解決這問題。
- 如果排程嚴重延遲影響使用，可改用外部服務（如 cron-job.org）呼叫 GitHub `repository_dispatch` API 強制觸發。

### 5. Push 失敗 / 衝突

`workflow_permissions` 沒設成 read/write。回到 Settings → Actions → General 修正。

### 6. 想看摘要長什麼樣

打開 `reports/research_report_YYYY-MM-DD.md`，每個 stage 區塊最後都有 "Summary (passed to next stage)" 欄位，那就是傳給下一階段的內容。如果發現摘要漏掉重要資訊，可以調整 `agent.py` 裡 `generate_summary()` 的 system prompt。

---

## 成本估算

以一天 5 階段、每階段 ~2k tokens 輸出計算：

- Stage 1, 2 用 `compound-mini`：~$0.001/天
- Stage 3, 4, 5 用 `llama-3.3-70b-versatile`：~$0.002/天
- 摘要 5 次用 `llama-3.1-8b-instant`：~$0.0003/天

**一天總成本約 < $0.005**（Groq 也有 free tier 額度，初期通常完全免費）。

GitHub Actions free tier：2000 分鐘/月，每次跑 ~2 分鐘 × 5 次/天 = 300 分鐘/月，遠低於額度。

---

## 授權與貢獻

本專案為個人用途範本，可自由 fork 修改。
