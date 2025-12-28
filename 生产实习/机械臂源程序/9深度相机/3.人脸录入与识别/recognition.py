import cv2
# 人脸识别
def recognition(mydict):
    print("按'q'退出！")
    mydict = mydict
    recognizer = cv2.face.LBPHFaceRecognizer_create()#LBP识别器
    recognizer.read('trainer/trainer.yml')#读取训练的人脸数据
    cascadePath = "data/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)#加载自带的人脸检测模型
    font = cv2.FONT_HERSHEY_SIMPLEX
    cam = cv2.VideoCapture(2)#打开相机
    ret, image = cam.read()
    if ret != True:
        cam = cv2.VideoCapture(3)
    while True:
        ret, im = cam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)#检测人脸
        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x - 20, y - 20), (x + w + 20, y + h + 20), (0, 255, 0), 4)
            Id, conf = recognizer.predict(gray[y:y + h, x:x + w])#识别人脸
            if conf < 80:#大于80则认为差别大
                if str(Id) in mydict:
                    Id = mydict[str(Id)]
            else:
                Id = "Unknow"
            cv2.rectangle(im, (x - 22, y - 90), (x + w + 22, y - 22), (0, 255, 0), -1)
            cv2.putText(im, str(Id), (x, y - 40), font, 2, (255, 255, 255), 3)
        cv2.imshow('im', im)
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()
