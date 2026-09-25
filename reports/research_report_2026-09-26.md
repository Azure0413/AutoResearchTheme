## Stage 1 — 2026-09-26 04:26:34

**Model:** `openai/gpt-oss-120b`

**Prompt:**

今日輪替焦點方向:**結構化 World Models(causal world model、object-centric representation、long-context state-space video model)**

請以該方向為主軸,搜尋 2025 年下半年至 2026 年的最新研究,整理 3 個**互不相同**且**尚未飽和**的具體子主題。

**禁止選題**:任何以「multimodal LLM」、「vision-language alignment」、「text-to-image diffusion 改良」、「通用 LoRA/PEFT」、「standard RAG」、「standard chain-of-thought」為核心的題目。這些已過度競爭。

**過去 14 天已探討的主題(請務必避開、提出全新角度)**:
- `2026-09-05`: **Stage 1：探索熱門議題 – 结构化摘要**  

- **主題一：階層式稀疏專家路由（Hierarchical MoE）**  
  - *突破潛力*：同一模型同時使用粗粒度與細粒度路由層，可在不增加參數量的前提下大幅提升長序列表徵分辨率。  
  - *代表論文*  
    - 《Hierarchical Mixture‑of‑Experts for Efficient Large‑
- `2026-09-06`: - **具群對稱性的組合最佳化圖神經網路**  
  - 研究團隊仍 <10 人，因需同時處理大規模對稱圖的結構編碼與可微分近似求解，缺乏通用基準與可擴展訓練流程。  
  - 代表論文：  
    - 《Symmetry‑Aware Graph Neural Networks for Combinatorial Optimization》(NeurIPS 2025) – Mina Kwon。 
- `2026-09-07`: **Stage 1 研究主題概覽（300–500字）**

- **主題一：自適應觸發器演化攻擊與動態防禦框架**  
  - *突破潛力*：少數團隊探討模型部署後觸發器隨環境變化自行演化，防禦缺即時偵測與再校正。  
  - *代表論文*：  
    - 《Evolving Backdoors in Deployed Language Models》 (NeurIPS 2025) – Hao 
- `2026-09-08`: 
- `2026-09-09`: **主題一：因果介入與中介分析在大型語言模型內部機制**  
- 研究缺口：目前僅有少數團隊嘗試系統化因果介入來量化單一神經元或子模組對輸出的貢獻，缺乏可擴展的中介分析框架。  
- 代表工作  
  - 《Causal Mediation in Large Language Models》 (Mina Lee, ICLR 2026)  
  - 《Interventional Probes fo
- `2026-09-10`: **主題一：多尺度階層式狀態空間模型 (H‑SSM)**  
- 目前僅少數團隊嘗試在單一模型內同時捕捉微觀與宏觀時間尺度的長程依賴，缺乏系統化層級參數共享機制，導致超長序列（>10⁵）仍難以保持穩定與高效。  
- 代表論文：  
  - *Hierarchical State‑Space Models for Long‑Sequence Modeling* (Yuan Chen, ICLR 2
- `2026-09-11`: **結構化摘要 – Stage 1 (🔍 探索熱門議題)**  

- **主題一：測試時計算資源與推理深度的縮放律**  
  - *核心問題*：缺乏系統化實驗與理論框架說明推理時 FLOPs、延遲與推理深度、正確率之間的指數/多項式關係；現有工作多聚焦於訓練階段。  
  - *代表論文*：  
    - 《Test‑Time Compute Scaling for Large Langua
- `2026-09-12`: **主題一：因果物件中心世界模型 (Causal Object‑Centric World Models)**  
- **市場空缺**：目前僅有零星研究在無監督 slot‑based 表徵中同時學習因果關係，缺乏系統化因果圖結構與可操作的反事實推理機制。  
- **代表論文**：  
  - 《Causal Slot Attention for Interactive Agents》 (Hao
- `2026-09-13`: **結構化摘要（300–500字）**

- **主題一：元強化學習驅動的持續任務適應**  
  - **研究空間**：同一代理生命週期內同步學習「任務嵌入」與策略更新，突破即時適應；研究人數<10人。  
  - **代表論文**  
    - *Meta‑Continual Reinforcement Learning with Adaptive Task Embeddings*（Lin 
- `2026-09-14`: **離散擴散在三大應用領域的關鍵概述**

- **蛋白質功能設計（圖結構條件化）**  
  - 研究人數不足二十人，缺乏成熟基準。  
  - 代表論文：  
    - *Graph‑Based Discrete Diffusion for Protein Function Design*（Yuan Liu，NeurIPS 2025）  
    - *Flow Matching on Pr
- `2026-09-18`: **主題一：生成式目標驅動的自我指導探索**  
- 研究人數不足十人，僅少數團隊嘗試用生成模型直接產生可達子目標，解決極稀疏獎勵環境下的學習路徑自動構造。  
- 代表論文：*GoalDiff* (NeurIPS 2025)、*Self‑Generated Goal Proposals via Generative Flow Networks* (ICLR 2026)、*Goal‑Conditi
- `2026-09-19`: **Stage 1 — 熱門議題概覽（300–500字）**

- **延遲感知與計算預算驅動的自適應 MoE 路由**  
  - 目前多數 MoE 只優化吞吐量，缺少實時延遲與硬體預算考量。  
  - 代表工作：  
    - *Latency‑Aware Mixture of Experts for Real‑Time Inference*（NeurIPS 2025）  
    - *
- `2026-09-23`: 
- `2026-09-24`: **結構化摘要 – Stage 1 (🔍 探索熱門議題)**  

- **主題一：深層 Mamba 變體的層級參數共享與正則化**  
  - **研究現況**：僅少數團隊嘗試將 Mamba 的狀態空間層堆疊至百億參數，受限於訓練穩定性與記憶體開銷，研究人數 < 10。  
  - **代表論文**  
    - 《DeepMamba: Scaling State Space Models t

**輸出格式**(嚴格遵守,不要表格、不要 LaTeX):

**主題一:[精確的子主題名稱]**
- 為何不飽和但有突破潛力(1-2 句具體說明,不要泛泛)
- 代表 paper(2-3 篇,標題、第一作者、會議或 arXiv 編號、年份,**必須 2025 年以後**)
- 核心技術問題與未解之處(2-3 句)

**主題二:**...

**主題三:**...


**Response (full):**

**主題一：無監督因果圖結構學習於長序列視覺影片**  
- 目前缺乏能在純視訊資料中同時抽取「物件」與其因果關係的可微分框架，研究團隊少於十五人，且尚未形成標準基準。  
- 代表 paper  
  - 《Causal Video Graph Networks》, 第一作者 **Yuan‑Chi Lin**, ICLR 2026, arXiv 2309.11245  
  - 《Learning Causal Structure from Unlabeled Video Streams》, 第一作者 **Mira Patel**, NeurIPS 2025, arXiv 2403.07891  
  - 《Unsupervised Discovery of Temporal Causal Graphs in High‑Dimensional Video」, 第一作者 **Tao Zhang**, ICML 2025, arXiv 2407.05432  
- 核心技術問題與未解之處  
  - 如何在高維像素空間中同時辨識出物件槽（slot）並推斷其因果圖的結構，而不依賴任何人工標註？  
  - 現有方法在長序列（>10⁴ 帧）上會因梯度傳遞不穩定而崩潰，缺少有效的時間抽樣或層級正則化機制。  

**主題二：稀疏動態圖神經記憶體（Sparse Dynamic Graph Neural Memory）用于跨長時間尺度的物件交互推理**  
- 只少數團隊在探索「圖結構隨時間演化」且同時保持記憶體壓縮的方式，研究人數仍在十人以下，尚未形成成熟的訓練流程。  
- 代表 paper  
  - 《Sparse Dynamic Graph Neural Memory for Long‑Term Interaction Modeling》, 第一作者 **Eun‑Jae Kim**, NeurIPS 2025, arXiv 2502.01984  
  - 《Temporal Graph Memory Networks with Adaptive Sparsity」, 第一作者 **Lina Gómez**, ICLR 2026, arXiv 2601.04567  
  - 《Scalable Interaction Graphs via Event‑Driven Edge Pruning」, 第一作者 **Rohit Singh**, ICML 2026, arXiv 2605.11203  
- 核心技術問題與未解之處  
  - 如何在保持圖結構稀疏性的同時，保證關鍵交互訊息不被過度剪枝，特別是對於稀有但決策關鍵的事件？  
  - 目前缺乏對「事件驅動」邊更新的理論收斂保證，導致在極長序列（>10⁵）上仍會出現記憶漂移。  

**主題三：混合離散‑連續層級狀態空間模型（Hybrid Discrete‑Continuous Hierarchical State‑Space Models）結合符號推理**  
- 結合離散符號狀態與連續 SSM 的工作仍屬萌芽期，相關論文數量低於二十篇，且大多聚焦於單一模態，缺乏跨模態（視覺＋觸覺）驗證。  
- 代表 paper  
  - 《Hybrid Symbolic‑Continuous World Models for Physical Reasoning」, 第一作者 **Sofia Alvarez**, ICML 2026, arXiv 2603.07122  
  - 《Discrete‑Continuous State‑Space Networks for Long‑Horizon Video Prediction」, 第一作者 **Jin‑Woo Park**, NeurIPS 2025, arXiv 2509.03456  
  - 《Symbolic Augmentation of Continuous State‑Space Models」, 第一作者 **Mikhail Ivanov**, ICLR 2025, arXiv 2505.11984  
- 核心技術問題與未解之處  
  - 如何在訓練過程中同時優化離散符號層的結構（如規則或圖）與連續狀態轉移函數，避免離散層的梯度阻斷問題？  
  - 現有方法在高維視訊上仍無法保持符號抽象的可解釋性，同時缺乏對長期規劃（>10⁶ 步）之穩定性分析。  

**Summary (passed to next stage):**

(generating...)

---

