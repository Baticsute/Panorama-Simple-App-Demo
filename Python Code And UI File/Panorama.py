import cv2
import numpy as np
import imutils


def detectAndDescribe(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    descriptor = cv2.xfeatures2d.SIFT_create() ## Version python_opencv_contrib
    (keypoints, desc) = descriptor.detectAndCompute(image, None) ## Tìm keypoint và bộ mô tả desc

    ## <keypoint #$43324> , desc

    keypoints= np.float32([kp.pt for kp in keypoints])
   ## print(keypoints)

    return (keypoints, desc)

def match_descriptors(descA,descB,ratio):

    matcher = cv2.DescriptorMatcher_create("BruteForce") ## Tính khoảng cách 2 điêm vector
    rawMatches = matcher.knnMatch(descA, descB, 2) ## Tìm 2 desc gần giống ( gần nhất với desc1 )
    matches = []
    for m in rawMatches:
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            matches.append((m[0].trainIdx, m[0].queryIdx))
    return matches


def RANSAC(keypoints1,keypoints2,matches,thresh):
    if len(matches) > 4:
        # construct the two sets of points
        ptsA = np.float32([keypoints1[i] for (_, i) in matches])
        ptsB = np.float32([keypoints2[i] for (i, _) in matches])

        (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC,thresh) ## Tìm Homography - Khử nhiễu với RANSAC

        return H,status
    return None

def get_column_index(img,height,num=50):

    t = img.copy()
    th,ma = cv2.threshold(t,0,255,cv2.THRESH_BINARY)
    ma = cv2.cvtColor(ma,cv2.COLOR_BGR2GRAY)
    ##cv2.imshow("temp",ma)
    last_index_top = 0
    last_index_bot = 0
    last_index = 0
    for i in range(ma.shape[1]-1,-1,-1):
        if ma[0][i] != 0:
            last_index_top=i
            break
    for i in range(ma.shape[1]-1,-1,-1):
        if ma[height-1][i] != 0:
            last_index_bot=i
            break

    if last_index_bot > last_index_top:
        last_index = last_index_bot
    else:
        last_index = last_index_top

    return last_index-num ##

def merge_from_image_warp(warp1,warp2,height,width):

    mask = cv2.bitwise_and(warp1,warp2)

    last_index = get_column_index(mask,height)
    for i in range(height):
        for j in range(width):
            if j < last_index:
                warp2[i, j] = warp1[i, j]

    return warp2

def remove_black(img):

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    last_index = 0
    for i in range(gray.shape[1]-1,-1,-1):
        if gray[int(gray.shape[0]/2)][i] != 0:
            last_index=i
            break

    result = img[:,0:last_index]

    return result

def stitch(images,ratio=0.75,reprojThresh=4.0,time=2.0):

    ## Set default size of panorama picture ( sum( width of images ) x height of first image
    pano_height = images[0].shape[0]
    pano_width = 0
    for i in images:
        pano_width = pano_width + i.shape[1]

    keypoints = []
    descriptors = []
    matches = []
    ## Return keypoints and descriptors
    for i in images:
        kp ,desc = detectAndDescribe(i)
        keypoints.append(kp) ## DoG
        descriptors.append(desc)  ## SIFT

    for i in range(len(images)-1):
        m = match_descriptors(descriptors[i],descriptors[i+1],ratio) ## Nối match
        matches.append(m)

    Homo = []
    for i in range(len(images)-1):

        h , status = RANSAC(keypoints[i],keypoints[i+1],matches[i],reprojThresh)
        Homo.append(h)

    ## Calculate Referernce Matrix
    refernce_h = [Homo[0]]
    for i in range(1,len(Homo)):
        h_to_iv = np.dot(Homo[i],refernce_h[i-1])
        refernce_h.append(h_to_iv)

    ## Warp Images
    warp_img = []
    wm = cv2.warpPerspective(images[0],np.eye(3),(pano_width, pano_height))
    warp_img.append(wm)
    for i in range(1,len(images)):
        wm = cv2.warpPerspective(images[i],(np.linalg.inv(refernce_h[i-1])),(pano_width,pano_height))
        warp_img.append(wm)

    ## Merge Each Image
    result = None
    for i in range(len(warp_img)-1):
        result = merge_from_image_warp(warp_img[i],warp_img[i+1],pano_height,pano_width)
    result = remove_black(result)

    return result



'''
imageA = cv2.imread("Image1.jpg",cv2.IMREAD_COLOR)
imageB = cv2.imread("Image2.jpg",cv2.IMREAD_COLOR)
imageC = cv2.imread("3Hill.jpg",cv2.IMREAD_COLOR)
imageD = cv2.imread("yosemite4.jpg",cv2.IMREAD_COLOR)
imageE = cv2.imread("S6.jpg")

imageA = imutils.resize(imageA,width=400)
imageB = imutils.resize(imageB,width=400)
imageC = imutils.resize(imageC,width=400)
imageD = imutils.resize(imageD, width=400)

listim = [imageA,imageB]

##img_blended_simple = np.concatenate((imageA,imageB),axis=1)

r = stitch(listim,time=2.1)

cv2.imshow("Result",r)

cv2.waitKey(0)

'''