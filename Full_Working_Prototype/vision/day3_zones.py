import cv2
import numpy as np

# Crosswalk / vulnerable-user zone
CROSSWALK_ZONE = np.array([
    [333, 382],    # Top-left
    [881, 330],    # Top-right
    [1125, 623],   # Bottom-right
    [225, 619]     # Bottom-left
])


def in_zone(cx, cy, zone=CROSSWALK_ZONE):
    return cv2.pointPolygonTest(
        zone,
        (cx, cy),
        False
    ) >= 0


# Manual tests
print("Inside test:", in_zone(600, 500))
print("Outside test:", in_zone(50, 50))