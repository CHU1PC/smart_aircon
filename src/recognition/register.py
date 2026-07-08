import argparse

import numpy as np
import numpy.typing as npt
from loguru import logger

from camera import capture_frames
from recognition import face_store
from recognition.detect import detect_and_align
from recognition.embed import embed


def register(user_id: str, count: int) -> None:
    """Captures a burst of frames and stores the user's mean face embedding.

    Args:
        user_id: The identifier to enroll under.
        count: Number of frames to capture in one burst.
    """
    embeddings: list[npt.NDArray[np.float32]] = []
    for frame in capture_frames(count):
        face = detect_and_align(frame)
        if face is not None:
            embeddings.append(embed(face))

    if not embeddings:
        logger.error("No face detected in any frame; aborting")
        return

    mean = np.mean(embeddings, axis=0)
    embedding: npt.NDArray[np.float32] = (mean / np.linalg.norm(mean)).astype(np.float32)
    store = face_store.load()
    store[user_id] = embedding
    face_store.save(store)
    logger.info(f"Registered '{user_id}' from {len(embeddings)}/{count} frames ({len(store)} users total)")


def main() -> None:
    """Command-line interface for registering a user's face."""
    parser = argparse.ArgumentParser(description="Register a user's face into the store")
    parser.add_argument("--user", required=True)
    parser.add_argument("--count", type=int, default=15)
    args = parser.parse_args()
    register(args.user, args.count)


if __name__ == "__main__":
    main()
