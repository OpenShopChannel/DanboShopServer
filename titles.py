import string
from enum import Enum

"""A character range from A -> Z, a -> z, and 0 -> 9."""
CHAR_RANGE = string.ascii_uppercase + string.ascii_lowercase + string.digits
RANGE_LENGTH = len(CHAR_RANGE)


class TitleType(Enum):
    """Represents the upper byte for a given title ID."""
    SD = 'S'
    NAND = 'H'
    FORWARDER = 'O'


class TitlesExhaustedError(Exception):
    """This error denotes that titles for the given category have been exhausted."""
    pass


def get_char(index: int) -> str:
    """Returns the character for the given index. If zero, assumes A."""
    return CHAR_RANGE[index]


def get_title_category(title_type: TitleType) -> str:
    """Returns the upper title category for the title ID.

    At present, this assumes 00010001 for any non-SD title.
    If the title is SD, it's assumed to be 00010008."""

    if title_type == TitleType.SD:
        return '00010008'
    else:
        return '00010001'


def generate_title_id(title_type: TitleType, amount: int) -> str:
    """Generates a lower title ID.

    Given an iteration amount, increments from <type>AAA
    to that of the passed iteration. For example, with a title
    type of NAND and amount of 52, HAAA iter 52 is HAAz.
    It then returns
    """
    type_byte: str = title_type.value

    # Begin stringing a title ID.
    title_id: str = type_byte

    # Our amount should be minus one so that 1 -> AAA.
    amount -= 1

    # Ensure we are not exceeding our maximum amount.
    if amount > (RANGE_LENGTH ** 3):
        raise TitlesExhaustedError

    # We can determine the amount of characters by dividing
    # by our length exponentially.
    # For example, we start by dividing by 3844 (62 ** 2) in order
    # to determine the iteration for our third character.
    # We then divide by 62 (62 ** 1).
    # Lastly, we divide 1 with our remainder alone,
    # determining the last character's index.
    for offset in reversed(range(3)):
        index = amount // (RANGE_LENGTH ** offset)
        if index:
            # Use the remainder of this operation for the next amount.
            amount = amount % (RANGE_LENGTH ** offset)

        # Add this character's index to our title ID.
        title_id += get_char(index)

    # Encode the title's characters to hexadecimal.
    hex_title_id = bytes(title_id, 'ascii').hex()
    return hex_title_id


def get_title_id(title_type: TitleType, app_id: int) -> str:
    """Returns a predictable title ID for an application type and ID."""

    title_upper = get_title_category(title_type)
    title_lower = generate_title_id(title_type, app_id)
    return title_upper + title_lower
