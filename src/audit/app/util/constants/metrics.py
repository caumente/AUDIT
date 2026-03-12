class Metrics:
    def __init__(self):
        self.metrics = {
            # AUDIT backend
            "Dice": "DICE",
            "Hausdorff distance": "HAUS",
            "Jaccard": "JACC",
            "Accuracy": "ACCU",
            "Precision": "PREC",
            "Specificity": "SPEC",
            "Sensitivity": "SENS",

            # metrics reloaded backend
            "Number of reference pixels": "numb_ref",
            "Number of predicted pixels": "numb_pred",
            "True positives": "numb_tp",
            "False positives": "numb_fp",
            "False negatives": "numb_fn",
            "Accuracy ": "accuracy",
            "Net Benefit": "nb",
            "Expected Cost": "ec",
            "Balanced Accuracy": "ba",
            "Cohen's kappa": "cohens_kappa",
            "Positive Likelihood ratio +": "lr+",
            "Intersection over Union": "iou",
            "F-beta score": "fbeta",
            "Dice Score Coefficient": "dsc",
            "Youden index": "youden_ind",
            "Matthews Correlation Coefficient": "mcc",
            "CL Dice": "cldice",
            "Average Aymmetric Aurface Sistance": "assd",
            "Boundary IoU": "boundary_iou",
            "Hausdorff dist.": "hd",
            "Hausdorff dist. percentile": "hd_perc",
            "Mean Absolute Surface Distance": "masd",
            "Normalized Surface Distance": "nsd"

        }



        self.orderby = {"Ascending": True, "Descending": False}

    def get_metrics(self):
        return self.metrics
