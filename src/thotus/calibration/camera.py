from thotus.ui import gui
from thotus import settings

import cv2
import numpy as np
from thotus.calibration.chessboard import chess_detect, chess_draw


def calibration(calibration_data, images):
    obj_points = []
    img_points = []
    found_nr = 0

    failed_serie = 0
    term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.001)
    flags = cv2.CALIB_CB_FAST_CHECK
    pattern_points = settings.get_pattern_points()

    for idx, fn in enumerate(images):
        gui.progress('Webcam calibration %s (%d found)... ' % (fn, found_nr), idx, len(images))
        img = cv2.imread(fn, 0)
        # rotation:
        img = cv2.flip(cv2.transpose(img), 1)

        if img is None:
            print("Failed to load", fn)
            continue

        w, h = img.shape[:2]

        found, corners = chess_detect(img, flags)

        if not found:
            if found_nr > 20 and failed_serie > 6:
                break
            failed_serie += 1
            continue

        if flags & cv2.CALIB_CB_FAST_CHECK:
            flags -= cv2.CALIB_CB_FAST_CHECK

        failed_serie = 0
        found_nr += 1
        cv2.cornerSubPix(img, corners, (11, 11), (-1, -1), term)

        METADATA[fn]['chess_corners'] = corners
        img_points.append(corners.reshape(-1, 2))
        obj_points.append(pattern_points)

        # compute mask
        p1 = corners[0][0]
        p2 = corners[settings.PATTERN_MATRIX_SIZE[0] - 1][0]
        p3 = corners[settings.PATTERN_MATRIX_SIZE[0] * (settings.PATTERN_MATRIX_SIZE[1] - 1)][0]
        p4 = corners[settings.PATTERN_MATRIX_SIZE[0] * settings.PATTERN_MATRIX_SIZE[1] - 1][0]
        points = np.array([p1, p2, p4, p3], dtype='int32')
        METADATA[fn]['chess_contour'] = points

        chess_draw(img, found, corners)
        gui.display(img[int(img.shape[0]/3):-100,], 'chess')

    if settings.skip_calibration:
        settings.load_data(calibration_data)
        return

    if not obj_points:
        raise ValueError("Unable to detect pattern on screen :(")

    print("\nComputing calibration...")
    rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(np.array(obj_points), np.array(img_points), (w, h), None, None)

    camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w,h))

    calibration_data.camera_matrix = camera_matrix
    calibration_data.distortion_vector = dist_coefs.ravel()

    settings.save_data(calibration_data)