import torch
import cv2
from pathlib import Path


class DetectorYolov5():
    def __init__(self, model="yolov5s6"):
        self.model = torch.hub.load('ultralytics/yolov5', model)

    def anote_save(self, img, crop=False, is_cv2_bgr=True, save_dir=Path("out")):
        if is_cv2_bgr:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        result = self.model(img)
        result.display(pprint=True, show=False, save=True, crop=crop, render=False, save_dir=save_dir)

    def anote(self, img, is_cv2_bgr=True):
        if is_cv2_bgr:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        result = self.model(img)
        result.render()
        img = result.imgs[0]

        if is_cv2_bgr:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        return img


if __name__ == "__main__":
    src = cv2.imread("test.jpg")
    det = DetectorYolov5(model="yolov5x6")
    det.anote_save(src)

    # dst = det.anote(src)
    # cv2.imshow("yolo", dst)
    # cv2.waitKey(0)
