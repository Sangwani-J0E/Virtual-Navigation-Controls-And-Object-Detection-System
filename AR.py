import cv2
import numpy as np
import pygame

# Initialize video capture and target image
cap = cv2.VideoCapture(1)
imgTarget = cv2.imread('TargetImage.jpg')
myVid = cv2.VideoCapture('video.mp4')

detection = False
frameCounter = 0

# Load video frame and resize to match target image dimensions
success, imgVideo = myVid.read()
hT, wT, cT = imgTarget.shape
imgVideo = cv2.resize(imgVideo, (wT, hT))

# Initialize ORB detector
orb = cv2.ORB_create(nfeatures=1000)
kp1, des1 = orb.detectAndCompute(imgTarget, None)

# Initialize Pygame for audio playback
pygame.mixer.init()
pygame.mixer.music.load('video_audio.mp3')  # Ensure the audio file matches the video

# Function to stack images vertically for visualization
def stackImagesVertical(imgArray, scale):
    sizeW = imgArray[0].shape[1]
    sizeH = imgArray[0].shape[0]
    for i in range(len(imgArray)):
        imgArray[i] = cv2.resize(imgArray[i], (sizeW, sizeH), None, scale, scale)
        if len(imgArray[i].shape) == 2:
            imgArray[i] = cv2.cvtColor(imgArray[i], cv2.COLOR_GRAY2BGR)
    stackedImage = np.vstack(imgArray)
    return stackedImage

# Main processing loop
while True:
    success, imgWebcam = cap.read()
    if not success:
        break

    imgAug = imgWebcam.copy()
    kp2, des2 = orb.detectAndCompute(imgWebcam, None)

    if not detection:
        myVid.set(cv2.CAP_PROP_POS_FRAMES, 0)
        frameCounter = 0
        if pygame.mixer.music.get_busy():  # Stop audio if playing
            pygame.mixer.music.stop()
    else:
        success, imgVideo = myVid.read()
        if not success:
            myVid.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, imgVideo = myVid.read()
        imgVideo = cv2.resize(imgVideo, (wT, hT))

    imgWarp = np.zeros_like(imgWebcam)

    # Match features and find good matches
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)

    if len(good) > 20:
        if not detection:  # Start audio playback
            pygame.mixer.music.play(-1)  # Loop indefinitely
        detection = True
        srcPts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dstPts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        matrix, mask = cv2.findHomography(srcPts, dstPts, cv2.RANSAC, 5)

        pts = np.float32([[0, 0], [0, hT], [wT, hT], [wT, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, matrix)
        imgWebcam = cv2.polylines(imgWebcam, [np.int32(dst)], True, (255, 0, 255), 3)

        imgWarp = cv2.warpPerspective(imgVideo, matrix, (imgWebcam.shape[1], imgWebcam.shape[0]))

        maskNew = np.zeros((imgWebcam.shape[0], imgWebcam.shape[1]), np.uint8)
        cv2.fillPoly(maskNew, [np.int32(dst)], (255, 255, 255))
        maskInv = cv2.bitwise_not(maskNew)
        imgAug = cv2.bitwise_and(imgAug, imgAug, mask=maskInv)
        imgAug = cv2.bitwise_or(imgWarp, imgAug)
    else:
        detection = False

    imgStacked = stackImagesVertical([imgAug, imgWebcam, imgVideo, imgTarget, imgWarp], 0.5)
    cv2.imshow('Main Output', imgStacked)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

    frameCounter += 1

# Release resources and close all windows
cap.release()
myVid.release()
pygame.mixer.music.stop()
pygame.mixer.quit()
cv2.destroyAllWindows()
