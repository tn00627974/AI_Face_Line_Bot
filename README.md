

<img src="https://github.com/tn00627974/Ai_Face_Linebot/assets/139155210/92b450af-16b7-488d-adfb-56bb3a5e5323" width="200"></h1> 


# 洗面乳識別系統
本項目是一個基於LINE Bot開發的洗面乳推薦系統，使用了Keras的MobileNetV2進行遷移式訓練，並結合了爬蟲和自然語言處理（NLP）技術來分析和獲取網絡上的相關產品評價。整個服務部署在Google Cloud Run上。

<img src="https://i.imgur.com/4w7iZFO.png" alt="替代文字" width="150"/>

↑↑↑歡迎掃描體驗我們的LINE Bot服務

## 成品Demo影片：
https://youtu.be/IO_8H76po74  

## 特點
**1. 圖像識別**：利用Keras的MobileNetV2模型進行遷移式學習，訓練了專門針對洗面乳產品的圖像識別系統。  
**2. 自動爬蟲**：自動抓取網絡上的洗面乳產品評價。  
**3. NLP文本分析**：分析抓取到的評價文本，提供用戶更多維度的產品信息。  
**4. LINE Bot互動**：用戶可以通過LINE Bot上傳洗面乳圖片，系統將返回識別結果及相關評價。  

## 技術線
- Python  
- Keras & TensorFlow   
- 網路爬蟲  
- 自然語言處理（NLP）  
- LINE Messaging API  
- Google Cloud Run  

## 前提條件
- Python版本: 3.8
- Tensorflow版本: 2.4.0
- LINE Developers設定:
  - `channel_access_token`: [你的channel_access_token]
  - `channel_secret`: [你的channel_secret]
  - `end_point`: [你的end_point]
- MySQL設定:
  - `host`: [你的MySQL主機地址]
  - `port`: 3306
  - `user`: [你的MySQL用戶名]
  - `passwd`: [你的MySQL密碼]
- GCP帳戶



## 安裝流程
提供一步步的指南，說明如何安裝必要的依賴、如何本地運行項目以及如何部署到Google Cloud Run。  

**1. 下載完整檔案**: git clone https://github.com/Jay98Lin/AI-Project.git  
**2. 模型部署**: 將`AI_recognition`資料夾中已訓練好的模型`05.MobileNetV2_0212.h5`轉為SavedModel格式, 並用Docker build部署到GCP cloud run  
**3. 自動爬蟲部署**： 將整個`NLP`資料夾透過Docker build方式, 部署到Google Cloud Run  
**4. 準備好您的ＭySQL**: 可將網路爬蟲更新的評論資訊, 放進您的資料庫  
**5. LINE Bot**: 可將`Linebot`資料夾透過Docker build方式, 部署到Google Cloud Run

## 安裝依賴
**自動爬蟲**：至NLP資料夾：pip install -r `requirements.txt`  
**LINE Bot**: 至Linebot資料夾: pip install -r `requirements.txt`  

## 本地運行
經前面敘述, 先將模型＋爬蟲部署至GCP的cloud run(或架在VM)  
可在本地端運行Linebot資料夾中的主程式：`1_linebot_main.py`  
如需雲端服務, 可用Docker build部署到Google Cloud Run  

## 使用說明
此辨識系統目前共有四個功能：  


<img src="https://github.com/tn00627974/Ai_Face_Linebot/assets/139155210/f6f6b59c-ffb2-4411-b410-bc69a0c40770" width="500"></h1> 

**1. 拍照辨識** ：可拍照洗面乳照片，系統會回傳該洗面乳相關的網路評價分數，優缺點以及相關推薦產品給您。  
**2. 選擇膚質** ：使用者可輸入自己的年齡及膚質等資訊，尋找最適合自己的洗面乳及相關推薦產品。  
**3. 收錄品項** ：可查看我們目前有收錄的洗面乳品項https://github.com/tn00627974/Streamlit_app
**4. 我們團隊** ：可查看我們開發團隊的成員以及個人履歷。  



# 版本更新及維護
**版本紀錄** : main_v6版本 (20240509)
- 新增詳細註解內容，使程式碼更好被閱讀
- 更動Flex massge圖像大小 從full > 3xl , 回傳模板時圖像不會過大等問題
- 優化主程式碼雜亂問題,更新原有的code重新移至select_tool_v2建立funtion(load_js3)


## 貢獻指南
歡迎更多的開發者共同參與，對於目前的代碼、運作問題或擴充功能給予建議及說明。

## 致謝
感謝所有使用和支持本項目的人。
特別感謝所有對項目代碼做出貢獻的開發者。

專案PTT預覽 :
https://gamma.app/docs/-nrxnrc44lavx17z?mode=doc
