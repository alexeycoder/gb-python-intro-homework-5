def to_superscripted_digit(digit: int) -> str:
    match digit:
        case 1:
            return '\u00b9'
        case 2:
            return '\u00b2'
        case 3:
            return '\u00b3'
        case 4:
            return '\u2074'
        case 5:
            return '\u2075'
        case 6:
            return '\u2076'
        case 7:
            return '\u2077'
        case 8:
            return '\u2078'
        case 9:
            return '\u2079'
        case 0:
            return '\u2070'
    return ''


def to_superscripted_number(num: int) -> str:
    negative = num < 0
    if negative:
        num = -num

    result = ''
    while num > 0:
        digit = num % 10
        result = to_superscripted_digit(digit) + result
        num //= 10

    if negative:
        result = "-" + result

    return result
