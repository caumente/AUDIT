import numpy as np


def errors_per_class(ground_truth, predicted, unique_classes):
    # Find all unique classes present in the ground truth data and predictions
    num_classes = len(unique_classes)

    # Initialize a zero matrix with the maximum range of classes
    errors = np.zeros((num_classes, num_classes), dtype=np.int32)

    # Convert ground truth and predicted to arrays for indexing
    ground_truth = np.array(ground_truth)
    predicted = np.array(predicted)

    # Calculate indices where ground truth and prediction match
    match_indices = ground_truth == predicted

    # Calculate errors per class
    for i, class_i in enumerate(unique_classes):
        # Find indices where ground truth equals class_i
        class_indices = ground_truth == class_i

        # Count errors for each unique class predicted when ground truth is class_i
        unique, counts = np.unique(predicted[class_indices & ~match_indices], return_counts=True)

        # Map unique classes to their indices in unique_classes
        unique_to_index = {class_j: index for index, class_j in enumerate(unique_classes)}

        # Update errors matrix
        for class_j, count in zip(unique, counts):
            if class_j in unique_to_index:
                errors[i, unique_to_index[class_j]] = count

    return errors


def normalize_matrix_per_row(matrix):
    row_sums = matrix.sum(axis=1)
    zero_sum_mask = row_sums == 0
    row_sums[zero_sum_mask] = 1
    normalized_matrix = 100 * matrix / row_sums[:, np.newaxis]
    normalized_matrix[zero_sum_mask] = 0
    return normalized_matrix
