import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import csv
import os
import jieba
import mysql.connector
import json
from openai import OpenAI
from datetime import datetime
from gensim.models.word2vec import LineSentence
from gensim.models import Word2Vec
from gensim.utils import simple_preprocess
from gensim.models import KeyedVectors
import pandas as pd
import jieba.posseg as pseg
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from opencc import OpenCC

with open("config.json") as f:
    config = json.load(f)
cnx = mysql.connector.connect(  ##要改
    user=config["user"],
    password=config["password"],
    host=config["host"],
    port=config["port"],
    database="face_input",
    charset="utf8mb4",
)
# 確保替換為你的資料庫訊息

# 使用連接進行操作
cursor = cnx.cursor()

item_dict = {
    0: "超綿感泡泡保濕洗面乳",
    1: "青柚籽深層潔顏乳",
    2: "卵肌溫和去角質洗面乳",
    3: "極潤健康深層清潔調理洗面乳",
    4: "極潤保濕洗面乳",
    5: "豆乳美肌洗面乳",
    6: "草本調理淨化洗顏乳",
    7: "溫和保濕潔顏乳",
    8: "超微米胺基酸溫和潔顏慕絲",
    9: "淨白洗面乳",
    10: "溫和水嫩洗面乳",
    11: "透白勻亮洗面乳",
    12: "碧菲絲特毛孔淨透洗面乳",
    13: "清透極淨洗面乳",
    14: "海泥毛孔潔淨洗顏乳",
    15: "碧菲絲特抗暗沉碳酸泡洗顏",
    16: "碧菲絲特清爽碳酸泡洗顏",
    17: "碧菲絲特保濕碳酸泡洗顏",
}


def get_stock(url, item_name, item_index):
    # 定義網頁請求的標頭
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # 創建空的DataFrame
    data = pd.DataFrame(
        columns=["ID", "膚質", "年齡", "評分", "效果", "評論內容", "UID", "DATE"]
    )

    # 用requests和BeautifulSoup獲取網頁資訊
    res = requests.get(url, headers=HEADERS) 
    soup = BeautifulSoup(res.text, "html.parser")

    # 獲取特定的元素
    ts3 = soup.find_all("div", class_="author-review-status")  # 膚質+年紀
    ts4 = soup.find_all("div", class_="review-score")  # 分數
    url2 = soup.find_all("a", class_="review-content-top")  # 評論的網頁

    # 初始化一些變數和數據結構
    items = []
    skins = []
    ages = []
    source = []
    comments = []
    effects = []
    url2s = []
    existing_urls = set() # set() = 集合，用來存放已存在的URL

    # 從數據庫中獲取已存在的URL，以防重複爬取
    cursor.execute(f"select UID from items_comment")
    rows = cursor.fetchall() # 獲取已存在的URL
    existing_urls = {row[-1] for row in rows} # 轉換為集合

    # 遍歷獲取到的元素
    page = 1
    for i, i3, i4 in zip(url2, ts3, ts4):
        # 如果評論不符合條件，則跳過
        if (
            i4.text == "(淺層體驗)"
            or int(re.findall("\d+", i3.text.split("・")[1])[0]) > 70
        ):
            print("格式錯誤")
            continue
        # 如果評論已存在於CSV，則跳過
        if i.get("href") in existing_urls:
            print("pass")
            continue
        else:
            # 爬取評論頁面的信息
            res2 = requests.get("https://cosme.net.tw" + i.get("href"), headers=HEADERS)
            url2s.append(i.get("href"))
            soup2 = BeautifulSoup(res2.text, "html.parser") # 評論頁面
            ts5 = soup2.find("div", class_="review-content")  # 評論
            ts6 = ts5.find("div", class_="review-attributes") # 效果
            effect = ts6.extract().text # 效果
            effects.append(effect.split("・")[1]) 

            comment = ts5.text.replace(" ", "")
            print(f"comment{page}")
            page += 1
            comments.append(comment)

            items.append((item_index))

            # 獲取膚質和年齡信息
            skinage = str(i3.text)
            skins.append(skinage.split("・")[0])
            ages.append(int(re.findall("\d+", skinage.split("・")[1])[0]))
            source.append(int(i4.text))

    # 將爬取的數據儲存到DataFrame中
    for i in range(len(items)):
        date = datetime.now().date()
        data.loc[i] = [
            items[i],
            skins[i],
            ages[i],
            source[i],
            effects[i],
            comments[i],
            url2s[i],
            date,
        ]

    # 檢查是否還有下一頁，如果有，返回下一頁的URL和數據DataFrame
    if soup.find("a", class_="next_page") is not None:
        ts6 = soup.find("a", class_="next_page").get("href")  # 下一頁連結
        return "https://cosme.net.tw" + ts6, data
    else:
        print("none")
        return None, data


# 分詞
def jieba_word(effect):
    # 載入自定義辭典
    jieba.load_userdict("effect.txt")
    word_list = []

    # 分詞並過濾停止詞
    for line in effect:
        keywords = jieba.cut(line)
        for word in keywords:
            word_list.append(word)

    # 讀取停止詞文件
    with open("stopword.txt", "r", encoding="utf-8") as f:
        stop_word_list = [rep.replace("\n", "") for rep in f.readlines()]

    # 過濾分詞並統計詞頻
    word_cut_list = [
        word for word in word_list if len(word) > 1 and word not in stop_word_list
    ]
    count = {}
    for w in word_cut_list:
        if w not in count:
            count[w] = 1
        else:
            count[w] += 1

    # 取詞頻前三的效果詞
    sorted_dict = [
        item[0]
        for item in sorted(count.items(), key=lambda item: item[1], reverse=True)[:3]
    ]
    if len(sorted_dict) < 3:
        return None, None, None
    else:
        return sorted_dict[0], sorted_dict[1], sorted_dict[2]


# 平均
def source_mean(source):
    average = round(source.mean(), 1)
    return average


# 根據條件從數據庫中獲取資料並計算平均分數和頂部詞
def a1(id, age, skin):
    # 根據ID、年齡、膚質從數據庫中獲取資料
    sql = "select 評分,效果 from items_comment WHERE ID=%s and 年齡<=%s and 膚質=%s"
    cursor.execute(sql, (id, age, skin))
    rows = cursor.fetchall()
    a1 = pd.DataFrame(rows, columns=["評分", "效果"])
    return a1


# 根據條件從數據庫中獲取資料並計算平均分數和頂部詞
def a2(id, agemin, agemax, skin):
    # 根據ID、年齡區間、膚質從數據庫中獲取資料
    sql = "select 評分,效果 from items_comment WHERE ID=%s and (年齡>%s and 年齡<%s) and 膚質=%s"
    cursor.execute(sql, (id, agemin, agemax, skin))
    rows = cursor.fetchall()
    a2 = pd.DataFrame(rows, columns=["評分", "效果"])
    return a2


# 根據條件從數據庫中獲取資料並計算平均分數和頂部詞
def a3(id, age, skin):
    # 根據ID、年齡、膚質從數據庫中獲取資料
    sql = "select 評分,效果 from items_comment WHERE ID=%s and 年齡>%s and 膚質=%s"
    cursor.execute(sql, (id, age, skin))
    rows = cursor.fetchall()
    a3 = pd.DataFrame(rows, columns=["評分", "效果"])
    return a3


# 從DataFrame中提取平均分數和頂部詞
def extract_info(df):
    if df.empty:
        return None, None

    # 計算平均分數和頂部詞
    average = source_mean(df["評分"])
    top_effects = jieba_word(df["效果"])
    top = None
    if top_effects[0] is not None:
        top = "、".join(top_effects[:3])

    return average, top


# 根據不同條件從數據庫中獲取資料並計算平均分數和頂部詞
def ageskinall(skin):
    results = []

    # 定義不同條件
    conditions = [
        (a1, num, 20, skin),
        (a2, num, 20, 35, skin),
        (a2, num, 35, 45, skin),
        (a3, num, 45, skin)
    ]

    # 遍歷不同條件並計算平均分數和頂部詞
    for func, *args in conditions:
        df = func(*args)
        average, top = extract_info(df)
        results.extend([average, top])

    return tuple(results)
# 從數據庫中獲取資料並計算平均分數和頂部詞
table1_data = pd.DataFrame(
    columns=[
        "ID",
        "簡稱",
        "平均分數",
        "效果",
        "A1分數",
        "A1效果",
        "A2分數",
        "A2效果",
        "A3分數",
        "A3效果",
        "A4分數",
        "A4效果",
        "B1分數",
        "B1效果",
        "B2分數",
        "B2效果",
        "B3分數",
        "B3效果",
        "B4分數",
        "B4效果",
        "C1分數",
        "C1效果",
        "C2分數",
        "C2效果",
        "C3分數",
        "C3效果",
        "C4分數",
        "C4效果",
        "D1分數",
        "D1效果",
        "D2分數",
        "D2效果",
        "D3分數",
        "D3效果",
        "D4分數",
        "D4效果",
        "缺點",
        "優點",
    ]
)
datas = pd.DataFrame(columns=["ID", "膚質", "年齡", "評分", "效果", "評論內容", "UID"])

# 定義網頁URL
url = config["url"] 
cursor = cnx.cursor() 
word2vectf = list() 
for num, u in enumerate(url, start=0): 
    while True:
        next_page, data = get_stock(u, item_dict[num], num)
        datas = pd.concat([datas, data])

        if next_page == None:
            break
        else:
            u = next_page

    for index, row in datas.iterrows(): # 遍歷每一筆資料 iterrows() 會回傳 index, row
        
        insert_query = f"INSERT INTO items_comment (ID,膚質,年齡,評分,效果,評論內容,UID,DATE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(
            insert_query,
            (
                row["ID"],
                row["膚質"],
                row["年齡"],
                row["評分"],
                row["效果"],
                row["評論內容"],
                row["UID"],
                row["DATE"],
            ),
        )
        cnx.commit()
        
    datas = pd.DataFrame(columns=datas.columns) # datas 清空 

    cursor.execute(f"select DATE from items_comment WHERE ID={num}")
    rows = cursor.fetchall() # 獲取已存在的日期
    existing_date = {row[0].strftime("%Y-%m-%d") for row in rows} # 轉換為集合
    today = str(datetime.now().date()) # 今天日期
    
    # 計算平均分數和頂部詞
    if today in existing_date: 
        cursor.execute(f"select 評分,效果 from items_comment WHERE ID={num}")
        rows = cursor.fetchall()
        effect = pd.DataFrame(rows, columns=["評分", "效果"])

        top1, top2, top3 = jieba_word(effect["效果"])
        top = f"{top1}、{top2}、{top3}"
        average = source_mean(effect["評分"])

        dry = ageskinall("乾性肌膚") 
        oil = ageskinall("油性肌膚")
        sen = ageskinall("敏感性肌膚")
        mix = ageskinall("混合性肌膚")

        client = OpenAI(api_key=config["api_key"])  # 要改

        cursor.execute(f"select 評論內容 from items_comment where ID={num}")
        t = cursor.fetchall()

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": f"""{t[-30:]}是一個品項洗面乳的評論幫我依照json格式產出一個缺點以及一個優點不要使用原本的評論內容
                請按照我以下範例格式回傳
                '{'缺點:繁體中文的內容,優點:繁體中文的內容'}'""",
                },
            ],
        )
        cc = OpenCC("s2t") 
        print(response.choices[0].message.content)
        gdbd = json.loads(response.choices[0].message.content)
        gdbd["缺點"] = cc.convert(gdbd["缺點"])
        gdbd["優點"] = cc.convert(gdbd["優點"])
        table1_data.loc[num] = [
            num,
            item_dict[num],
            average,
            top,
            dry[0],
            dry[1],
            dry[2],
            dry[3],
            dry[4],
            dry[5],
            dry[6],
            dry[7],
            oil[0],
            oil[1],
            oil[2],
            oil[3],
            oil[4],
            oil[5],
            oil[6],
            oil[7],
            sen[0],
            sen[1],
            sen[2],
            sen[3],
            sen[4],
            sen[5],
            sen[6],
            sen[7],
            mix[0],
            mix[1],
            mix[2],
            mix[3],
            mix[4],
            mix[5],
            mix[6],
            mix[7],
            gdbd["缺點"],
            gdbd["優點"],
        ]
        print(table1_data.loc[num])
        cursor.execute(f"select * from items_table WHERE ID={num}") # 獲取已存在的資料
        rows = cursor.fetchall() 
        sql_data = pd.DataFrame(rows)
        # print(type(table1_data.loc[num]),table1_data.loc[num])
        for index, row in table1_data.iterrows():
            if num == index:
                break

        if sql_data.empty: # 資料庫中沒有該ID的資料
            print(
                row["ID"],
                row["簡稱"],
                row["平均分數"],
                row["效果"],
                row["A1分數"],
                row["A1效果"],
                row["A2分數"],
                row["A2效果"],
                row["A3分數"],
                row["A3效果"],
                row["A4分數"],
                row["A4效果"],
                row["B1分數"],
                row["B1效果"],
                row["B2分數"],
                row["B2效果"],
                row["B3分數"],
                row["B3效果"],
                row["B4分數"],
                row["B4效果"],
                row["C1分數"],
                row["C1效果"],
                row["C2分數"],
                row["C2效果"],
                row["C3分數"],
                row["C3效果"],
                row["C4分數"],
                row["C4效果"],
                row["D1分數"],
                row["D1效果"],
                row["D2分數"],
                row["D2效果"],
                row["D3分數"],
                row["D3效果"],
                row["D4分數"],
                row["D4效果"],
                row["缺點"],
                row["優點"],
            )
            insert_query = """INSERT INTO items_table (ID,簡稱,平均分數,效果,
                            A1分數,A1效果,A2分數,A2效果,A3分數,A3效果,A4分數,A4效果,
                            B1分數,B1效果,B2分數,B2效果,B3分數,B3效果,B4分數,B4效果,
                            C1分數,C1效果,C2分數,C2效果,C3分數,C3效果,C4分數,C4效果,
                            D1分數,D1效果,D2分數,D2效果,D3分數,D3效果,D4分數,D4效果,
                            缺點,優點) 
                            VALUES (%s, %s, %s, %s,
                            %s,%s,%s,%s,%s,%s,%s,%s,
                            %s,%s,%s,%s,%s,%s,%s,%s,
                            %s,%s,%s,%s,%s,%s,%s,%s,
                            %s,%s,%s,%s,%s,%s,%s,%s,
                            %s,%s)"""
            cursor.execute(
                insert_query,
                (
                    row["ID"],
                    row["簡稱"],
                    row["平均分數"],
                    row["效果"],
                    row["A1分數"],
                    row["A1效果"],
                    row["A2分數"],
                    row["A2效果"],
                    row["A3分數"],
                    row["A3效果"],
                    row["A4分數"],
                    row["A4效果"],
                    row["B1分數"],
                    row["B1效果"],
                    row["B2分數"],
                    row["B2效果"],
                    row["B3分數"],
                    row["B3效果"],
                    row["B4分數"],
                    row["B4效果"],
                    row["C1分數"],
                    row["C1效果"],
                    row["C2分數"],
                    row["C2效果"],
                    row["C3分數"],
                    row["C3效果"],
                    row["C4分數"],
                    row["C4效果"],
                    row["D1分數"],
                    row["D1效果"],
                    row["D2分數"],
                    row["D2效果"],
                    row["D3分數"],
                    row["D3效果"],
                    row["D4分數"],
                    row["D4效果"],
                    row["缺點"],
                    row["優點"],
                ),
            )

        else:

            update_query = """UPDATE items_table SET 簡稱 = %s, 平均分數 = %s, 效果 = %s, 
                A1分數 = %s, A1效果 = %s,A2分數 = %s, A2效果 = %s,A3分數 = %s, A3效果 = %s,A4分數 = %s, A4效果 = %s,
                B1分數 = %s, B1效果 = %s,B2分數 = %s, B2效果 = %s,B3分數 = %s, B3效果 = %s,B4分數 = %s, B4效果 = %s,
                C1分數 = %s, C1效果 = %s,C2分數 = %s, C2效果 = %s,C3分數 = %s, C3效果 = %s,C4分數 = %s, C4效果 = %s,
                D1分數 = %s, D1效果 = %s,D2分數 = %s, D2效果 = %s,D3分數 = %s, D3效果 = %s,D4分數 = %s, D4效果 = %s, 
                缺點 = %s,優點 = %s   WHERE ID = %s"""
            cursor.execute(
                update_query,
                (
                    row["簡稱"],
                    row["平均分數"],
                    row["效果"],
                    row["A1分數"],
                    row["A1效果"],
                    row["A2分數"],
                    row["A2效果"],
                    row["A3分數"],
                    row["A3效果"],
                    row["A4分數"],
                    row["A4效果"],
                    row["B1分數"],
                    row["B1效果"],
                    row["B2分數"],
                    row["B2效果"],
                    row["B3分數"],
                    row["B3效果"],
                    row["B4分數"],
                    row["B4效果"],
                    row["C1分數"],
                    row["C1效果"],
                    row["C2分數"],
                    row["C2效果"],
                    row["C3分數"],
                    row["C3效果"],
                    row["C4分數"],
                    row["C4效果"],
                    row["D1分數"],
                    row["D1效果"],
                    row["D2分數"],
                    row["D2效果"],
                    row["D3分數"],
                    row["D3效果"],
                    row["D4分數"],
                    row["D4效果"],
                    row["缺點"],
                    row["優點"],
                    row["ID"],
                ),
            )

        cnx.commit()
        print("update successful")
        word2vectf.append(1)

    else:
        print("no new data")
if 1 in word2vectf:
    b = []
    item_mapping = {
        0: "超綿感泡泡保濕洗面乳",
        1: "青柚籽深層潔顏乳",
        2: "卵肌溫和去角質洗面乳",
        3: "極潤健康深層清潔調理洗面乳",
        4: "極潤保濕洗面乳",
        5: "豆乳美肌洗面乳",
        6: "草本調理淨化洗顏乳",
        7: "溫和保濕潔顏乳",
        8: "超微米胺基酸溫和潔顏慕絲",
        9: "淨白洗面乳",
        10: "溫和水嫩洗面乳",
        11: "透白勻亮洗面乳",
        12: "碧菲絲特毛孔淨透洗面乳",
        13: "清透極淨洗面乳",
        14: "海泥毛孔潔淨洗顏乳",
        15: "碧菲絲特抗暗沉碳酸泡洗顏",
        16: "碧菲絲特清爽碳酸泡洗顏",
        17: "碧菲絲特保濕碳酸泡洗顏",
    }
    # 產品名稱、缺點、優點、評論內容
    for i in range(len(item_mapping)):
        a = "" # "" 為缺點，優點內容
        c = "" # "" 為評論內容
        cursor.execute(f"SELECT 效果,優點,缺點 FROM items_table WHERE id={i}")
        items = cursor.fetchall()
        cursor.execute(f"SELECT 評論內容 FROM items_comment WHERE id={i}")
        items_comments = cursor.fetchall()
        # items_comments
        for it in items:
            a += " ".join(map(str, it)) + " "

            for comment in items_comments:
                c += " ".join(map(str, comment))

        item_str = item_mapping.get(i)
        b.append(item_str + " " + a + c)
        # print(b)
    sentences = []
    jieba.set_dictionary("dict.txt.big")
    jieba.load_userdict("word.txt")
    for line in b:  # 假設 data 是您提供的產品和評論列表
    # 使用 jieba 分词
        words = list(simple_preprocess(line))
        sentences.append(words)
    with open("stop_words.txt", "r", encoding="utf-8") as f:
        stop_word_list = [rep.replace("\n", "") for rep in f.readlines()] # 停用詞列表
    # 去除停用詞
    word_cut_list = [
        [word for word in words if len(word) > 1 and word not in stop_word_list]
        for words in sentences
    ]
    # 訓練 Word2Vec 模型
    model = Word2Vec(
        word_cut_list, vector_size=100, window=10, min_count=1, workers=4, sg=1
    )

    # 生成產品向量
    product_vectors = {}
    for words in word_cut_list:
        # 通過平均詞向量獲得產品向量
        vector = sum(model.wv[word] for word in words if word in model.wv) / len(words)
        product_vectors[words[0]] = vector  # 假設每段的第一個詞是產品名稱

    vectors = np.array(list(product_vectors.values()))

    # 計算所有產品之間的相似度
    similarity_matrix = cosine_similarity(vectors)

    # # # 選擇商品推薦
    # # product_index = 0

    # 計算指定產品與所有其他產品的相似度
    similarities = similarity_matrix
    for count in range(len(similarities)):

        item_similarities = similarity_matrix[count]

        # 對相似度進行排序並獲取最相似的產品索引
        most_similar = item_similarities.argsort()[-4:-1]  # 取最相似，排除自身

        # 給出推薦的產品
        recommended_product = [
            list(product_vectors.keys())[i] for i in most_similar[-3:]
        ]
        print(recommended_product)
        # 將推薦的產品寫入資料庫
        update_query = (
            "update items_table set 推薦1=%s ,推薦2=%s ,推薦3=%s where id=%s "
        )
        # 假設 count 是商品索引 找出最相似的商品索引
        # 假設 recommended_product 是推薦商品名稱
        cursor.execute(
            update_query,
            (
                recommended_product[0],
                recommended_product[1],
                recommended_product[2],
                count,
            ),
        )
        cnx.commit()
cursor.close()
cnx.close()
