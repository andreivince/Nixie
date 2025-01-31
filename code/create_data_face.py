import cv2, sys, numpy, os



path = './DatasetFaces/andreivince' # Change the Name of the Person

if not os.path.exists(path):
    os.makedirs(path)


(width, height) = (130,100)

face_cascade = cv2.CascadeClassifier('resources/haarcascade_frontalface_default.txt')
webcam = cv2.VideoCapture(0)

count = 10 # Change this number and the one below for more data
while count < 20:
    (_, im) = webcam.read()
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3 , 4)
    for (x,y,w,h) in faces:
        cv2.rectangle(im, (x,y), (x+w,y+h), (255,0,0), 2)
        face = gray [y:y+h,x:x+w]
        face_resize = cv2.resize(face, (width,height))
        cv2.imwrite('% s/% s.png' % (path, count), face_resize) 
    count += 1

    cv2.imshow('OpenCV', im) 