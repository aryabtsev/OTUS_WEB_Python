from nltk import pos_tag


def flat(list_with_tuples):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""

    return sum([list(item) for item in list_with_tuples], [])


def is_verb(word):

    if not word:
        return False
    pos_info = pos_tag([word])

    return pos_info[0][1] == 'VB'


def is_number(string):

    return str(string).isdigit()