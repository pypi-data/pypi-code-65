from typing import Protocol


class FewShotDatasetDelegate(Protocol):
    """Any instance of the protocol is a FewShot dataset"""
    K: int  # K-shot for K instance
    N: int  # N classes in support set

    def len(self):
        """Length of dataset"""
        ...
