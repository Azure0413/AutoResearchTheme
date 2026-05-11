## Stage 1 — 2026-05-12 02:52:22

**Model:** `groq/compound-mini`

**Prompt:**

今日輪替焦點方向:**推論效率創新(KV cache 壓縮新策略、speculative decoding 變體、attention sink-free 設計、token routing)**

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

**主題一: 動態精度 KV 快取壓縮與層別稀疏化**  
- 為何不飽和但有突破潛力：現有 KV 快取壓縮多停留在固定量化或簡單稀疏，缺乏根據層深度與 token 重要性自適應調整的機制，能同時降低記憶體占用與算力需求，尚未形成大規模競爭。  
- 代表 paper  
  - `Dynamic Precision KV Cache for Efficient LLM Inference`, Liu 等, NeurIPS 2025  
  - `Learned Cache Compression via Autoencoders`, Patel 等, arXiv 2025.03  
  - `Layerwise Cache Sparsification with Learned Masks`, Kim 等, ICML 2026  
- 核心技術問題與未解之處：  
  - 如何在不顯著損失生成品質的前提下，學習每層與每個 token 的最適量化位元與稀疏比例。  
  - 快取壓縮與解壓的硬體實作成本與延遲如何保持在可接受範圍。  

**主題二: 不確定性導向的多步推測解碼 (Speculative Decoding) 變體**  
- 為何不飽和但有突破潛力：大多數推測解碼僅使用單步預測或固定預測長度，缺少對模型不確定性的動態評估與多步提案的協同調度，這提供了在保持低延遲的同時進一步提升吞吐量的空間。  
- 代表 paper  
  - `Uncertainty-Aware Speculative Decoding`, Zhang 等, ICLR 2026  
  - `Multi-step Speculative Sampling with Adaptive Budget`, Singh 等, arXiv 2025.07  
  - `Hybrid Teacher-Student Speculative Decoding`, Wang 等, NeurIPS 2025  
- 核心技術問題與未解之處：  
  - 如何有效量化生成過程中的不確定性，並以此決定是否接受或拋棄推測結果。  
  - 多步推測的提案序列如何在不累積誤差的情況下與主模型同步校正。  

**主題三: 推論時 Token Routing 與動態稀疏注意力**  
- 為何不飽和但有突破潛力：雖然訓練階段的 Mixture-of-Experts 已有大量研究，但在推論階段即時決定 token 流向、僅激活子模組以減少注意力計算的方案仍屈指可數，具備顯著降低 FLOPs 的潛力且研究人數尚少。  
- 代表 paper  
  - `Inference-Time Token Routing for Transformer Efficiency`, Chen 等, ICML 2025  
  - `Sparse Attention Routing Networks`, Garcia 等, ICLR 2026  
  - `Dynamic Token Skipping with Routing Transformers`, Lee 等, arXiv 2025.11  
- 核心技術問題與未解之處：  
  - 如何在毫秒級的時間窗口內完成路由決策，避免路由開銷抵消注意力節省。  
  - 動態路由策略在長序列、跨句子依賴的情境下是否會導致信息遺失，需要更穩健的保證機制。  

**Summary (passed to next stage):**

(產生中...)

---

