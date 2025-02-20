"""Implements Precision Meter."""
import torch

from torchflare.metrics.meters import MetricMeter, _BaseInputHandler


class Precision(_BaseInputHandler, MetricMeter):
    """Class to compute Precision Score.

    Support binary, multiclass and multilabel cases
    """

    def __init__(
        self,
        num_classes: int,
        average: str = "macro",
        threshold: float = 0.5,
        multilabel: bool = False,
    ):
        """Constructor method for Precision Class.

        Args:
            num_classes: The number of num_classes.
            average: The type of reduction to apply.
                macro: calculate metrics for each class and averages them with equal weightage to each class.
                micro: calculate metrics globally for each sample and class.
            threshold: The threshold value to transform probability predictions to binary values(0,1)
            multilabel: Set it to True if your problem is  multilabel classification.
        """
        super(Precision, self).__init__(
            threshold=threshold,
            num_classes=num_classes,
            multilabel=multilabel,
            average=average,
        )

        self._outputs = None
        self._targets = None

        self.reset()

    def handle(self) -> str:
        """Method to get the class name.

        Returns:
            The name of the class
        """
        return self.__class__.__name__.lower()

    def accumulate(self, outputs: torch.Tensor, targets: torch.Tensor):
        """Method to accumulate the outputs and targets.

        Args:
            outputs : raw logits from the network.
            targets : targets to use for computing accuracy
        """
        outputs, targets = self.detach_tensor(outputs), self.detach_tensor(targets)
        self._outputs.append(outputs)
        self._targets.append(targets)

    @property
    def value(self) -> torch.Tensor:
        """Computes the Precision Score.

        Returns:
            The computed precision score.
        """
        outputs = torch.cat(self._outputs)
        targets = torch.cat(self._targets)

        tp, fp, tn, fn = self.compute_stats(outputs=outputs, targets=targets)

        precision = self.reduce(numerator=tp, denominator=tp + fp)
        return precision

    def reset(self):
        """Resets the accumulation Lists."""
        self._outputs = []
        self._targets = []


__all__ = ["Precision"]
