import os
import time
import random
import json
import click
from gesture_app import GESTURE_APP_HOME
from gesture_app._utils import checkIfUserValid, addConfig, getConfig, printSectionConfig
from gesture_app.model.gesture_prediction import GesturePrediction

# TODO: handle relative paths. Here the assumption is that the code is being run from the root directory of app
# Solution: https://click.palletsprojects.com/en/7.x/utils/#finding-application-folders (need to verify on other systems)
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
        self.hsv_thresholds = None
        # passing default actions and gestures
        self.gestures = ['high_five']
        self.actions = [{'actionName': 'screenshot', 'action': 'cmd+shift+3'}]


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
    ctx.name = getConfig(USER_PREFIX + "name")
    # print("Context values:" + " " + str(ctx.sname) + " "+ str(ctx.password))


# settings_option_cls can be used here to set any default values using the Settting class, in which case the user can simply press enter
# Ref: https://stackoverflow.com/questions/49511933/better-usage-of-make-pass-decorator-in-python-click
@cli.command()
@click.option('-u', '--name', cls=settings_option_cls('name'), prompt='Please enter your name', help='App user.',
              type=str)
@pass_setting
def register(ctx, name):
    """Register personalised user data"""
    click.echo('Hello %s!' % name)
    addConfig(USER_PREFIX + 'name', name)

    files = list(range(0, 5))
    # https://click.palletsprojects.com/en/7.x/utils/#showing-progress-bars
    with click.progressbar(files, label='Registering the user....', ) as bar:
        for file in bar:
            time.sleep(random.random())

    # adding default actions during registration, user can change them by using commands later
    for gesture in ctx.gestures:
        key = GESTURE_PREFIX + gesture
        addConfig(key, key)
        click.echo(f"Gesture {gesture} is added by default")
    for action in ctx.actions:
        key = ACTION_PREFIX + action['actionName']
        addConfig(key, action['action'])
        click.echo(f"Action {action['actionName']} is added by default")
    for itr in range(len(ctx.gestures)):
        key = MAP_PREFIX + ctx.gestures[itr]
        addConfig(key, ctx.actions[itr]['actionName'])
        click.echo(f"{ctx.gestures[itr]} mapped to {ctx.actions[itr]['actionName']} by default")

    click.echo(f"User '{name}' registered successfully!")


@cli.command()
@pass_setting
def start(ctx):
    """Starts the application in the background"""
    if(checkIfUserValid(ctx.name)):
        click.echo('Please register first.')
        exit(1)
    click.echo('Starting.....')
    action_name = getConfig(MAP_PREFIX+ctx.gestures[0])
    keyboard_command = getConfig(ACTION_PREFIX+action_name)
    predictor = GesturePrediction(keyboard_command)
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
    click.echo('Adding gesture with name:{}'.format(gestureName))
    # TODO: trigger model train here, and add a corresponding identifier (id) which will be used to identify this gesture in ML model
    key = GESTURE_PREFIX + gestureName
    addConfig(key, key)
    click.echo(f'Gesture {gestureName} added.')


@cli.command()
@click.option('-a', 'actionName', help='Action Name', required=True, type=str)
@click.option('-g', 'gestureName', help='Gesture Name', required=True, type=str)
@pass_setting
def mapActionWithGesture(ctx, actionName, gestureName):
    """Map a configured action with a gesture configured with the app."""
    if checkIfUserValid(ctx.name):
        click.echo('Please register first.')
        exit(1)
    key = MAP_PREFIX + gestureName
    addConfig(key, actionName)
    click.echo('Mapping Complete!')


if __name__ == "__main__":
    cli()
