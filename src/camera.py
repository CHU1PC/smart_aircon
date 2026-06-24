import cv2
from loguru import logger


def capture_image() -> cv2.typing.MatLike:
    """Captures a image with the default camera (index 0) using OpenCV.

    Returns:
        cv2.typing.MatLike: The captured image as a NumPy array.

    Raises:
        ValueError: If the image could not be captured.
    """
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    for _ in range(5):
        cap.read()

    for time in [2.0, 3.0, 5.0]:
        ret, frame = cap.read()
        if ret:
            cap.release()
            return frame

        logger.error(f"Failed to capture image. Retrying in {time} seconds...")
        cap.release()
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        for _ in range(5):
            cap.read()
        cv2.waitKey(int(time * 1000))

    err = "Failed to capture image from camera. Maybe the camera is not connected or accessible."
    logger.error(err)
    raise ValueError(err)
