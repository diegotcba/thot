from __future__ import print_function

import sys
import cv2
from scipy.misc import imresize

class GUI:

    name = 'Thot display'

    def __init__(self):
        cv2.namedWindow(self.name)
        self.secondary = []

    def progress(self, text, val, total=100):
        print("\r%s [%d] @ %3d%%"%(text, val, int(100.0*val/total)), end='')
        sys.stdout.flush()

    def clear(self):
        names = [self.name] + self.secondary
        for name in names:
            cv2.destroyWindow(name)
            cv2.imshow(name, 0)
        self.secondary.clear()
        self._wk()

    def _wk(self):
        for n in range(5):
            if cv2.waitKey(20) <= 0:
                break

    def ok_cancel(self, duration=10, default=True):
        for n in range(duration):
            x = cv2.waitKey(100)
            if x == 27:
                return False
            elif x&0xFF in (10, 32):
                return True
        return default

    def display(self, image, text, resize=None, crop=False, disp_number=0):
        if crop:
            image = image[crop[0] or slice(None, None), crop[1] or slice(None, None)]

        if resize:
            image = image.copy()
            if isinstance(resize, float):
                resize = tuple(int(x*resize) for x in image.shape[:2])

        if text:
            black = (0, 0, 0)
            white = (255, 255, 255)
            cv2.putText(image, text, (9, 99), cv2.FONT_HERSHEY_SIMPLEX, 2.0, black)
            cv2.putText(image, text, (12, 102), cv2.FONT_HERSHEY_SIMPLEX, 2.0, black)
            cv2.putText(image, text, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 2.0, white)
            cv2.putText(image, text, (11, 101), cv2.FONT_HERSHEY_SIMPLEX, 2.0, white)

        if resize:
            image = imresize(image, resize)
        if disp_number:
            name = "%s %d"%(self.name, disp_number)
            cv2.imshow(name, image)
            if not name in self.secondary:
                self.secondary.append(name)
        else:
            cv2.imshow(self.name, image)
        self._wk()

gui = GUI()
