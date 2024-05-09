from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    ImageMessage,
    TextSendMessage,
    TextMessage,
    MessageAction,
    FlexSendMessage,
    QuickReplyButton,
    QuickReply,
    CameraAction,
    CameraRollAction,
)
from io import BytesIO
from PIL import Image
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import re, json, configparser, requests, cv2, os
from select_tool_v2 import select_1, select_2, load_js1, load_js2, push_db # 載入資料庫函式工具


app = Flask(__name__, static_url_path="/img", static_folder="images")

config = configparser.ConfigParser()
config.read("config.ini")

line_bot_api = LineBotApi(config.get("line-bot", "channel_access_token"))
handler = WebhookHandler(config.get("line-bot", "channel_secret"))


# 在路由"/"設置回撥函數，該函數處理接收到的POST請求
@app.route("/", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]  # 從請求頭部獲取簽名信息
    body = request.get_data(as_text=True)  # 獲取請求主體內容，以文本形式返回
    try:
        handler.handle(body, signature)  # 呼叫handler處理請求內容和簽名
    except InvalidSignatureError: 
        abort(400)  # 中止請求並返回狀態碼400
    return "OK"  # 返回狀態碼200，表示處理成功

# 拍照辨識功能 : 1.拍照 2.上傳照片
@handler.add(MessageEvent, message=(TextMessage, ImageMessage))
def handle_message(event):
    global product_data, skin_os, age_os # 全局變數

    if isinstance(event.message, ImageMessage):
        # 获取图片内容
        message_content = line_bot_api.get_message_content(event.message.id)
        image_bytes = BytesIO(message_content.content)

        # 使用 PIL.Image 打开图片
        img = Image.open(image_bytes)
        width, height = img.size

        # 转换为numpy数组进行处理
        img_np = np.array(img)

        # 填充黑邊功能 : 根據圖像的高度和寬度進行填充，使其成為正方形
        if height > width:
            diff = height - width
            left = diff // 2
            right = diff - left
            padding = ((0, 0), (left, right), (0, 0)) # 左右填充
        elif width > height:
            diff = width - height 
            top = diff // 2
            bottom = diff - top
            padding = ((top, bottom), (0, 0), (0, 0)) # 上下填充
        else:
            padding = ((0, 0), (0, 0), (0, 0)) # 不需填充,是正方形

        # 將圖像進行黑邊填充
        padded_image = np.pad(img_np, padding, mode="constant", constant_values=0)

        # 调整大小
        resized_image = cv2.resize(padded_image, (224, 224))

        # img_array = np.array(img)
        img_array = np.expand_dims(resized_image, axis=0)  # 创建一个 batch
        img_array = preprocess_input(img_array)  # 应用预处理

        # 预测
        img_array = img_array.astype(np.float32)
        # img_array = img_array.reshape(1, *img_array.shape)
        r = requests.post(
            "https://mobilenetv2-tbhf33veoq-uc.a.run.app/v1/models/mobilenetv2:predict",
            json={"instances": img_array.tolist()},
        )# 請求模型預測
        print(r.text)
        predicted_class = np.argmax(r.json()["predictions"][0])

        # 使用预测结果生成回复消息
        product_id = predicted_class  # 商品編號
        product_data = select_1(product_id)  
        # 用Flex模板生成商品資訊
        flex_msg = FlexSendMessage(alt_text="flex_msg", contents=load_js1(product_data)) # 回傳 ID, 簡稱, 平均分數, 效果, 優點, 缺點
        line_bot_api.reply_message(event.reply_token, flex_msg)


    # 推薦商品 
    # 如果收到的訊息是文字訊息
    elif isinstance(event.message, TextMessage):
        # 如果訊息中包含"推薦:"這個字串
        if "推薦:" in event.message.text:
            # 建立產品名稱與編號的字典
            info_dict = {
                "超綿感泡泡保濕洗面乳": 0,
                "青柚籽深層潔顏乳": 1,
                "卵肌溫和去角質洗面乳": 2,
                "極潤健康深層清潔調理洗面乳": 3,
                "極潤保濕洗面乳": 4,
                "豆乳美肌洗面乳": 5,
                "草本調理淨化洗顏乳": 6,
                "溫和保濕潔顏乳": 7,
                "超微米胺基酸溫和潔顏慕絲": 8,
                "淨白洗面乳": 9,
                "溫和水嫩洗面乳": 10,
                "透白勻亮洗面乳": 11,
                "碧菲絲特毛孔淨透洗面乳": 12,
                "清透極淨洗面乳": 13,
                "海泥毛孔潔淨洗顏乳": 14,
                "碧菲絲特抗暗沉碳酸泡洗顏": 15,
                "碧菲絲特清爽碳酸泡洗顏": 16,
                "碧菲絲特保濕碳酸泡洗顏": 17,
            }
            # 取得產品名稱前三個商品訊息
            push_id = info_dict[event.message.text[3:]]
            # 根據產品編號從資料庫中取得相關資訊
            push_info = select_1(push_id)
            # 取得推薦產品相關的三個產品編號
            id_tp = (
                info_dict[push_info[6]],
                info_dict[push_info[7]],
                info_dict[push_info[8]],
            )
            # 根據產品編號從資料庫中取得推薦資料
            push_data = push_db(id_tp)

            # 建立彈性訊息並回覆給使用者
            flex_msg2 = FlexSendMessage(
                alt_text="flex_msg", contents=load_js2(push_data)
            )
            line_bot_api.reply_message(event.reply_token, flex_msg2)

        # 選擇膚質 功能 
        elif event.message.text == "選擇膚質":
            try:
                i = product_data 
                skin = TextSendMessage(
                    text="請選擇膚質!",
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=MessageAction(
                                    label="乾性肌膚", text="A: 乾性肌膚"
                                )
                            ),
                            QuickReplyButton(
                                action=MessageAction(
                                    label="油性肌膚", text="B: 油性肌膚"
                                )
                            ),
                            QuickReplyButton(
                                action=MessageAction(
                                    label="敏感性肌膚", text="C: 敏感性肌膚"
                                )
                            ),
                            QuickReplyButton(
                                action=MessageAction(
                                    label="混合性肌膚", text="D: 混合性肌膚"
                                )
                            ),
                        ]
                    ),
                )
                line_bot_api.reply_message(event.reply_token, skin)
            except NameError:
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text="請上傳照片!!!")
                )
        # 選擇膚質 功能
        elif re.match("[ABCD]", event.message.text[:1]):
            skin_os = event.message.text[:1]
            age = TextSendMessage(
                text="請選擇年紀範圍!",
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="20歲以下", text="1: 20歲以下")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="21-30歲", text="2: 21-30歲")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="31-45歲", text="3: 31-45歲")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="46歲以上", text="4: 46歲以上")
                        ),
                    ]
                ),
            )
            line_bot_api.reply_message(event.reply_token, age)

        elif re.match("[1-4]", event.message.text[:1]):
            age_os = event.message.text[:1]
            age_type = f"{skin_os}{age_os}"
            result = select_2(product_data[0], age_type)
            skin_dict = {
                "A": "乾性肌膚",
                "B": "油性肌膚",
                "C": "敏感性肌膚",
                "D": "混合性肌膚",
            }
            age_dict = {
                "1": "20歲以下",
                "2": "21-30歲",
                "3": "31-45歲",
                "4": "46歲以上",
            }

            with open("v3.json", mode="r", encoding="utf-8") as fi:
                js = json.load(fi)

            js["body"]["contents"][1]["text"] = product_data[1]  # 商品名稱
            js["body"]["contents"][3]["contents"][0]["contents"][1]["text"] = skin_dict[
                skin_os
            ]  # 皮膚屬性
            js["body"]["contents"][3]["contents"][1]["contents"][1]["text"] = age_dict[
                age_os
            ]  # 年紀範圍
            js["body"]["contents"][3]["contents"][3]["contents"][1]["text"] = (
                str(result[0]) if result[0] != None else "無使用者分享"
            )  # 分數
            js["body"]["contents"][3]["contents"][4]["contents"][1]["text"] = (
                result[1] if result[1] != None else "無使用者分享"
            )  # 效果

            flex_msg3 = FlexSendMessage(alt_text="flex_msg", contents=js)

            line_bot_api.reply_message(event.reply_token, flex_msg3)

            skin_os = ""
            age_os = ""
            
        # 拍照辨識 快速回覆按鈕 : 1.拍照 2.上傳照片
        elif event.message.text == "拍照":
            camera_button = QuickReplyButton(action=CameraAction(label="拍照"))
            camera_roll = QuickReplyButton(action=CameraRollAction(label="上傳照片"))
            quick_reply = QuickReply(items=[camera_button, camera_roll])
            message = TextSendMessage(text="請拍照或上傳照片", quick_reply=quick_reply)
            line_bot_api.reply_message(event.reply_token, message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

# if __name__ == "__main__":
#     app.run()
