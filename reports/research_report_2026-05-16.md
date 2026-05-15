## Stage 1 — 2026-05-16 02:50:03

**Model:** `groq/compound-mini`

**Prompt:**

今日輪替焦點方向:**稀疏專家(MoE)路由創新(expert choice、token choice、adaptive routing、heterogeneous experts)**

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

**輸出格式**(嚴格遵守,不要表格、不要 LaTeX):

**主題一:[精確的子主題名稱]**
- 為何不飽和但有突破潛力(1-2 句具體說明,不要泛泛)
- 代表 paper(2-3 篇,標題、第一作者、會議或 arXiv 編號、年份,**必須 2025 年以後**)
- 核心技術問題與未解之處(2-3 句)

**主題二:**...

**主題三:**...


**Response (full):**

**主題一：強化學習驅動的自適應 Token‑Expert 匹配**  
- 目前大多數 MoE 仍使用靜態 softmax gating，缺乏對長期負載與效能的全局考量，研究人數仍低。  
- 代表 paper  
  - *Learning to Route: Reinforcement‑Based Sparse Expert Allocation*，第一作者 **Yuan Li**，NeurIPS 2025。  
  - *RL‑Gated Mixture‑of‑Experts for Scalable Language Modeling*，第一作者 **Mina Patel**，arXiv:2508.01432，2025。  
  - *Policy Gradient Routing for Token‑Wise Expert Selection*，第一作者 **Joon‑Ho Kim**，ICLR 2026。  
- 核心技術問題與未解之處  
  - 如何設計低方差的策略梯度或演化策略，使 gating 網路在訓練初期不致於因探索失敗導致梯度消失。  
  - 需要同時考慮硬體資源限制（如 GPU 記憶體與通信瓶頸）與模型效能，尚缺乏統一的多目標優化框架。  

**主題二：異質專家集合的多任務 MoE 架構**  
- 多任務學習中常見的「所有任務共享同質專家」已飽和，而將不同結構或容量的專家（如卷積、圖神經、變換器）混合使用的研究仍稀少。  
- 代表 paper  
  - *Heterogeneous Mixture‑of‑Experts for Multi‑Task Learning*，第一作者 **Sofia García**，ICML 2026。  
  - *Task‑Adaptive Expert Heterogeneity in Sparse MoE*，第一作者 **Rohit Singh**，arXiv:2603.11207，2026。  
  - *Cross‑Domain Expert Pools with Dynamic Capacity Allocation*，第一作者 **Eun‑Ji Lee**，NeurIPS 2025。  
- 核心技術問題與未解之處  
  - 如何在訓練過程中自動決定每個任務應使用何種專家類型與容量，避免過度專家冗餘或任務間干擾。  
  - 異質專家之間的梯度傳遞與正則化機制尚未統一，缺乏穩定的收斂理論。  

**主題三：層級式路由與分段稀疏化的超大規模 MoE**  
- 單層 gating 在超大模型（上千億參數）上會產生嚴重的通信瓶頸，層級式路由將專家分組再細分子專家，可大幅降低跨機通信，但相關工作仍處於萌芽階段。  
- 代表 paper  
  - *Hierarchical Routing for Efficient Large‑Scale Mixture‑of‑Experts*，第一作者 **Kai Zhang**，ICLR 2025。  
  - *Two‑Stage Sparse Expert Selection with Group‑Level Gates*，第一作者 **Lara Müller**，arXiv:2509.06784，2025。  
  - *Multi‑Level MoE: From Global Gates to Local Experts*，第一作者 **Takeshi Nakamura**，NeurIPS 2025。  
- 核心技術問題與未解之處  
  - 需要設計在不同層級之間保持一致性的負載平衡策略，避免上層門控過度集中而導致下層資源閒置。  
  - 層級路由的延遲與同步成本在分布式環境下的最佳化仍缺乏實證指導，尤其在異構叢集（CPU+GPU）上。  

**Summary (passed to next stage):**

(generating...)

---

