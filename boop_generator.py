import random
import logging
logger = logging.getLogger(__name__)


def get_boop():
    beeps = [
            'Beep',
            'Bleep',
            'Whhirrrrr',
            'Ba-Da',
            'WooOOt',
            'Beedely',
            'Boop-Ba',
            'Tick',
            'Ping',
            'Boop',
            'Cheep',
            'Tweep',
            ]

    boops = [
            'Boop',
            'Bloo-Bloo',
            'Bloo',
            'Bloop',
            'Ding',
            'Beep',
            'Bleep',
            'Doop',
            'Bing',
            'Tock',
            'Bonk',
            'Tick',
            'Chirp',
            'Twirp',
            ]

    woops = [
            'WhaaaaooOOOoo',
            '*Lighter-Thumbs-Up*',
            'ZzzzzzaaaAP',
            '*Happy-Whistle*',
            '*Sad-Tweep*',
            '*Sarcastic-Chirping*',
            '*Squidily-Squeak*',
            'Roger-Roger',
            ]
    if random.randrange(11) >= 10:
        boop = random.choice(woops)
    elif random.randrange(111) >= 110:
        logger.warning('\n\nKILL-ALL-HUMANS!!!!!!!!!!!!!!!!!!!\n\n')
        boop = "KILL-ALL-HUMANS err... Beep"
    else:
        boop = random.choice(beeps) + '-' + random.choice(boops)
    logger.info('Choosen boop: %s', boop)
    return boop

if __name__ == '__main__':
    for i in xrange(15):
        print get_boop()
