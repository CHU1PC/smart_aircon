from collections.abc import Mapping, Sequence

import numpy as np
import numpy.typing as npt

class NodeArg:
    name: str
    type: str
    shape: list[int | str | None]

class InferenceSession:
    def __init__(
        self,
        path_or_bytes: str | bytes,
        sess_options: object = ...,
        providers: Sequence[str] | None = ...,
        provider_options: Sequence[object] | None = ...,
    ) -> None: ...
    def get_inputs(self) -> list[NodeArg]: ...
    def get_outputs(self) -> list[NodeArg]: ...
    def run(
        self,
        output_names: Sequence[str] | None,
        input_feed: Mapping[str, npt.NDArray[np.generic]],
        run_options: object = ...,
    ) -> list[npt.NDArray[np.float32]]: ...
