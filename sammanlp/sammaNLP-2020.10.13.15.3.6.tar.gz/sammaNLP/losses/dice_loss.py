import torch
from torch import nn


class DiceLoss(nn.Module):
    """DiceLoss implemented from 'Dice Loss for Data-imbalanced NLP Tasks'
    Useful in dealing with unbalanced data
    """

    def __init__(self):
        super(DiceLoss, self).__init__()

    def forward(self, input, target):
        '''
        input: [N, C]
        target: [N, ]
        '''
        prob = torch.softmax(input, dim=1)
        prob = torch.gather(prob, dim=1, index=target.unsqueeze(1))
        dsc_i = 1 - ((1 - prob) * prob) / ((1 - prob) * prob + 1)
        dice_loss = dsc_i.mean()
        return dice_loss


class SelfAdjDiceLoss(nn.Module):
    """
    create a criterion that optimizes a multi-class self-adjusting Diceloss
    (Dice Loss for Data-imbalanced NLP Tasks) paper

    arguments:
        alpha(float): a factor to push down the of easy examples
        gamma(float): a factor added to both the nominator and denomiinator for smoothing purposes


    shape:
        logit: (N,C) where N is the batch size and C is the number of class
        target:(N,) where each value is in [0,C-1]

    """

    def __init__(self, alpha: float = 1.0, gamma: float = 1.0):
        super(SelfAdjDiceLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, logit: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        probs = torch.softmax(logit, dim=1)
        probs = torch.gather(probs, dim=1, index=targets.unsqueeze(1))

        probs_with_factor = ((1 - probs) ** self.alpha) * probs
        loss = 1 - (2 * probs_with_factor + self.gamma) / (probs_with_factor + 1 + self.gamma)
        return loss.mean()
