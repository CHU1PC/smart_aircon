import numpy as np
import numpy.typing as npt
from loguru import logger

from camera import capture_frames
from recognition import face_store
from recognition.detect import detect_and_align
from recognition.embed import embed

_FRAMES = 7


def recognize(threshold: float = 0.6) -> tuple[str, float]:
    """Recognizes a face from a short burst of camera frames.

    Args:
        threshold: Minimum cosine similarity to accept a match.

    Returns:
        (user_id, score) for the best match, or ("unknown", best_score) if below
        threshold or if no face was found in any frame.
    """
    embeddings: list[npt.NDArray[np.float32]] = []
    for frame in capture_frames(_FRAMES):
        face = detect_and_align(frame)
        if face is not None:
            embeddings.append(embed(face))

    if not embeddings:
        logger.info("No face detected in any frame.")
        return "unknown", 0.0

    mean = np.mean(embeddings, axis=0)
    query: npt.NDArray[np.float32] = (mean / np.linalg.norm(mean)).astype(np.float32)
    store = face_store.load()
    return face_store.match(store, query, threshold)


if __name__ == "__main__":
    user_id, score = recognize()
    logger.info(f"Recognized: {user_id} (score={score:.3f})")
