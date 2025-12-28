import os
import cv2
import numpy as np
from PIL import Image

path = r'./trainer'#保存训练数据的路径
# 人脸数据训练
def training():
    recognizer = cv2.face.LBPHFaceRecognizer_create()#LBP识别器
    detector = cv2.CascadeClassifier("data/haarcascade_frontalface_default.xml")
    #获取图片和标签
    def getImagesAndLabels(path):
        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
        faceSamples = []
        ids = []
        for imagePath in imagePaths:
            PIL_img = Image.open(imagePath).convert('L')
            img_numpy = np.array(PIL_img, 'uint8')
            id = int(os.path.split(imagePath)[-1].split(".")[1])
            # print(id)
            faces = detector.detectMultiScale(img_numpy)
            for (x, y, w, h) in faces:
                faceSamples.append(img_numpy[y:y + h, x:x + w])
                ids.append(id)
        return faceSamples, ids
    faces, ids = getImagesAndLabels('./dataset')
    recognizer.train(faces, np.array(ids))#训练人脸
    recognizer.save('trainer/trainer.yml')#保存训练好的人脸数据
    print("数据训练完毕！")
