# 洗面乳評論分析系統
本項目使用Python進行開發，旨在從特定網站抓取洗面乳產品的用戶評論，通過自然語言處理（NLP）技術分析評論內容，計算產品的平均評分和效果，並使用Word2Vec模型來分析評論文本，從而為用戶提供產品推薦。

## 功能特點
- 抓取指定網站上的洗面乳產品評論。
- 分析評論內容，提取關鍵詞和評分。
- 使用Word2Vec技術進行文本分析，生成詞向量。
- 基於相似度推薦相關產品。

## 技術線
- Python
- BeautifulSoup：用於網頁內容抓取。
- pandas：數據處理和分析。
- jieba：中文分詞。
- Gensim：實現Word2Vec模型。
- MySQL：存儲抓取的數據。
- OpenAI GPT：生成評論的優缺點。
- scikit-learn：計算文本之間的相似度。

## 項目結構

```plaintext  
.  
├── config.json            # 配置文件，包含數據庫連接和API密鑰等信息。  
├── effect.txt             # 自定義的詞典文件，用於jieba分詞。  
├── stopword.txt           # 停用詞文件，用於文本預處理。  
├── dict.txt.big           # jieba分詞的大詞典，適用於繁體中文。  
├── word.txt               # 自定義分詞詞典。  
└── 1_crawl+word2vec.py    # 主腳本，實現項目的核心功能。
```

## 環境準備
確保你的系統已安裝Python 3和必要的庫。你可以通過運行以下命令來安裝所需的Python庫：  

```plaintext  
pip install beautifulsoup4 pandas jieba gensim mysql-connector-python openai scikit-learn  
```
## 配置
在config.json文件中配置你的數據庫信息和API密鑰：

```plaintext 
{
  "user": "your_database_user",
  "password": "your_database_password",
  "host": "your_database_host",
  "port": "your_database_port",
  "url": ["your_target_url_for_scraping"]
}
```

## 運行
運行主腳本開始抓取數據並分析：  

```plaintext 
python 1_crawl+word2vec.py
```

## 貢獻
歡迎貢獻代碼或提出改進建議，可以通過GitHub的Issue或Pull Request進行。
