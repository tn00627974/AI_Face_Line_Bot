
# AI_model_deploy (佈署至GCP取得模型API)

此檔案放置在~~gcp-deploy~~的專案下 ,已移至tn00627973 的gcp-deploy

# 首先先將h5模型轉檔

```
import tensorflow as tf
model = tf.keras.models.load_model('MobileNetV2_0212_09轉_standard.h5')
# '1' = 資料夾名稱
model.save('mb2',save_format='tf')
```


- GCP Artifact Registry 
- 建立docker資料夾mb2 , 區域選 愛荷華州

![image](https://github.com/tn00627974/Ai_Face_Linebot/assets/139155210/add91f49-24c4-4c2a-bfda-0a49b0d1f040)


- 在Cloud shell上傳轉好檔的mb2檔案 > 選資料夾上傳與Dockerfile >選檔案上傳 

```dockerfile
FROM tensorflow/serving:2.12.1
COPY mb2/ /models/mobilenetv2/1
ENTRYPOINT tensorflow_model_server --rest_api_port=$PORT --model_name=mobilenetv2 --model_base_path=/models/mobilenetv2
```

# 根據您提供的 Dockerfile，您的 Docker 映像檔將基於 TensorFlow Serving 的 `2.12.1` 版本。該 Dockerfile 包含了三個主要步驟：

1. `FROM tensorflow/serving:2.12.1`：這個指令從 TensorFlow Serving 的官方 Docker 映像檔開始，使用版本為 `2.12.1`。
    
2. `COPY mb2/ /models/mobilenetv2/1`：這個指令將本機文件系統中 `mb2/` 目錄下的文件複製到容器中的 `/models/mobilenetv2/1` 目錄中。這樣做是為了將模型文件複製到 TensorFlow Serving 預期的模型目錄中。
    
3. `ENTRYPOINT tensorflow_model_server --rest_api_port=$PORT --model_name=mobilenetv2 --model_base_path=/models/mobilenetv2`：這個指令設置了容器的入口點（entry point），即在容器啟動時要運行的命令。在這個例子中，它啟動了 TensorFlow Model Server，並指定了 REST API 的端口號、模型名稱以及模型的基本路徑。

接著在Cloud Shell
```CloudShell
#查看當前目錄
ls
```

![image](https://github.com/tn00627974/Ai_Face_Linebot/assets/139155210/13643b9a-3690-4151-a7ac-db31f7fdfb15)


用Dokcer build mb2資料夾 產生image檔
```CloudShell
docker build -t us-central1-docker.pkg.dev/hybrid-circle-411606/mb2/mobilenetv2:v1 .
```

- 用Docker 推上資料夾

```CloudShell
docker push us-central1-docker.pkg.dev/hybrid-circle-411606/mb2/mobilenetv2:v1
```

- 按授權
![image](https://github.com/tn00627974/Ai_Face_Linebot/assets/139155210/d4e24752-d855-4221-97aa-4c1cd5124c2d)


- 回到Artface Registry將push好的模型佈署到Cloud Run
![image](https://github.com/tn00627974/Ai_Face_Linebot/assets/139155210/2e0a913c-13d2-433a-8f8c-6a720c5d78ad)



# Cloud Run > 建立服務 >容器映像檔網址
![image](https://github.com/tn00627974/Ai_Face_Linebot/assets/139155210/b54ef4ec-380a-4331-8a47-a06e375087e8)


執行個體數項下限選0 or 1
0 = 冷啟動 (當沒使用時會關閉)
1 = 隨時保持1個待命 , 啟動時較快 (費用會增加)

![image](https://github.com/tn00627974/Ai_Face_Linebot/assets/139155210/c66a3ad3-08ea-4f49-b3f6-790aafbbfadc)


![image](https://github.com/tn00627974/Ai_Face_Linebot/assets/139155210/3a0489c8-7466-488b-9fb8-1894fd325987)


# 測試模組API運行程式碼
```python
import cv2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
img = Image.open('222.jpg')
width, height = img.size

# 转换为numpy数组进行处理
img_np = np.array(img)

# 检查高度和宽度，进行填充
if height > width:
    diff = height - width
    left = diff // 2
    right = diff - left
    padding = ((0, 0), (left, right), (0, 0))
elif width > height:
    diff = width - height
    top = diff // 2
    bottom = diff - top
    padding = ((top, bottom), (0, 0), (0, 0))
else:
    padding = ((0, 0), (0, 0), (0, 0))

padded_image = np.pad(img_np, padding, mode="constant", constant_values=0)

# 调整大小
resized_image = cv2.resize(padded_image, (224, 224))

# img_array = np.array(img)
img_array = np.expand_dims(resized_image, axis=0)  # 创建一个 batch
img_array = preprocess_input(img_array)  # 应用预处理

# 预测
img_array = img_array.astype(np.float32)

r = requests.post(
    "https://mb2-ainhv2l3eq-uc.a.run.app:443/v1/models/mobilenetv2:predict",
    json={"instances": img_array.tolist()},
)
print(r.content)
predicted_class = np.argmax(r.json()["predictions"][0])
print(predicted_class)
```


us-central1-docker.pkg.dev/linebot-deploy/mb2/mobilenetv2@sha256:bfa2ee17364feeec704068e7889680c0e6c817c4fdba1a84bf67dd2fd4b5bfba

# 如沒有問題就可以串接在LINEBOT程式碼內囉!
