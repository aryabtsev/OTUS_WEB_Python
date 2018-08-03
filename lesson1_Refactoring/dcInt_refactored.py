import ast
import os
import collections

from nltk import pos_tag


def flat(list_with_tuples):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""

    return sum([list(item) for item in list_with_tuples], [])


def is_verb(word):

    if not word:
        return False
    pos_info = pos_tag([word])

    return pos_info[0][1] == 'VB'


def get_filename_path(path):
    '''принимает на вход путь -> список путей до каждого из .py файлов'''
    pathways = []

    for dirname, dirs, files in os.walk(path, topdown=True):
        for file in files:
            if file.endswith('.py'):
                pathways.append(os.path.join(dirname, file))
                if len(pathways) == 100:
                    break

    print('total %s files' % len(pathways))
    return pathways


def generate_trees(pathways, with_filenames=False, with_file_content=False):

    trees = []

    for filename in pathways:
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

    return trees


def get_all_names(tree):

    return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]


def get_verbs_from_function_name(function_name):

    return [word for word in function_name.split('_') if is_verb(word)]


def split_snake_case_name_to_words(name):

    return [n for n in name.split('_') if n]


def get_target_functions(node_names):
    '''возвращает все кроме служебных и магических методов'''

    return [f for f in node_names if not (f.startswith('__') and f.endswith('__'))]


def get_all_words_in_path(path):

    trees = generate_trees(path)
    names = flat([get_all_names(t) for t in trees])
    functions = get_target_functions(names)
    split_name = [split_snake_case_name_to_words(fnctn_name) for fnctn_name in functions]

    return flat(split_name)


def parse_node_names(trees):
    '''возвращает списком названия функций'''
    node_names = []
    for t in trees:
        node_names += [node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)]

    return node_names





def get_top_verbs_in_path(path, top_size=10):

    pathways = get_filename_path(path)
    trees = generate_trees(pathways)
    node_names = parse_node_names(trees)
    target_functions = get_target_functions(node_names)
    verbs = flat([get_verbs_from_function_name(function_name) for function_name in target_functions])

    return collections.Counter(verbs).most_common(top_size)


def get_top_functions_names_in_path(path, top_size=10):

    trees = generate_trees(path)
    node_names = parse_node_names(trees)
    target_functions = get_target_functions(node_names)

    return collections.Counter(target_functions).most_common(top_size)


if __name__ == '__main__':

    top_verbs = []
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
        top_verbs += get_top_verbs_in_path(path)

    top_size = 200
    print('total %s words, %s unique' % (len(top_verbs), len(set(top_verbs))))
    for word, occurence in collections.Counter(top_verbs).most_common(top_size):
        print(word, occurence)
