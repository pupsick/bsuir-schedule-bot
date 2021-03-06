from json import load


def read_locale(filename="ru.json"):
    with open(file=filename, encoding="UTF-8") as file:
        return load(file)


def read_lesson_template(locale):
    return locale['lesson_template']


def read_subgroup_template(locale):
    return locale['subgroup_template']


def read_prefix(locale):
    return locale['prefix']


def read_cabinet_template(locale):
    return locale['cabinet_template']


def read_lesson_types(locale):
    return locale['lesson_types']


def read_nothing(locale):
    return locale['nope']


def read_buildings(locale):
    return locale['buildings']