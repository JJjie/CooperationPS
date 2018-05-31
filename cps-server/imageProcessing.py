# -*- coding: utf-8 -*-
# @Time    : 2018/5/31 13:54
# @Author  : UNE
# @Project : cps-server
# @File    : imagePreprocessing.py
# @Software: PyCharm

from PIL import Image
import cv2
import dlib


def recognizeFace(img_path):
    #使用dlib自带的frontal_face_detector作为我们的特征提取器
    detector = dlib.get_frontal_face_detector()

    # 从文件读取图片
    img = cv2.imread(img_path)
    # 转为灰度图片
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 使用detector进行人脸检测 dets为返回的结果
    dets = detector(gray_img, 1)

    #使用enumerate 函数遍历序列中的元素以及它们的下标
    #下标i即为人脸序号
    #left：人脸左边距离图片左边界的距离 ；right：人脸右边距离图片左边界的距离
    #top：人脸上边距离图片上边界的距离 ；bottom：人脸下边距离图片上边界的距离
    position = [] # [left, upper, right, bottom]
    for i, d in enumerate(dets):
        x1 = d.top() if d.top() > 0 else 0
        y1 = d.bottom() if d.bottom() > 0 else 0
        x2 = d.left() if d.left() > 0 else 0
        y2 = d.right() if d.right() > 0 else 0
        # img[y:y+h,x:x+w]
        position.append([x2, x1, y2, y1])
    return position

def mergeImage(position, filedir, filename, originfilename):
    img = Image.open(filedir / filename)
    oimg = Image.open(filedir / originfilename)
    oimg.paste(img, position)
    oimg.save(filedir / originfilename)