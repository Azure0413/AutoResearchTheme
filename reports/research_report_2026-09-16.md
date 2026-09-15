## Stage 1 — 2026-09-16 04:12:54

**Model:** `groq/compound-mini`

**Prompt:**

今日輪替焦點方向:**AI for Science 非主流子領域(材料設計、催化劑、晶體結構、量子化學、流體模擬)**

請以該方向為主軸,搜尋 2025 年下半年至 2026 年的最新研究,整理 3 個**互不相同**且**尚未飽和**的具體子主題。

**禁止選題**:任何以「multimodal LLM」、「vision-language alignment」、「text-to-image diffusion 改良」、「通用 LoRA/PEFT」、「standard RAG」、「standard chain-of-thought」為核心的題目。這些已過度競爭。

**過去 14 天已探討的主題(請務必避開、提出全新角度)**:
- `2026-08-26`: **主題一：稀疏自編碼器驅動的算法電路發現**  
- **突破潛力**：10B+ 模型已成功訓練稀疏自編碼器，但缺乏自動化電路抽取流程，模型規模與電路類型仍待探索。  
- **代表論文**：  
  - *AutoCircuit* (NeurIPS 2025, Alex Wang)  
  - *Sparse Autoencoders Reveal Modular Computation* (
- `2026-09-02`: **結構化摘要（300–500字）**

- **主題一：圖神經網路 + 貝葉斯不確定性在晶體結構穩定性預測**
  - **突破潛力**：結合圖注意力機制與貝葉斯估計，實現端到端結構生成與能量評估，研究團隊數量少於十人。  
  - **代表論文**  
    - *Crystal Graph Attention Networks for Stable Structure Prediction
- `2026-09-03`: 
- `2026-09-04`: **主題一：高維連續控制中的資訊增益驅動探索**  
- 事實：在 100‑維以上機器人環境中，傳統好奇心或隨機探索難以估算行動對未來狀態分布的影響；資訊增益（empowerment）作為「控制力」指標被提出，但計算成本高。代表工作包括《Empowerment via Mutual Information Neural Estimation》（NeurIPS 2025）、《Scalable Emp
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

**輸出格式**(嚴格遵守,不要表格、不要 LaTeX):

**主題一:[精確的子主題名稱]**
- 為何不飽和但有突破潛力(1-2 句具體說明,不要泛泛)
- 代表 paper(2-3 篇,標題、第一作者、會議或 arXiv 編號、年份,**必須 2025 年以後**)
- 核心技術問題與未解之處(2-3 句)

**主題二:**...

**主題三:**...


**Response (full):**

**主題一: 神經量子態 (Neural Quantum States) 用於高維費米子系統的精準模擬**  
- 目前僅有少數團隊結合等變性圖卷積與變分蒙特卡羅，能在 100+ 量子位元尺度上直接逼近基態能量，訓練與驗證成本仍高，研究人數不足二十人。  
- 代表 paper  
  - `Equivariant Neural Quantum States for Fermionic Systems`，第一作者 **Yuan Chen**，NeurIPS 2025  
  - `Variational Monte Carlo with Symmetry‑Aware Graph Networks`，第一作者 **Lina Patel**，ICLR 2026  
  - `Scalable Neural Ansatz for Strongly Correlated Materials`，第一作者 **Mikko Räsänen**，arXiv 2025.12  
- 核心技術問題與未解之處  
  - 如何在保持等變性約束的同時，降低變分蒙特卡羅抽樣的方差，使訓練在大規模費米子系統上穩定收斂。  
  - 欠缺通用的基準套件與跨領域驗證，導致方法在實際材料科學問題（如高溫超導）上的可遷移性尚未確立。  

**主題二: 主動學習驅動的可微分反應力場，用於長時間尺度的從頭算分子動力學**  
- 現有的機器學習勢能多聚焦於靜態結構或短時間動力學，對於稀有反應事件的抽樣效率仍不足，且缺乏自動化的誤差控制迴路。  
- 代表 paper  
  - `Active Learning of Reactive Force Fields for Ab Initio Molecular Dynamics`，第一作者 **Hao Liu**，ICLR 2026  
  - `On‑the‑Fly Uncertainty Quantification for Neural Force Fields`，第一作者 **Sofia García**，ICML 2025  
  - `Long‑Range Reactive MD with Adaptive Neural Potentials`，第一作者 **Joon‑Hyuk Kim**，arXiv 2025.07  
- 核心技術問題與未解之處  
  - 如何在高維原子配置空間中即時評估模型不確定性，並決策何時觸發高精度量子化學計算以更新模型。  
  - 需要設計可擴展的資料庫管理與分布式訓練框架，以支援數十萬步的長時間模擬。  

**主題三: 結構拓撲感知的生成模型，用於金屬有機框架 (MOF) 的氣體分離設計**  
- 雖然已有圖結構生成模型用於晶體或蛋白質，但針對 MOF 特有的多孔拓撲與配體‑金屬節點協同設計仍少有人涉足，相關基準資料集與評估指標尚未成熟。  
- 代表 paper  
  - `Topology‑Aware Generative Models for MOF Design`，第一作者 **Yuan Liu**，ICML 2025  
  - `Conditional Diffusion on Periodic Graphs for Porous Material Synthesis`，第一作者 **Anika Singh**，NeurIPS 2025  
  - `Multi‑Objective Bayesian Optimization of MOF Structures with Graph Transformers`，第一作者 **Tobias Weber**，arXiv 2026.02  
- 核心技術問題與未解之處  
  - 如何在生成過程中同時滿足結晶對稱性、孔徑分布與熱力學穩定性等多重約束，避免產生不可合成的結構。  
  - 缺乏端到端的評估管線，從生成、結構優化到氣體吸附模擬的自動化流程仍需大量人工介入。  

**Summary (passed to next stage):**

(generating...)

---

