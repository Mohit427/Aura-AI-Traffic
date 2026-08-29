import math

# Placeholder scale factor.
# This will be calibrated using the camera scene.
SCALE_FACTOR = 0.05


def estimate_speed(y_prev, y_curr, dt, scale=SCALE_FACTOR):
    """
    Estimate object speed from pixel displacement.

    y_prev : previous y-coordinate
    y_curr : current y-coordinate
    dt     : time between frames in seconds
    scale  : metres per pixel
    """

    if dt <= 0:
        return 0.0

    pixel_distance = abs(y_curr - y_prev)

    distance_m = pixel_distance * scale

    speed_mps = distance_m / dt

    return speed_mps


# Simple sanity test
speed = estimate_speed(
    y_prev=100,
    y_curr=150,
    dt=1.0
)

print("Estimated speed:", speed, "m/s")