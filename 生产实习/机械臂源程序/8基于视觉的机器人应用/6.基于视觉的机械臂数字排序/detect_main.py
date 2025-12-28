#!/usr/bin/env python3
import cv2
import numpy as np
import pyrealsense2 as rs

class my_nanodet():
    def __init__(self, input_shape=320, prob_threshold=0.6, iou_threshold=0.6, model_path='./nanodet.onnx', clsname_path='./coco.names'):
        with open(clsname_path, 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')
        self.num_classes = len(self.classes)
        self.strides = (8, 16, 32)
        self.input_shape = (input_shape, input_shape)
        self.reg_max = 7
        self.prob_threshold = prob_threshold
        self.iou_threshold = iou_threshold
        self.project = np.arange(self.reg_max + 1)
        self.mean = np.array([103.53, 116.28, 123.675], dtype=np.float32).reshape(1, 1, 3)
        self.std = np.array([57.375, 57.12, 58.395], dtype=np.float32).reshape(1, 1, 3)
        self.net = cv2.dnn.readNet(model_path)
        self.mlvl_anchors = []
        for i in range(len(self.strides)):
            anchors = self._make_grid((int(self.input_shape[0] / self.strides[i]), int(self.input_shape[1] / self.strides[i])), self.strides[i])
            self.mlvl_anchors.append(anchors)
        print('模型初始化完成！')

    def _make_grid(self, featmap_size, stride):
        feat_h, feat_w = featmap_size
        shift_x = np.arange(0, feat_w) * stride
        shift_y = np.arange(0, feat_h) * stride
        xv, yv = np.meshgrid(shift_x, shift_y)
        xv = xv.flatten()
        yv = yv.flatten()
        cx = xv + 0.5 * (stride-1)
        cy = yv + 0.5 * (stride - 1)
        return np.stack((cx, cy), axis=-1)

    def softmax(self,x, axis=1):
        x_exp = np.exp(x)
        # 如果是列向量，则axis=0
        x_sum = np.sum(x_exp, axis=axis, keepdims=True)
        s = x_exp / x_sum
        return s

    def _normalize(self, img):  
        img = img.astype(np.float32)
        img = (img - self.mean) / self.std
        return img

    def resize_image(self, srcimg, keep_ratio=True):
        top, left, newh, neww = 0, 0, self.input_shape[0], self.input_shape[1]
        if keep_ratio and srcimg.shape[0] != srcimg.shape[1]:
            hw_scale = srcimg.shape[0] / srcimg.shape[1]
            if hw_scale > 1:
                newh, neww = self.input_shape[0], int(self.input_shape[1] / hw_scale)
                img = cv2.resize(srcimg, (neww, newh), interpolation=cv2.INTER_AREA)
                left = int((self.input_shape[1] - neww) * 0.5)
                img = cv2.copyMakeBorder(img, 0, 0, left, self.input_shape[1] - neww - left, cv2.BORDER_CONSTANT,
                                         value=0)  # add border
            else:
                newh, neww = int(self.input_shape[0] * hw_scale), self.input_shape[1]
                img = cv2.resize(srcimg, (neww, newh), interpolation=cv2.INTER_AREA)
                top = int((self.input_shape[0] - newh) * 0.5)
                img = cv2.copyMakeBorder(img, top, self.input_shape[0] - newh - top, 0, 0, cv2.BORDER_CONSTANT, value=0)
        else:
            img = cv2.resize(srcimg, self.input_shape, interpolation=cv2.INTER_AREA)
        return img, newh, neww, top, left

    def detect(self, srcimg):
        img, newh, neww, top, left = self.resize_image(srcimg)
        img = self._normalize(img)
        blob = cv2.dnn.blobFromImage(img)  #将输入图片进行数据处理，符合模型输入的要求
        # 将图像数据加载到网络模型
        self.net.setInput(blob)
        # 模型中进行前向预测，得到输出结果
        outs = self.net.forward(self.net.getUnconnectedOutLayersNames())

        det_bboxes, det_conf, det_classid = self.post_process(outs)
        drawimg = srcimg.copy()
        # cv2.imshow("dr", drawimg)
        ratioh,ratiow = srcimg.shape[0]/newh,srcimg.shape[1]/neww
        for i in range(det_bboxes.shape[0]):
            xmin, ymin, xmax, ymax = max(int((det_bboxes[i,0] - left) * ratiow), 0), max(int((det_bboxes[i,1] - top) * ratioh), 0), min(
                int((det_bboxes[i,2] - left) * ratiow), srcimg.shape[1]), min(int((det_bboxes[i,3] - top) * ratioh), srcimg.shape[0])
        self.drawPred(drawimg, det_classid[i], det_conf[i], xmin, ymin, xmax, ymax)
        # cv2.imshow("dr1", drawimg)
        return drawimg, self.result

    def post_process(self, preds):
        cls_scores, bbox_preds = preds[::2], preds[1::2]
        det_bboxes, det_conf, det_classid = self.get_bboxes_single(cls_scores, bbox_preds, 1, rescale=False)
        return det_bboxes.astype(np.int32), det_conf, det_classid

    def get_bboxes_single(self, cls_scores, bbox_preds, scale_factor, rescale=False):
        mlvl_bboxes = []
        mlvl_scores = []
        for stride, cls_score, bbox_pred, anchors in zip(self.strides, cls_scores, bbox_preds, self.mlvl_anchors):
            if cls_score.ndim==3:
                cls_score = cls_score.squeeze(axis=0)
            if bbox_pred.ndim==3:
                bbox_pred = bbox_pred.squeeze(axis=0)
            bbox_pred = self.softmax(bbox_pred.reshape(-1, self.reg_max + 1), axis=1)
            bbox_pred = np.dot(bbox_pred, self.project).reshape(-1,4)
            bbox_pred *= stride
            nms_pre = 1000
            if nms_pre > 0 and cls_score.shape[0] > nms_pre:
                max_scores = cls_score.max(axis=1)
                topk_inds = max_scores.argsort()[::-1][0:nms_pre]
                anchors = anchors[topk_inds, :]
                bbox_pred = bbox_pred[topk_inds, :]
                cls_score = cls_score[topk_inds, :]
            bboxes = self.distance2bbox(anchors, bbox_pred, max_shape=self.input_shape)
            mlvl_bboxes.append(bboxes)
            mlvl_scores.append(cls_score)

        mlvl_bboxes = np.concatenate(mlvl_bboxes, axis=0)
        if rescale:
            mlvl_bboxes /= scale_factor
        mlvl_scores = np.concatenate(mlvl_scores, axis=0)

        bboxes_wh = mlvl_bboxes.copy()
        bboxes_wh[:, 2:4] = bboxes_wh[:, 2:4] - bboxes_wh[:, 0:2]  ####xywh
        classIds = np.argmax(mlvl_scores, axis=1)
        confidences = np.max(mlvl_scores, axis=1)  ####max_class_confidence

        indices = cv2.dnn.NMSBoxes(bboxes_wh.tolist(), confidences.tolist(), self.prob_threshold, self.iou_threshold)
        if len(indices)>0:
            mlvl_bboxes = mlvl_bboxes[indices[:, 0]]
            confidences = confidences[indices[:, 0]]
            classIds = classIds[indices[:, 0]]
            return mlvl_bboxes, confidences, classIds
        else:
            print('nothing detect')
            return np.array([]), np.array([]), np.array([])

    def distance2bbox(self, points, distance, max_shape=None):
        x1 = points[:, 0] - distance[:, 0]
        y1 = points[:, 1] - distance[:, 1]
        x2 = points[:, 0] + distance[:, 2]
        y2 = points[:, 1] + distance[:, 3]
        if max_shape is not None:
            x1 = np.clip(x1, 0, max_shape[1])
            y1 = np.clip(y1, 0, max_shape[0])
            x2 = np.clip(x2, 0, max_shape[1])
            y2 = np.clip(y2, 0, max_shape[0])
        return np.stack([x1, y1, x2, y2], axis=-1)

#画框
    def drawPred(self, frame, classId, conf, left, top, right, bottom):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), thickness=4)
        center_x = int(left + right) / 2
        center_y = int(top + bottom) / 2
        self.center = [center_x, center_y]
        label = '%.2f' % conf
        label = '%s:%s' % (self.classes[classId], label)
        print('检测结果为：', self.classes[classId], conf)
        # 在图像的顶点处显示检测结果
        self.result = [center_x, center_y, self.classes[classId]]
        labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        top = max(top, labelSize[1])
        cv2.putText(frame, "number:" + str(self.classes[classId]), (10, 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
        cv2.putText(frame, "conf:" + str(conf), (10, 40), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255),
                    1)

        cv2.putText(frame, "center:" + "(" + str(center_x) + "," + str(center_y) + ")", (10, 60),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
        cv2.imwrite("pic/result.jpg", frame)
        return frame

#############################
#坐标在上述画框中，自己去提取



