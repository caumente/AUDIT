import os
import platform
import subprocess
import colorsys

def get_color(index, total):
    # Generate distinct colors in RGB using HSV
    hue = index / max(total, 1)  # spread hues evenly
    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
    return int(r*255), int(g*255), int(b*255)


# TODO: this functionality only works if all the sequences are present
def run_itk_snap(path, dataset, case, labels=None):
    verification_check = True
    names = ["t1", "t1ce", "t2", "flair", "seg"]
    t1, t1ce, t2, flair, seg = [f"{path}/{dataset}/{dataset}_images/{case}/{case}_{n}.nii.gz" for n in names]

    if labels:
        labels_path = "./src/audit/configs/itk_labels.txt"
        generate_itk_labels(labels, labels_path)
        command = open_itk_command() + ["-l", labels_path, "-g", t1ce, "-s", seg, "-o"] + [t1, t2, flair]
    else:
        command = open_itk_command() + ["-g", t1ce, "-s", seg, "-o"] + [t1, t2, flair]

    # Checking if both path exist
    if os.path.exists(t1ce) and os.path.exists(seg):
        subprocess.run(command)
    # elif os.path.exists(t1ce) and not os.path.exists(seg_path):
    #     subprocess.run(["open", "-n", "-a", "ITK-SNAP", "--args", "-g", img_path])
    # elif not os.path.exists(t1ce) and os.path.exists(seg_path):
    #     subprocess.run(["open", "-n", "-a", "ITK-SNAP", "--args", "-s", seg_path])
    else:
        verification_check = False

    return verification_check


def generate_itk_labels(labels, output_file):
    total_labels = len(labels)
    lines = [
        "# ITK-SNAP Label Description File",
        "# Columns = Index, Red, Green, Blue, Visibility, Opacity, Label Name",
    ]

    for name, index in labels.items():
        color = get_color(index, total_labels)
        visibility = 0 if index == 0 else 1
        opacity = 0 if index == 0 else 1
        line = f'{index:<2} {color[0]:<3} {color[1]:<3} {color[2]:<3}    {visibility} {visibility} {opacity}    "{name}"'
        lines.append(line)

    with open(output_file, "w") as f:
        for line in lines:
            f.write(line + "\n")



def run_comparison_segmentation_itk_snap(path_seg, path_pred, case, labels=None):
    from audit.utils.sequences.sequences import read_sequences_dict

    verification_check = True
    t1 = f"{path_seg}/{case}/{case}_t1.nii.gz"
    t1ce = f"{path_seg}/{case}/{case}_t1ce.nii.gz"
    t2 = f"{path_seg}/{case}/{case}_t2.nii.gz"
    flair = f"{path_seg}/{case}/{case}_flair.nii.gz"
    seg = f"{path_seg}/{case}/{case}_seg.nii.gz"
    seg_ai = f"{path_pred}/{case}/{case}_pred.nii.gz"

    if labels:
        labels_path = "./src/audit/configs/itk_labels.txt"
        generate_itk_labels(labels, labels_path)
        command = open_itk_command() + ["-g", t1ce, "-s", seg, "-o", t1, t2, flair, seg_ai, "-l", labels_path]
    else:
        command = open_itk_command() + ["-g", t1ce, "-s", seg, "-o", t1, t2, flair, seg_ai] + [seg_ai]

    # Checking if both path exist
    if os.path.exists(t1ce) and os.path.exists(seg):
        subprocess.run(command)
    else:
        verification_check = False

    return verification_check


def check_operative_system():
    return platform.system()


def open_itk_command():
    op_sys = check_operative_system()

    if op_sys == "Darwin":  # macOS
        open_itk_command = ["open", "-n", "-a", "ITK-SNAP", "--args"]
    elif op_sys == "Linux":  # Linux/Ubuntu
        open_itk_command = ["itksnap"]
    else:
        raise OSError("Unsupported Operating System")

    return open_itk_command