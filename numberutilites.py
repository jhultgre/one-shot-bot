from num2words import num2words
import logging

logger = logging.getLogger(__name__)


def number_to_text(num):
    logger.debug('number to text')
    if type(num) is 'string' and '.' in num:
        raise Exception("Decimal number")
    return num2words(int(num)).replace('-', ' ').replace(' and ', ' ').title()


def text_to_number(textnum, numwords={}):
    '''
    from stack overflow
    http://stackoverflow.com/questions/493174/is-there-a-way-to-convert-number-words-to-integers-python

    '''
    logger.debug('text to number')
    if not numwords:
        units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
        ]

        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

        scales = ["hundred", "thousand", "million", "billion", "trillion"]

        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):    numwords[word] = (1, idx)
        for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    textnum = textnum.lower()
    for word in textnum.split():
        if word not in numwords:
            raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current
