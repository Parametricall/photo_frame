import cv2.cv2 as cv2
import numpy


def static_image_face_detection(pil_image):
    face_cascade = cv2.CascadeClassifier(
        "./.venv/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml")
    eye_cascade = cv2.CascadeClassifier(
        "./.venv/Lib/site-packages/cv2/data/haarcascade_eye.xml"
    )
    img = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)
    # img = cv2.resize(img, (960, 540))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)

        # eyes = eye_cascade.detectMultiScale(gray, 1.1, 10)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 0, 255),
                          2)

    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # cv2.imshow('img', img)
    # cv2.waitKey()

def main():
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
                cv2.rectangle(frame, (ex, ey), (ex + ew, ey + eh), (0, 255, 0),
                              2)

        num_faces = len(faces)
        num_eyes = len(eyes)

        if num_eyes == 2 * num_faces:
            cv2.circle(frame, (100, 100), 63, (0, 0, 255), -1)

        key = cv2.waitKey(20)
        if key == 27:  # exit on ESC
            break

    video.release()
    cv2.destroyWindow(title)

if __name__ == '__main__':
    main()
