class Metrics:
    def __init__(self):
        self.metrics = {
            "Dice": "DICE",
            "Hausdorff distance": "HAUS",
            "Jaccard": "JACC",
            "Accuracy": "ACCU",
            "Precision": "PREC",
            "Specificity": "SPEC",
            "Sensitivity": "SENS",
        }

        self.orderby = {
            "Ascending": True,
            "Descending": False
        }

    def get_metrics(self):
        return self.metrics
