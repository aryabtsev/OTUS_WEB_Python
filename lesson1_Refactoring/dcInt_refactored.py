import ast
import os
import collections

from nltk import pos_tag


def flat(_list):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in _list], [])


def is_verb(word):

    if not word:
        return False
    pos_info = pos_tag([word])
    return pos_info[0][1] == 'VB'


def get_filenames(path):

    filenames = []

    for dirname, dirs, files in os.walk(path, topdown=True):
        for file in files:
            if file.endswith('.py'):
                filenames.append(os.path.join(dirname, file))
                if len(filenames) == 100:
                    break

    print('total %s files' % len(filenames))
    return filenames


def get_trees(filenames, with_filenames=False, with_file_content=False):

    trees = []

    for filename in filenames:
        with open(filename, 'r', encoding='utf-8') as attempt_handler:
            main_file_content = attempt_handler.read()

        try:
            tree = ast.parse(main_file_content)
        except SyntaxError as e:
            print(e)
            tree = None

        if with_filenames:
            if with_file_content:
                trees.append((filename, main_file_content, tree))
            else:
                trees.append((filename, tree))
        else:
            trees.append(tree)
    print(trees)
    return trees


def get_all_names(tree):

    return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]


def get_verbs_from_function_name(function_name):

    return [word for word in function_name.split('_') if is_verb(word)]


def split_snake_case_name_to_words(name):

    return [n for n in name.split('_') if n]


def get_all_words_in_path(path):

    trees = [t for t in get_trees(path) if t]
    names = flat([get_all_names(t) for t in trees])
    functions = [f for f in names if not (f.startswith('__') and f.endswith('__'))]
    split_name = [split_snake_case_name_to_words(fnctn_name) for fnctn_name in functions]
    return flat(split_name)


def get_top_verbs_in_path(path, top_size=10):

    filenames = get_filenames(path)
    trees = [t for t in get_trees(filenames) if t]
    node_names = []

    for t in trees:
        node_names += [node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)]

    target_funnames = [f for f in node_names if not (f.startswith('__') and f.endswith('__'))]
    verbs = flat([get_verbs_from_function_name(fname) for fname in target_funnames])

    return collections.Counter(verbs).most_common(top_size)


def get_top_functions_names_in_path(path, top_size=10):

    trees = get_trees(path)
    nodes = [ast.walk(t) for t in trees]
    node_names = [node.name.lower() for node in nodes if isinstance(node, ast.FunctionDef)]
    fnames = [f for f in flat(node_names) if not (f.startswith('__') and f.endswith('__'))]

    return collections.Counter(fnames).most_common(top_size)


wds = []
projects = [
    'django',
    'flask',
    'pyramid',
    'reddit',
    'requests',
    'sqlalchemy',
]

for project in projects:
    path = os.path.join('.', project)
    wds += get_top_verbs_in_path(path)

top_size = 200
print('total %s words, %s unique' % (len(wds), len(set(wds))))
for word, occurence in collections.Counter(wds).most_common(top_size):
    print(word, occurence)
