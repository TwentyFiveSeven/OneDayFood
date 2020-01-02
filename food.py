# coding: utf-8

# In[44]:


import numpy as np
import cv2 as cv

#���� �������� ���� ū �� ����
def test(shape_img):

    #�̹��� �ҷ��µ� 224*224�� resize
#    shape_img = cv.resize(shape_img,(112,112),interpolation = cv.INTER_LINEAR_EXACT)

    
    #�̹��� �ҷ��µ� gray �����Ϸ� ���� �� resize
    img_gray = cv.cvtColor(shape_img,cv.COLOR_BGR2GRAY)#cv.imread(name, cv.IMREAD_GRAYSCALE)
    img_gray = cv.resize(img_gray,(112,112),interpolation = cv.INTER_LINEAR_EXACT)

    img_gray = cv.medianBlur(img_gray,5)
    img_color = cv.cvtColor(img_gray,cv.COLOR_GRAY2BGR)

    #�̹������� ���� ã�� �Լ�
    circles = cv.HoughCircles(img_gray,cv.HOUGH_GRADIENT,1,20,
                                param1=50,param2=35,minRadius=28,maxRadius=56)
    
    #������ ������ ����Ʈ�� ����
    circles = np.uint16(np.around(circles))
    
    
    y=0
    x=0
    radius = 0

    #    �������� ���� ū ���� ã�� �ݺ���
    
    for c in circles[0,:]:
        if radius < c[2] :
            
            #���� �߽� ��ǥ
            x = c[1]
            y = c[0]
            #���� ������
            radius = c[2]
        
   
    shape_img = shape_img[x-radius : x+radius , y-radius : y+radius]
    x,y,_ = shape_img.shape
    if x < 112 :
        shape_img = cv.resize(shape_img,(112,112),interpolation = cv.INTER_LINEAR_EXACT)
    
    return shape_img
