import cv2


def enhance_low_light(frame):
    """
    Enhance a low-light traffic frame using CLAHE.

    CLAHE improves local contrast while preserving
    important image details for object detection.
    """

    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    l_enhanced = clahe.apply(l)

    enhanced_lab = cv2.merge(
        (l_enhanced, a, b)
    )

    return cv2.cvtColor(
        enhanced_lab,
        cv2.COLOR_LAB2BGR
    )