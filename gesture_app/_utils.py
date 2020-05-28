import click
import os
import configparser

app_dir = click.get_app_dir("gesture_app")
config_file = os.path.join(app_dir, "cfg")
config = configparser.ConfigParser()


def checkIfUserValid(name):
    if (name is None or name == ""):
        return True
    return False


def addConfig(key, value):
    """Set global configuration for this app."""
    config.read(config_file)
    section, key = key.split(".")
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, key, value)
    with open(config_file, "w") as configfile:
        config.write(configfile)


def getConfig(key):
    """Get global configuration for this app."""
    config.read(config_file)
    section, key = key.split(".")
    if not config.has_section(section):
        return None
    try:
        return config.get(section, key)
    except KeyError:
        return None
    except configparser.NoOptionError:
        return None


def printSectionConfig(section_name):
    section_name = section_name[:-1]
    config.read(config_file)
    try:
        for name, value in config.items(section_name):
            click.echo('  %s = %s' % (name, value))
    except configparser.NoSectionError:
        click.echo('No such configuration exists.')

if __name__ == '__main__':
    print(app_dir)