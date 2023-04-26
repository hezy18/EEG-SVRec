# frame
# generate video_feature.csv

import math
import cv2
import os
from PIL import Image, ImageStat
import pandas as pd
import csv
import numpy as np
# from skimage.measure import compare_ssim, compare_psnr, compare_mse


def save_image(image, addr, num):
    address = addr + str(num) + '.jpg'
    cv2.imwrite(address, image)

def compute_brightness(image_path):
    im = Image.open(image_path).convert('L')
    stat = ImageStat.Stat(im)
    return stat.mean[0]

def compute_HSV(image_path):
    img = cv2.imread(image_path)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue = img_hsv[:,0].mean()
    saturation = img_hsv[:,1].mean()
    value = img_hsv[:,2].mean()
    # print('HSV',hue, saturation, value)
    return hue, saturation, value

def compute_entropy(image_path):
    img = cv2.imread(image_path,0)
    
    hist_cv = cv2.calcHist([img],[0],None,[256],[0,256])
    P= hist_cv/(len(img)*len(img[0]))
    E_1D = np.sum([p *np.log2(1/p) for p in P])
    
    N = 1
    S=img.shape
    IJ = []
    for row in range(S[0]):
        for col in range(S[1]):
            Left_x=np.max([0,col-N])
            Right_x=np.min([S[1],col+N+1])
            up_y=np.max([0,row-N])
            down_y=np.min([S[0],row+N+1])
            region=img[up_y:down_y,Left_x:Right_x]
            j = (np.sum(region) - img[row][col])/((2*N+1)**2-1)
            IJ.append([img[row][col],j])
    # print('IJ',IJ)
    F=[]
    arr = [list(i) for i in set(tuple(j) for j in IJ)]
    for i in range(len(arr)):
        F.append(IJ.count(arr[i]))
    # print('F',F)
    P=np.array(F)/(img.shape[0]*img.shape[1])
    E_2D = np.sum([p *np.log2(1/p) for p in P])
    
    print('E',E_1D,E_2D)
    return E_1D,E_2D

def compute_quality(image_path):
    img = cv2.imread(image_path)
    
    img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # contrast
    contrast = img_grey.std()
    # print('contrast', contrast)
    # laplace
    laplace_var = cv2.Laplacian(img_grey,cv2.CV_64F).var()
    # print('laplace_var', laplace_var)
    
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(img)
    h,w,_ = img.shape
    da = a_channel.sum()/(h*w)-128
    db = b_channel.sum()/(h*w)-128
    histA = [0]*256
    histB = [0]*256
    for i in range(h):
        for j in range(w):
            ta = a_channel[i][j]
            tb = b_channel[i][j]
            histA[ta] += 1
            histB[tb] += 1
    msqA = 0
    msqB = 0
    for y in range(256):
        msqA += float(abs(y-128-da))*histA[y]/(w*h)
        msqB += float(abs(y - 128 - db)) * histB[y] / (w * h)
    cast = math.sqrt(da*da+db*db)/math.sqrt(msqA*msqA+msqB*msqB)
    # print('color cast',cast)
    return contrast, laplace_var, cast


if __name__ == "__main__":
    result = pd.DataFrame(columns=('id', 'count', 'height', 'width', 'brightness', 'dif_brightness', 'E_1D', 'dif_E_1D', 'E_2D', 'dif_E_2D', 
                                   'contrast', 'dif_contrast', 'laplace_var', 'dif_laplace_var', 'color_cast', 'dif_color_cast',
                                   'hue', 'dif_hue', 'saturation', 'dif_saturation', 'value', 'dif_value'))
    filenames = os.listdir('douyin')
    for filename in filenames:
    # i=len(filenames)-1
    # while i>=0:
    #     filename = filenames[i]
    #     i-=1
        print(filename)
        id = filename.split('.')[0]
        # if os.path.exists('image/' + id):
        #     continue
        capture = cv2.VideoCapture('douyin/'+filename)
        cv2.waitKey(1000)
        video_count = capture.get(cv2.CAP_PROP_FRAME_COUNT)    
        video_height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        video_width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        video_fps = capture.get(cv2.CAP_PROP_FPS)
        
        timeF = 30
        j = 0
        count=0
        s_brightness = []
        s_E_1D, s_E_2D = [], []
        s_contrast, s_laplace_var, s_color_cast = [], [], []
        s_hue, s_saturation, s_value = [],[], []
        success=True
        if capture.isOpened():
            while success:
                success, frame = capture.read()
                j += 1
                if j % timeF == 0:
                    if not os.path.exists('image/' + id):
                        os.makedirs('image/' + id)
                    try:
                        img = cv2.resize(frame, (96, int(36/video_width*video_height)), interpolation=cv2.INTER_LINEAR)
                    except:
                        print('resize fail',id)
                        img=frame
                    if not os.path.exists('image/' + id+'/'+str(count)+'.jpg'):
                        if frame is not None:
                            work=cv2.imwrite('image/' + id+ '/'+str(count)+'.jpg', img)
                            if not work:
                                print('imwrite not work id',id)
                            cv2.waitKey(1000)
                        
                    img_path = 'image/' + id + '/' + str(count) + '.jpg'
                    
                    try:
                        s_brightness.append(compute_brightness(img_path))
                    except:
                        print('compute brightness error, img_path=%s' % img_path)
                    
                    try:
                        E_1D, E_2D = compute_entropy(img_path)
                        if E_1D != np.nan:
                            s_E_1D.append(E_1D)
                        if E_2D != np.nan:
                            s_E_2D.append(E_2D)
                    except:
                        print('compute entropy error, img_path=%s' % img_path)
                    
                    try:
                        contrast, laplace_var, color_cast = compute_quality(img_path)
                        s_contrast.append(contrast)
                        s_laplace_var.append(laplace_var)
                        s_color_cast.append(color_cast)
                    except:
                        print('compute quality error, img_path=%s' % img_path)
                    
                    try:
                        hue, saturation, value = compute_HSV(img_path)
                        s_hue.append(hue)
                        s_saturation.append(saturation)
                        s_value.append(value)
                    except:
                        print('compute HSV error, img_path=%s' % img_path)
                    count+=1
        mean_brightness = np.array(s_brightness).mean()
        mean_E_1D = np.array(s_E_1D).mean()
        mean_E_2D = np.array(s_E_2D).mean()
        mean_contrast = np.array(s_contrast).mean()
        mean_laplace_var = np.array(s_laplace_var).mean
        mean_color_cast = np.array(s_color_cast).mean()
        mean_hue = np.array(s_hue).mean()
        mean_saturation = np.array(s_saturation).mean()
        mean_value = np.array(s_value).mean()
        
        
        mean_dif1_brightness = np.diff(s_brightness).mean()
        mean_dif1_E_1D = np.diff(s_E_1D).mean()
        mean_dif1_E_2D = np.diff(s_E_2D).mean()
        mean_dif1_contrast = np.diff(s_contrast).mean()
        mean_dif1_laplace_var = np.diff(s_laplace_var).mean()
        mean_dif1_color_cast = np.diff(s_color_cast).mean()
        mean_dif1_hue = np.diff(s_hue).mean()
        mean_dif1_saturation = np.diff(s_saturation).mean()
        mean_dif1_value = np.diff(s_value).mean()
        
        
        result = result.append(pd.DataFrame({'id':[id],'count':[video_count],'height':[video_height],'width':[video_width],
                                             'brightness':[mean_brightness],'dif_brightness':[mean_dif1_brightness],
                                             'E_1D':[E_1D], 'dif_E_1D':[mean_dif1_E_1D], 'E_2D':[E_2D], 'dif_E_2D':[mean_dif1_E_2D],
                                             'contrast':[contrast], 'dif_contrast':[mean_dif1_contrast],
                                             'laplace_var':[laplace_var], 'dif_laplace_var':[mean_dif1_laplace_var], 
                                             'color_cast':color_cast, 'dif_color_cast':[mean_dif1_color_cast],
                                             'hue':[hue], 'dif_hue':[mean_dif1_hue], 
                                             'saturation':[saturation], 'dif_saturation':[mean_dif1_saturation], 
                                             'value':[value], 'dif_value':[mean_dif1_value],
                                             }),ignore_index=True)
        
        capture.release()
    result.to_csv('video_img_feature.csv')
        
    
    
