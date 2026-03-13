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
            "Weighted Cohen's Kappa": "wck",
            "Positive Likelihood ratio +": "lr+",
            "Intersection over Union": "iou",
            "F-beta score": "fbeta",
            "Dice Score Coefficient": "dsc",
            "Matthews Correlation Coefficient": "mcc",
            "CL Dice": "cldice",
            "Average Symmetric Surface Distance": "assd",
            "Boundary IoU": "boundary_iou",
            "Hausdorff dist.": "hd",
            "Hausdorff dist. percentile": "hd_perc",
            "Mean Absolute Surface Distance": "masd",
            "Normalized Surface Distance": "nsd",
            "Positive Predictive Value": "ppv",
            "Negative Predictive Value": "npv",
            "Intersection over Reference": "ior",
            "Sensitivity (Recall)": "sensitivity",
            "Specificity ": "specificity",
            "Absolute Volume Difference Ratio": "avdr"

        }



        self.orderby = {"Ascending": True, "Descending": False}

    def get_metrics(self):
        return self.metrics
