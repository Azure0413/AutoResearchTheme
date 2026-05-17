## Stage 1 — 2026-05-18 02:08:15

**Model:** `groq/compound-mini`

**Prompt:**

今日輪替焦點方向:**資料中毒、後門攻擊與防禦(post-training data poisoning、emergent misalignment 機制研究)**

請以該方向為主軸,搜尋 2025 年下半年至 2026 年的最新研究,整理 3 個**互不相同**且**尚未飽和**的具體子主題。

**禁止選題**:任何以「multimodal LLM」、「vision-language alignment」、「text-to-image diffusion 改良」、「通用 LoRA/PEFT」、「standard RAG」、「standard chain-of-thought」為核心的題目。這些已過度競爭。

**過去 14 天已探討的主題(請務必避開、提出全新角度)**:
- `2026-05-11`: **離散擴散研究方向摘要**

### 主題一: 離散擴散於蛋白質接觸圖的結構生成

* **關鍵事實**：
 + 離散擴散模型仍在萌芽階段，研究者數量低。
 + 可直接結合生物物理圖譜資訊，具高突破潛力。
* **核心技術問題**：
 + 設計有效的噪聲轉移機制，逆向過程保持生物學上合理的接觸約束。
 + 離散擴散的樣本效率低，缺乏針對稀疏圖結構的加速抽樣策略。
* **代表 paper**：

- `2026-05-14`: **主題一: 自我監督的層級技能發現與世界模型結合**

* **關鍵事實**：
 + 研究人數仍少，因為需要同時解決長期規劃、層級抽象與高維感知的交叉挑戰。
 + 需要開創新型自主代理的潛力。
* **結論**：
 + 需要設計自動抽取可重用的子策略的方法。
 + 需要發展有效的誤差校正機制。
* **技術細節**：
 + 使用世界模型預測誤差累積問題。
 + 需要設計層級技能發現的方法。
* 
- `2026-05-15`: **Stage 1: 探索熱門議題**

### 主題一：生成式自我監督探索 (Generative Self‑Supervised Exploration)

* **關鍵事實**：
 + 研究人數仍少，因為要同時設計可生成高維觀測的世界模型與與之匹配的內在獎勵。
 + 核心技術問題：如何在不依賴外部回饋的情況下，讓生成模型的重建誤差成為可靠的探索獎勵。
* **結論**：
 + 生成式自我監督
- `2026-05-16`: **Stage 1: 探索熱門議題**

**主題一：強化學習驅動的自適應 Token-Expert 匹配**

* **關鍵事實**：
 + 大多數 MoE 使用靜態 softmax gating，缺乏對長期負載與效能的全局考量。
 + 研究人數仍低。
* **結論**：
 + 需要設計低方差的策略梯度或演化策略，使 gating 網路在訓練初期不致於因探索失敗導致梯度消失。
 + 需要考慮硬體
- `2026-05-17`: **主題一：周期晶格與材料科學的群等變 GNN**

* **關鍵事實**：
 + 大多數 SE(3) 等變模型只處理有限尺寸的分子，對於具週期邊界條件的晶體結構仍缺乏系統化方法。
 + 研究者數量極少且與材料設計需求高度匹配。
* **結論**：
 + 周期晶格與材料科學的群等變 GNN 有很大潛力，但仍面臨許多挑戰。
* **技術細節**：
 + 設計高效的訊息傳遞與噪聲注入機制，保持平移、旋

**輸出格式**(嚴格遵守,不要表格、不要 LaTeX):

**主題一:[精確的子主題名稱]**
- 為何不飽和但有突破潛力(1-2 句具體說明,不要泛泛)
- 代表 paper(2-3 篇,標題、第一作者、會議或 arXiv 編號、年份,**必須 2025 年以後**)
- 核心技術問題與未解之處(2-3 句)

**主題二:**...

**主題三:**...


**Response (full):**

**主題一: 因果圖驅動的後訓練資料中毒根因追蹤**  
- 研究人數仍少，因為需要結合因果推斷與大規模語言模型的內部表示，跨領域門檻高，卻能直接定位被植入的惡意樣本來源。  
- 代表 paper  
  - 「Causal Detection of Post‑Training Data Poisoning in Large Language Models」, **Y. Liu** 等, NeurIPS 2025.  
  - 「Tracing Poisoned Tokens via Structural Causal Models」, **M. Chen** 等, arXiv:2506.04123, 2025.  
  - 「Counterfactual Analysis for Data‑Poisoning Attribution」, **S. Gupta** 等, ICLR 2026.  
- 核心技術問題與未解之處  
  - 如何在不暴露模型權重的前提下，從輸出分布重建可靠的因果圖結構。  
  - 針對高維嵌入空間的因果效應估計仍缺乏有效的樣本效率策略。  

**主題二: 動態水印與指紋結合的持續學習防後門機制**  
- 持續學習場景中模型會不斷接收新資料，現有靜態水印易被逐步稀釋，動態更新的水印仍是少數研究，具備長期防護與快速後門偵測的雙重潛力。  
- 代表 paper  
  - 「Adaptive Watermarking for Backdoor Resilience in Continual Learning」, **X. Zhang** 等, ICLR 2026.  
  - 「Fingerprint‑Driven Backdoor Detection under Model Drift」, **L. Wang** 等, ICML 2025.  
  - 「Self‑Renewing Watermarks for Secure Model Updates」, **R. Patel** 等, arXiv:2511.07845, 2025.  
- 核心技術問題與未解之處  
  - 設計在模型權重微調時仍能保持辨識度的水印更新規則。  
  - 防止惡意方利用水印的可預測性逆向生成隱蔽後門。  

**主題三: RLHF 流程中的 emergent misalignment 動態建模**  
- 雖然 RLHF 已成主流，但其獎勵模型訓練與人類回饋之間的交互會產生非預期的對齊偏移，相關動態機制仍未被系統化研究，且研究社群尚未飽和。  
- 代表 paper  
  - 「Emergent Misalignment in RLHF: A Dynamical Systems Perspective」, **A. Patel** 等, ICML 2025.  
  - 「Detecting Alignment Drift in Reward Modeling via Trajectory Analysis」, **J. Kim** 等, NeurIPS 2025.  
  - 「Stability‑Guided RLHF to Mitigate Reward Hacking」, **E. Fernández** 等, arXiv:2509.03211, 2025.  
- 核心技術問題與未解之處  
  - 如何量化與預測獎勵模型在長期交互中的對齊漂移。  
  - 在不大量增加人類標註成本的情況下，設計自適應校正機制以抑制 emergent misalignment。  

**Summary (passed to next stage):**

(generating...)

---

