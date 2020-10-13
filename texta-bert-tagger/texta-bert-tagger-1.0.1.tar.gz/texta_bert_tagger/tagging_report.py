import datetime
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    roc_curve,
    auc,
    f1_score,
    accuracy_score
)

class TaggingReport:

    def __init__(self, y_test, y_pred, average="macro"):
        self.f1_score = f1_score(y_test, y_pred, average=average, zero_division=0)
        self.confusion = confusion_matrix(y_test, y_pred)
        self.precision = precision_score(y_test, y_pred, average=average, zero_division=0)
        self.recall = recall_score(y_test, y_pred, average=average, zero_division=0)
        self.accuracy = accuracy_score(y_test, y_pred)
        self.epoch = None
        self.training_loss = None
        self.validation_loss = None
        self.validation_time = None
        self.training_time = None
        self._round_digits = 5
    
    def _format_time(self, elapsed):
        """
        Takes a time in seconds and returns a string hh:mm:ss
        """
        # Round to the nearest second.
        ft_time = None
        if elapsed:
            elapsed_rounded = int(round((elapsed)))
            # Format as hh:mm:ss
            ft_time = str(datetime.timedelta(seconds=elapsed_rounded))
        return ft_time       
           
    def to_dict(self):
        return {
            "f1_score": round(self.f1_score, self._round_digits),
            "precision": round(self.precision, self._round_digits),
            "recall": round(self.recall, self._round_digits),
            "confusion_matrix": self.confusion.tolist(),
            "accuracy": round(self.accuracy, self._round_digits),
            "training_loss": round(self.training_loss, self._round_digits),
            "validation_loss": round(self.validation_loss, self._round_digits),
            "training_time" : self._format_time(self.training_time),
            "validation_time": self._format_time(self.validation_time),
            "epoch": self.epoch + 1 # epoch count starts at 0
        }
