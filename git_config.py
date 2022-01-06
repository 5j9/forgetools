from configparser import ConfigParser

from commons import DATAFILES, HOME


def main():
    updates = ConfigParser()
    with open(DATAFILES + '.gitconfig', encoding='utf8') as f:
        updates.read_file(f)

    home_config = ConfigParser()
    with open(HOME + '.gitconfig', 'a+', encoding='utf8') as f:
        f.seek(0)
        home_config.read_file(f)
        f.seek(0)
        home_config.update(updates)
        f.truncate()
        home_config.write(f)


if __name__ == '__main__':
    main()
