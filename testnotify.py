from pync import Notifier
import os

# Notifier.notify('Hello World')
Notifier.notify('Hello World', subtitle='test test test', group='oneshot',appIcon='test_files/oneshotlogo.png',contentImage='test_files/oneshotlogo.png')
# Notifier.notify('Hello World', group=os.getpid())
# Notifier.notify('Hello World', activate='com.apple.Safari')
# Notifier.notify('Hello World', open='http://github.com/')
# Notifier.notify('Hello World', execute='say "OMG"')

Notifier.remove('oneshot')

# Notifier.list(os.getpid())