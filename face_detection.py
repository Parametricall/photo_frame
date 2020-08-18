import cv2.cv2 as cv2

title = "PersonOfInterest"
cv2.namedWindow(title)
video = cv2.VideoCapture(0)

if video.isOpened():
    rval, frame = video.read()
else:
    rval = False

faceCascade = cv2.CascadeClassifier(
    "./.venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml"
)
eye_cascade = cv2.CascadeClassifier(
    "./.venv/Lib/site-packages/cv2/data/haarcascade_eye.xml"
)

while rval:
    cv2.imshow(title, frame)
    rval, frame = video.read()
    faces = faceCascade.detectMultiScale(frame)
    eyes = eye_cascade.detectMultiScale(frame)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(frame, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)


    num_faces = len(faces)
    num_eyes = len(eyes)

    if num_eyes == 2 * num_faces:
        cv2.circle(frame, (100, 100), 63, (0,0,255), -1)



    key = cv2.waitKey(20)
    if key == 27:  # exit on ESC
        break

video.release()
cv2.destroyWindow(title)

# # face_cascade = cv2.CascadeClassifier("./.venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml")
# # img = cv2.imread("./media/usb/images/Disneyland_2005/Disney 6.jpg")
# # img = cv2.imread("./.venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml")
# img = cv2.resize(img, (960, 540))
#
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
# faces = face_cascade.detectMultiScale(gray, 1.1, 4)
#
# for (x, y, w, h) in faces:
#     cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
#
# cv2.imshow('img', img)
# cv2.waitKey()
