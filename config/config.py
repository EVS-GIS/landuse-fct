#!/usr/bin/python
from configparser import ConfigParser


def db_config(filename='config/config.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

def paths_config(filename='config/config.ini', section='paths'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section
    paths = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            paths[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return paths

def parameters_config(filename='config/config.ini', section='parameters'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section
    parameters = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            if param[0] == 'landcover_tables':
                parameters[param[0]] = param[1].replace(' ','').split(',')
            elif param[0] == 'tile_size':
                parameters[param[0]] = float(param[1])
            elif param[0] == 'resolution' or param[0] == 'processes':
                parameters[param[0]] = int(param[1])
            else:
                parameters[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return parameters