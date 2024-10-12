import cv2, sys, numpy, os 

def recognized(): 
    size = 4
    haar_file = '/Users/andreivince/Desktop/Nixie/resources/haarcascade_frontalface_default.txt'
    datasets = 'DatasetFaces'
    
    # Part 1: Create fisherRecognizer 
    print('Recognizing Face Please Be in sufficient Lights...') 
    

    # Create a list of images and a list of corresponding names 
    (images, labels, names, id) = ([], [], {}, 0) 
    for (subdirs, dirs, files) in os.walk(datasets): 
        for subdir in dirs: 
            names[id] = subdir 
            subjectpath = os.path.join(datasets, subdir) 
            for filename in os.listdir(subjectpath): 
                path = subjectpath + '/' + filename 
                label = id
                img = cv2.imread(path, 0)
                img = cv2.imread(path, 0)

            if img is not None:
                img = numpy.float32(img) / 255.0  # Normalize here
                img = cv2.resize(img, (200, 200))
                images.append(img)
                labels.append(int(label))
            id += 1
    (width, height) = (200, 200) 
    
    # Create a Numpy array from the two lists above 
    (images, labels) = [numpy.array(lis) for lis in [images, labels]] 
    
    # OpenCV trains a model from the images 
    model = cv2.face.LBPHFaceRecognizer_create(neighbors = 8)
    model.train(images, labels) 
    
    # Part 2: Use fisherRecognizer on camera stream 
    face_cascade = cv2.CascadeClassifier(haar_file) 
    webcam = cv2.VideoCapture(0)    
    while True: 
        creator_recognized = False
        (_, im) = webcam.read() 
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) 
        faces = face_cascade.detectMultiScale(gray, 1.3, 5) 
        for (x, y, w, h) in faces: 
            cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2) 
            face = gray[y:y + h, x:x + w] 
            face_resize = cv2.resize(face, (width, height)) 
            # Try to recognize the face 
            prediction = model.predict(face_resize) 
            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 3) 
    
            if prediction[1]<150: 
    
                cv2.putText(im, '% s - %.0f' % (names[prediction[0]], prediction[1]), (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0)) 
                if names[prediction[0]] == "andreivince":
                        creator_recognized = True
                        return creator_recognized
                else: 
                    cv2.putText(im, 'not recognized',  
    (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0)) 
    
        
        key = cv2.waitKey(10) 
        if key == 27: 
            break
    