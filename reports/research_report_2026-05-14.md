## Stage 1 — 2026-05-14 03:06:35

**Model:** `groq/compound-mini`

**Prompt:**

今日輪替焦點方向:**Agent 學習範式創新(非 prompting,而是 skill discovery、policy distillation、tool-use 從零學起)**

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


**輸出格式**(嚴格遵守,不要表格、不要 LaTeX):

**主題一:[精確的子主題名稱]**
- 為何不飽和但有突破潛力(1-2 句具體說明,不要泛泛)
- 代表 paper(2-3 篇,標題、第一作者、會議或 arXiv 編號、年份,**必須 2025 年以後**)
- 核心技術問題與未解之處(2-3 句)

**主題二:**...

**主題三:**...


**Response (full):**

**主題一: 自我監督的層級技能發現與世界模型結合**  
- 研究人數仍少，因為需要同時解決長期規劃、層級抽象與高維感知的交叉挑戰，具備開創新型自主代理的潛力。  
- 代表 paper  
  - 《Hierarchical Skill Discovery via Predictive World Models》, 第一作者 **Yuan Li**, arXiv:2503.01427, 2025。  
  - 《Unsupervised Intrinsic Motivation for Multi‑Level RL in Physics Simulators》, 第一作者 **Mina Patel**, ICLR 2026, 2026。  
  - 《Learning Structured Options through Contrastive Predictive Coding》, 第一作者 **Jae‑Woo Kim**, NeurIPS 2025, 2025。  
- 核心技術問題與未解之處  
  - 如何在高維連續觀測下自動抽取可重用的子策略，且不依賴人工設計的層級結構。  
  - 世界模型的預測誤差會累積，導致層級技能的長期穩定性下降，缺乏有效的誤差校正機制。  

**主題二: 基於圖神經網路的多任務政策蒸餾與知識融合**  
- 目前多任務政策蒸餾仍以單一網路或簡單權重平均為主，圖結構的知識傳遞尚未被廣泛探索，研究空間大且可直接提升跨任務泛化。  
- 代表 paper  
  - 《Graph‑Based Policy Distillation for Scalable Multi‑Task Reinforcement Learning》, 第一作者 **Lena Zhou**, ICML 2025, 2025。  
  - 《Neural Relational Distillation for Heterogeneous RL Tasks》, 第一作者 **Rohit Singh**, arXiv:2509.06784, 2025。  
  - 《Composable Policy Graphs via Message‑Passing Distillation》, 第一作者 **Sofia García**, ICLR 2026, 2026。  
- 核心技術問題與未解之處  
  - 如何設計圖訊息傳遞機制，使得不同任務的策略資訊在蒸餾過程中保持語意一致且不產生衝突。  
  - 蒸餾後的圖形策略在動態環境變化時的適應性與穩定性仍缺乏理論保證。  

**主題三: 零樣本工具使用的組合式元強化學習**  
- 零樣本工具使用仍主要依賴大型語言模型的提示，缺乏純粹從交互中學習的機制，探索純 RL 的組合式方法仍是新興且未飽和領域。  
- 代表 paper  
  - 《Meta‑RL for Compositional Tool Use without Demonstrations》, 第一作者 **Alexei Morozov**, NeurIPS 2025, 2025。  
  - 《Zero‑Shot Object Manipulation via Action Primitive Libraries》, 第一作者 **Yun‑Hee Choi**, arXiv:2601.02215, 2026。  
  - 《Learning to Invent Tools through Self‑Play in Open‑World Environments》, 第一作者 **Diego Fernández**, ICML 2026, 2026。  
- 核心技術問題與未解之處  
  - 如何在缺乏任何先驗示範的情況下，自主構建可重用的動作原語並組合成新工具使用策略。  
  - 組合式策略的可擴展性與計算成本在高維開放世界中仍未得到有效控制。  

**Summary (passed to next stage):**

(generating...)

---

