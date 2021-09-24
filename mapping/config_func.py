import configparser
import os
import pandas as pd

def get_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    return config


def get_setting(path, section, setting):
    config = get_config(path)
    value = config.get(section, setting)
    msg = "{section} {setting} is {value}".format(
        section=section, setting=setting, value=value)
    print(msg)
    return value


def update_setting(path, section, setting, value):
    config = get_config(path)
    config.set(section, setting, value)
    with open(path, "w") as config_file:
        config.write(config_file)


def delete_setting(path, section, setting):
    config = get_config(path)
    config.remove_option(section, setting)
    with open(path, "w") as config_file:
        config.write(config_file)


if __name__ == "__main__":
    path = 'C:\\Users\\Admin\\Desktop\\Работа\\FHIR_mapping\\settings.ini'
    path_fin = get_setting(path, 'Paths', 'path_fin')
    cardio = get_setting(path, 'Paths', 'cardio_db_path')
    cache = get_setting(path, 'Paths', 'cache_db_path')