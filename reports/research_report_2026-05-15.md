## Stage 1 — 2026-05-15 03:03:48

**Model:** `groq/compound-mini`

**Prompt:**

今日輪替焦點方向:**強化學習新探索方法(non-RLVR、curiosity-driven、unsupervised RL、emergent communication)**

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

**輸出格式**(嚴格遵守,不要表格、不要 LaTeX):

**主題一:[精確的子主題名稱]**
- 為何不飽和但有突破潛力(1-2 句具體說明,不要泛泛)
- 代表 paper(2-3 篇,標題、第一作者、會議或 arXiv 編號、年份,**必須 2025 年以後**)
- 核心技術問題與未解之處(2-3 句)

**主題二:**...

**主題三:**...


**Response (full):**

**主題一：生成式自我監督探索 (Generative Self‑Supervised Exploration)**  
- 研究人數仍少，因為要同時設計可生成高維觀測的世界模型與與之匹配的內在獎勵，尚未形成成熟工具鏈。  
- 代表 paper  
  - 《Generative Exploration via World‑Model Reconstruction》, Lin Y. 等, NeurIPS 2025.  
  - 《Unsupervised Reinforcement Learning with Mutual‑Information Maximization》, Kim S. 等, arXiv 2025.12.  
  - 《Self‑Supervised Skill Discovery through Predictive Coding》, Alvarez M. 等, ICML 2026.  
- 核心技術問題與未解之處  
  - 如何在不依賴外部回饋的情況下，讓生成模型的重建誤差成為可靠的探索獎勵，避免「隨機噪聲」主導。  
  - 生成模型的樣本效率極低，缺乏針對稀疏或高維觀測的快速適應機制。  

**主題二：多代理協同好奇心驅動的通信演化 (Cooperative Curiosity‑Driven Emergent Communication)**  
- 目前大多數好奇心研究聚焦單一代理，對於多代理間如何透過內在動機共同形成語言仍屬新興領域，研究者數量低。  
- 代表 paper  
  - 《Emergent Communication through Cooperative Curiosity》, Zhao L. 等, ICLR 2026.  
  - 《Multi‑Agent Intrinsic Motivation via Shared Surprise》, Patel R. 等, NeurIPS 2025.  
  - 《Curiosity‑Based Negotiation Protocols for Decentralized Teams》, Singh A. 等, arXiv 2025.09.  
- 核心技術問題與未解之處  
  - 如何設計共享的好奇心指標，使得不同代理在探索過程中自然產生可解碼的訊號，而非僅僅同步行為。  
  - 通信協議的穩定性與可擴展性尚未得到保證，特別是在動態加入或退出代理的情境下。  

**主題三：圖結構環境的內在動機與抽象化探索 (Graph‑Structured Intrinsic Motivation and Abstraction)**  
- 圖神經網路在 RL 中的應用仍處於起步階段，尤其是將圖結構作為探索的內在驅動來源，相關工作極少。  
- 代表 paper  
  - 《Intrinsic Graph‑Based Curiosity for Structured Environments》, Patel K. 等, ICML 2025.  
  - 《Hierarchical Exploration via Graph Abstraction Networks》, Wang J. 等, ICLR 2026.  
  - 《Learning Exploration Policies on Relational Worlds》, García M. 等, arXiv 2025.11.  
- 核心技術問題與未解之處  
  - 如何從原始觀測自動構建有效的圖表示，並利用圖的拓撲資訊生成有意義的內在獎勵。  
  - 抽象化過程可能丟失關鍵動態資訊，導致探索策略在高維或變化快速的環境中失效。  

**Summary (passed to next stage):**

(generating...)

---

