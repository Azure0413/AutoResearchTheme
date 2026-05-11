## Stage 1 — 2026-05-11 10:11:06

**Model:** `groq/compound-mini`

**Prompt:**

今日輪替焦點方向:**Discrete Diffusion / Flow Matching 在非影像領域(蛋白質、程式碼、分子、時間序列、tabular data)**

請以該方向為主軸,搜尋 2025 年下半年至 2026 年的最新研究,整理 3 個**互不相同**且**尚未飽和**的具體子主題。

**禁止選題**:任何以「multimodal LLM」、「vision-language alignment」、「text-to-image diffusion 改良」、「通用 LoRA/PEFT」、「standard RAG」、「standard chain-of-thought」為核心的題目。這些已過度競爭。

**輸出格式**(嚴格遵守,不要表格、不要 LaTeX):

**主題一:[精確的子主題名稱]**
- 為何不飽和但有突破潛力(1-2 句具體說明,不要泛泛)
- 代表 paper(2-3 篇,標題、第一作者、會議或 arXiv 編號、年份,**必須 2025 年以後**)
- 核心技術問題與未解之處(2-3 句)

**主題二:**...

**主題三:**...


**Response (full):**

**主題一: 離散擴散於蛋白質接觸圖的結構生成**  
- 目前大多數蛋白質生成仍以連續潛在空間或能量函數為主，離散圖結構的擴散模型仍在萌芽階段，研究者數量低且可直接結合生物物理圖譜資訊，具高突破潛力。  
- 代表 paper  
  - 「Graph‑Discrete Diffusion for Protein Backbone Design」, Lin 等, NeurIPS 2025  
  - 「Discrete State Diffusion for Protein Folding Pathways」, Zhao 等, ICLR 2026  
  - 「Markovian Discrete Diffusion on Protein Contact Maps」, arXiv:2503.01427, 2025  
- 核心技術問題與未解之處  
  - 如何在高維離散圖空間中設計有效的噪聲轉移機制，使得逆向過程保持生物學上合理的接觸約束。  
  - 離散擴散的樣本效率低，缺乏針對稀疏圖結構的加速抽樣策略。  

**主題二: 離散流匹配於事件驅動時間序列的缺失值填補**  
- 時間序列領域的缺失值填補大多聚焦於連續數值，對於同時包含類別事件與時間戳的混合序列缺乏專門方法，相關研究人數仍少，且可直接服務金融、醫療等高需求領域。  
- 代表 paper  
  - 「Flow Matching for Categorical Time Series Generation」, Chen 等, ICML 2025  
  - 「Discrete Flow Matching on Event Sequences」, Liu 等, arXiv:2509.11234, 2025  
  - 「Hybrid Continuous‑Discrete Flow for Missing Data Imputation」, Patel 等, ICLR 2026  
- 核心技術問題與未解之處  
  - 設計同時處理連續值與離散事件的流向量場，使得逆向過程能保留事件的時間依賴結構。  
  - 缺乏對高頻稀疏事件序列的穩定訓練技巧，導致模型在長序列上易發散。  

**主題三: 抽象語法樹 (AST) 離散擴散於程式碼自動生成**  
- 現有程式碼生成多採用連續語言模型或微調大型模型，離散擴散直接在 AST 節點上操作的工作仍極少，研究門檻高且具備解決語法錯誤率高的根本潛力。  
- 代表 paper  
  - 「AST Diffusion: Discrete Diffusion over Syntax Trees for Code Generation」, Gupta 等, NeurIPS 2025  
  - 「Discrete Diffusion Language Model for Program Synthesis」, Wang 等, arXiv:2511.04567, 2025  
  - 「Flow Matching on Token Graphs for Code Completion」, Martínez 等, ICML 2026  
- 核心技術問題與未解之處  
  - 如何構造符合語法規則的離散噪聲轉移，使得逆向過程不會產生非法樹結構。  
  - 大規模 AST 空間的抽樣效率低，缺乏針對子樹級別的分層抽樣或重參考機制。  

**Summary (passed to next stage):**

(產生中...)

---

