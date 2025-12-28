import cv2
import glob
import numpy as np
def main():
    j = 0  # 对识别出信息的图片计数
    save_path = r'pic/'
    # 实例化
    detect_obj = cv2.QRCodeDetector()
    # 获取固定路径下的所有jpg格式图片
    path = glob.glob(r"pic/*.jpg")
    for i in range(len(path)):
        # 加载图片
        if i < len(path):
            img = cv2.imread(path[i])
            # QR检测和解析
            qr_info, points, qr_img = detect_obj.detectAndDecode(img)
            # 打印图片路径
            print(path[i])
            # 打印解码信息
            print('qr_info:', qr_info)
            if qr_info != "":
                j = j + 1
                # 可视化检测效果，绘制其外接矩形
                cv2.drawContours(img, [np.int32(points)], 0, (0, 0, 255), 2)
                # 批量保存检测出来并绘制外接矩形的图片
                cv2.imwrite(save_path + "result_"+str(i) + '.jpg', img)
                cv2.imshow("result", img)
                cv2.waitKey(0)
if __name__ == "__main__":
    main()