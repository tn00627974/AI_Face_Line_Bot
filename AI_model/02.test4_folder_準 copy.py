import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import numpy as np

import os

# 載入模型

# NB2 = 'path\MobileNetV2_0205_04_seq.h5'
loaded_model = tf.keras.models.load_model("MobileNetV2_0212_09轉_standard.h5")


# 測試集資料生成器
test_datagen = ImageDataGenerator(rescale=1.0 / 255)
test_generator = test_datagen.flow_from_directory(
    "F:\工程師資料夾\MobileNetV3Large_K專用訓練",  # 測試集數據的路徑
#     # target_size=(224, 224),
#     # batch_size=32,
#     # class_mode='categorical',
#     # shuffle=False  # 在測試時通常不需要打亂數據
)
# print(test_generator)


# def flow_from_directory(
#     self,
#     directory,               # 字符串，目標目錄的路徑。該目錄應包含一個子目錄，每個子目錄都包含一個特定類別的圖片。
#     target_size=(256, 256),   # 二元組，指定輸出圖片的高度和寬度。
#     color_mode='rgb',         # "grayscale"、"rgb" 或 "rgba" 之一。指定輸出圖片的顏色模式。
#     classes=None,             # 可選參數。一個可選的類別列表，用於指定順序的類別子集（默認為目錄名稱列表）。
#     class_mode='categorical', # "categorical", "binary", "sparse" 或 None 之一。控制返回標籤的類型。
#     batch_size=32,            # 一批生成的樣本數。
#     shuffle=True,             # 是否打亂數據。
#     seed=None,                # 可選參數，用於隨機數生成的種子。
#     save_to_dir=None,         # None 或 字符串，保存生成的增強圖片的目錄（用於檢查數據增強效果）。
#     save_prefix='',           # 字符串，保存生成的增強圖片時使用的文件名前綴。
#     save_format='png',        # "png" 或 "jpeg" 之一。保存生成的增強圖片的文件格式。
#     follow_links=False,       # 是否跟隨符號鏈接。
#     subset=None,              # 如果 `directory` 包含子目錄（被 `classes` 參數指定），則可選的子集（"training" 或 "validation"）。
#     interpolation='nearest'   # 在縮放時使用的插值方法。
# ):

# 獲取類別標籤和索引的對應
# class_labels ={'01.FOAM0119': 0, '02.上山採藥0119': 1, '03.卵肌0119': 2, '04.極潤(綠)0119': 3, '05.極潤(藍)0119': 4, '06.豆乳0129': 5, '07草本ロゼット-0129': 6, '08.Simple綠-0129': 7, '09.Perfect whip超微米-0129': 8, '10.雪肌粹-0129': 9, '11Biore溫和水嫩-0129': 10, '12.Biore透白勻亮-0130': 11, '13.Bifesta 碧菲絲': 12, '14.Biore 清透極淨-0129': 13}
class_labels = test_generator.class_indices
print("Class labels and corresponding indices:", class_labels)
# for key in class_labels :
#     print(key)

# Folder path containing multiple images
folder_path = "無黑邊"

# Get a list of all image files in the folder
image_files = [
    f
    for f in os.listdir(folder_path)
    if os.path.isfile(os.path.join(folder_path, f))
    and f.lower().endswith((".png", ".jpg", ".jpeg"))
]

# Loop through each image in the folder
for image_file in image_files:
    # Construct the full path to the image
    image_path = os.path.join(folder_path, image_file)

    # Load and preprocess the image
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    # print(img_array)
    # img_array = preprocess_input(img_array)
    # print(img_array)
    # img_array =(img_array/127.5) - 1
    # print("==============================",img_array)


    # Perform model inference
    preds = loaded_model.predict(img_array)

    # Find the index of the predicted class with the highest probability
    predicted_class_index = np.argmax(preds)

    # Convert to the predicted class name
    predicted_label = [
        k for k, v in class_labels.items() if v == predicted_class_index
    ][0]

    # Print the prediction result for each image
    # if  image_file == predicted_label :
    #     print(f"{image_file},{predicted_label},{preds[0][predicted_class_index]:.2f}","正確")
    # else :
    #     print(f"{image_file},{predicted_label},{preds[0][predicted_class_index]:.2f}","錯誤")
            
    print(
        f"Image: {image_file}, Predicted class: {predicted_label}, Probability: {preds[0][predicted_class_index]:.2f}"
    )

