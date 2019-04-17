import os


def get_data_path():
    cwd = os.getcwd()
    main_directory = os.path.abspath(os.path.join(cwd, os.pardir, os.pardir))
    data_path = os.path.join(main_directory, "DATA", "HSS")
    return data_path


def get_data_path_sss():
    cwd = os.getcwd()
    main_directory = os.path.abspath(os.path.join(cwd, os.pardir, os.pardir))
    data_path = os.path.join(main_directory, "DATA", "SSS")
    return data_path
