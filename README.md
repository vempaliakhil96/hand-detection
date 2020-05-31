## hand-gesture-recognition

[![image](https://img.shields.io/pypi/pyversions/conference-radar.svg)](https://github.com/vempaliakhil96/hand-detection)

## Installation
You can simply use pip to install `hand-gesture-recognition`:

<pre>
$ pip install *INSERT*
</pre>

## Features
Currently we can use the high-five gesture to trigger any keyboard command, by default it is set to 
`cmd+shift+3` for Mac. Windows users might need to reconfigure this. Please refer API documentation
on how to use the various commands.

## How to use
This app currently detects 1 gesture i.e high-five. We can configure trigger diferent keyboard inputs to this
gesture.

###commands
####register
<pre>
gesture-app register
</pre>
Use this to register yourself as a user and save your custom keyboard actions 

####start
This commands starts the app with the present configuration, if no changes in app configurations have been made then
default configuration is used.
<pre>
gesture-app start
</pre>

####addaction
You can add keyboard actions like so. Note: These are not mapped to trigger when gesture is recognized, they are just saved
in config file for later use.\
`-a`: Name of the action\
`-s`: keyboard command
<pre>
gesture-app addaction -a "copy text" -s "cmd+shift+3"
</pre>

####showaction
To display all the actions that are currently present in config use the following
<pre>
gesture-app showactions
</pre>

####showgesture
You can use this to get gesture names that are currently present.
<pre>
gesture-app showgestures
</pre>
####mapActionWithGesture
`-a`: Name of the action\
`-g`:Name of gesture\
Please note that the action name should already be 
registered using the `addaction` command.
<pre>
gesture-app mapActionWithGesture -a "copy text" -g "high_five"
</pre>

## TroubleShooting
If there are any issues, please write to us at \
`meghajindal1997@gmail.com` \
`vempaliakhil96@gmail.com` 

## License
This project is licensed under the Apache License, 
see the [LICENSE](https://github.com/vempaliakhil96/hand-detection/blob/master/LICENSE) file for details.
