import os
import time
import random
import json
import click
from utils import *
from gesture_prediction import GesturePrediction

# TODO: handle relative paths. Here the assumption is that the code is being run from the root directory of app
# Solution: https://click.palletsprojects.com/en/7.x/utils/#finding-application-folders (need to verify on other systems)
app_dir = click.get_app_dir("gesture_app")
CONFIG_DIR_PATH = app_dir + "/config/"
USER_PREFIX = "user."
ACTION_PREFIX = "action."
GESTURE_PREFIX = "gesture."
MAP_PREFIX = "map."


def build_settings_option_class(settings_instance):
    def set_default(default_name):
        class Cls(click.Option):
            def __init__(self, *args, **kwargs):
                kwargs['default'] = getattr(settings_instance, default_name)
                super(Cls, self).__init__(*args, **kwargs)

            def handle_parse_result(self, ctx, opts, args):
                obj = ctx.find_object(type(settings_instance))
                if obj is None:
                    ctx.obj = settings_instance
                return super(Cls, self).handle_parse_result(ctx, opts, args)

        return Cls

    return set_default


# click.pass_context is a way of using the Click context to pass parameters between commands, like username in our case
class Setting(object):
    def __init__(self):
        self.verbose = False
        self.name = "User"
        self.password = ""
        self.hsv_thresholds = None


settings = Setting()
settings_option_cls = build_settings_option_class(settings)
pass_setting = click.make_pass_decorator(Setting, ensure=True)


@click.group("gesture-app")
@click.version_option("0.1.0")
@click.option('--verbose', is_flag=True)
@pass_setting
def cli(ctx, verbose, *args, **kwargs):
    """the app to make your life easy by identifying hand getsures"""
    if verbose:
        click.echo("We are in verbose mode")
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    if not os.path.exists(CONFIG_DIR_PATH):
        os.makedirs(CONFIG_DIR_PATH)
    ctx.name = getConfig(USER_PREFIX + "name")
    ctx.password = getConfig(USER_PREFIX + "password")
    # print("Context values:" + " " + str(ctx.sname) + " "+ str(ctx.password))


# settings_option_cls can be used here to set any default values using the Settting class, in which case the user can simply press enter
# Ref: https://stackoverflow.com/questions/49511933/better-usage-of-make-pass-decorator-in-python-click
@cli.command()
@click.option('-u', '--name', cls=settings_option_cls('name'), prompt='Please enter your name', help='App user.',
              type=str)
@click.option('-p', '--password', prompt='Password', help='Password.', hide_input=True, confirmation_prompt=True)
@pass_setting
def register(ctx, name, password):
    """Register personalised user data"""
    click.echo('Hello %s!' % name)
    addConfig(USER_PREFIX + 'name', name)
    addConfig(USER_PREFIX + 'password', password)

    files = list(range(0, 5))
    # https://click.palletsprojects.com/en/7.x/utils/#showing-progress-bars
    with click.progressbar(files, label='Registering the user....', ) as bar:
        for file in bar:
            time.sleep(random.random())

    # add https://click.palletsprojects.com/en/7.x/utils/#getting-characters-from-terminal if required

    # record color and generate hsv here.
    hsv_thresholds = [[0, 0, 0], [1, 1, 1]]
    addConfig('config.hsv', json.dumps(hsv_thresholds))
    click.echo(f"User '{name}' registered successfully!")


@cli.command()
@pass_setting
def start(ctx):
    """Starts the application in the background"""
    if(checkIfUserValid(ctx.name)):
        click.echo('Please register first.')
        exit(1)
    click.echo('Starting.....')
    predictor = GesturePrediction()
    predictor.live_video()
    click.echo('Application started successfully.')

@cli.command()
@pass_setting
def showactions(ctx):
    """Displays different actions configured"""
    if (checkIfUserValid(ctx.name)):
        click.echo('Please register first.')
        exit(1)
    click.echo('Displaying all registered actions for user: ' + ctx.name)
    printSectionConfig(ACTION_PREFIX)


@cli.command()
@click.option('-a', 'actionName', help='Action Name', required=True, type=str)
@click.option('-s', 'shortcut', help='Keyboard shortcut for the action, separated by +', required=True, type=str)
@pass_setting
def addaction(ctx, actionName, shortcut):
    """Add an action with a name and keyboard shortcut which you want to trigger using hand gesture app"""
    if (checkIfUserValid(ctx.name)):
        click.echo('Please register first.')
        exit(1)
    click.echo('Adding action with name:{} and command:{}'.format(actionName, shortcut))
    # TODO: how to handle cross platform keys: Mac / Windows
    key = ACTION_PREFIX + actionName
    addConfig(key, shortcut)
    click.echo('Action %s added.' % actionName)


@cli.command()
@pass_setting
def showgestures(ctx):
    """Displays different gestures configured"""
    if checkIfUserValid(ctx.name):
        click.echo('Please register first.')
        exit(1)
    click.echo('Displaying all registered gestures for user: ' + ctx.name)
    printSectionConfig(GESTURE_PREFIX)


@cli.command()
@click.option('-g', 'gestureName', help='Gesture Name', required=True, type=str)
@pass_setting
def addgesture(ctx, gestureName):
    """Configure a hand gesture in the app"""
    if checkIfUserValid(ctx.name):
        click.echo('Please register first.')
        exit(1)
    click.echo('Adding gesture with name:{}'.format(actionName))
    # TODO: trigger model train here, and add a corresponding identifier (id) which will be used to identify this gesture in ML model
    key = GESTURE_PREFIX + gestureName
    #  addConfig(key, id)
    click.echo('Gesture %s added.' % gestureName)


@cli.command()
@click.option('-a', 'actionName', help='Action Name', required=True, type=str)
@click.option('-g', 'gestureName', help='Gesture Name', required=True, type=str)
@pass_setting
def mapActionWithGesture(ctx, actionName, gestureName):
    """Map a configured action with a gesture configured with the app."""
    if checkIfUserValid(ctx.name):
        click.echo('Please register first.')
        exit(1)
    key = MAP_PREFIX + actionName
    addConfig(key, gestureName)
    click.echo('Mapping Complete!')


@cli.command()
def start():
    """Starts the app"""
    predictor = GesturePrediction()
    predictor.live_video()


if __name__ == "__main__":
    cli()
