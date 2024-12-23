import base64

from colorama import Fore
from colorama import Style
from loguru import logger
from tqdm import tqdm


def add_prefix_dict(dictionary: dict, prefix: str) -> dict:
    """
    Adds a specified prefix to all keys in a dictionary.

    Args:
        dictionary: The input dictionary whose keys will be prefixed.
        prefix: The prefix string to add to each key.

    Returns:
        dict: A new dictionary with prefixed keys and the original values.
    """
    return {f"{prefix}{k}": v for k, v in dictionary.items()}


def capitalizer(text: str) -> str:
    """
    Converts all characters in a given string to uppercase.

    Args:
        text: The input string to be converted.

    Returns:
        str: The input string with all characters in uppercase.
    """
    return text.upper()


def pretty_string(s: str, splitting_pattern: str = "_") -> str:
    """
    Converts a given string from a delimited format to a more readable format by capitalizing each word and joining them
     with spaces.

    Args:
        s: The input string to be prettified.
        splitting_pattern: The pattern used to split the string into words. Defaults to an underscore ('_').

    Returns:
        str: The prettified string with each word capitalized and joined by spaces.
    """
    # Split the string by the corresponding pattern
    words = s.split(splitting_pattern)

    # Capitalize the first letter of each word
    transformed_words = [word.capitalize() for word in words]

    # Join the words with a space
    output = " ".join(transformed_words)

    return output


def snake_case(s: str, splitting_pattern: str = " ") -> str:
    """
    Converts a given string to snake_case format by splitting based on a specified pattern,  converting all words to
    lowercase, and joining them with underscores.

    Args:
        s: The input string to be converted to snake_case.
        splitting_pattern: The pattern used to split the string into words. Defaults to a space (' ').

    Returns:
        str: The transformed string in snake_case format.
    """
    # Split the string by spaces
    words = s.split(splitting_pattern)

    # Convert each word to lowercase
    transformed_words = [word.lower() for word in words]

    # Join the words with underscores
    result = "_".join(transformed_words)

    return result


def fancy_tqdm(**kwargs):
    """
    Creates a custom progress bar using `tqdm` with a fancy color format.
    """
    bar_format = "{l_bar}%s{bar}%s{r_bar}" % (Fore.LIGHTBLUE_EX, Fore.CYAN)
    return tqdm(bar_format=bar_format, **kwargs)


def fancy_print(message, color=Fore.WHITE, symbol="•"):
    """
    Prints a message to the console with a custom symbol and color.
    """

    print(f" {color}{symbol}{message}{Style.RESET_ALL}")


def img_to_base64(image_path: str) -> str:
    """
     Converts an image to a base64-encoded string.

     Args:
         image_path: The file path of the image to be converted.

     Returns:
         str: A base64-encoded string representation of the image.
     """
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def configure_logging(log_filename: str):
    logger.add(log_filename, retention="90 days", level="INFO")
