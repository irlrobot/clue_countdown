"""
Strings
"""
import random


WELCOME_BACK_1 = """
<amazon:emotion name="excited" intensity="medium">
Hey there, welcome back to Clue Countdown!
</amazon:emotion>
<amazon:emotion name="excited" intensity="low">
You've earned a grand total of {} points playing. Nice! Do you need a refresher on the rules of the game?
</amazon:emotion>
"""

WELCOME_BACK_2 = """
<amazon:emotion name="excited" intensity="medium">
Look who's back for more Clue Countdown! 
</amazon:emotion>
<amazon:emotion name="excited" intensity="low">
Last time you played you earned {} points. Let's see what you can do this game! Do you need to hear the rules?
</amazon:emotion>
"""

WELCOME_BACK_PERSONALIZED_1 = """
<amazon:emotion name="excited" intensity="medium">
Hey <alexa:name type="first" personId="{}"/>, welcome back to Clue Countdown! 
</amazon:emotion>
<amazon:emotion name="excited" intensity="low">
You've earned a grand total of {} points playing. Nice! Do you need a refresher on the rules of the game?
</amazon:emotion>
"""

WELCOME_BACK_PERSONALIZED_2 = """
<amazon:emotion name="excited" intensity="medium">
Look who's back for more Clue Countdown it's <alexa:name type="first" personId="{}"/>! 
</amazon:emotion>
<amazon:emotion name="excited" intensity="low">
Last time you played you earned {} points. Let's see what you can do this game! Do you need to hear the rules?
</amazon:emotion>
"""

WELCOME_BACK_OPPONENT_1 = """
<amazon:emotion name="excited" intensity="medium">
Welcome back to Clue Countdown <alexa:name type="first" personId="{}"/>! 
</amazon:emotion>
<amazon:emotion name="excited" intensity="low">
Hope you brought your A game today to beat <alexa:name type="first" personId="{}"/>'s recent score of {}.
Do you need me to remind you of the rules before we start the game?
</amazon:emotion>
"""

WELCOME_BACK_OPPONENT_2 = """
<amazon:emotion name="excited" intensity="medium">
<alexa:name type="first" personId="{}"/> is in the house and ready for more Clue Countdown! 
</amazon:emotion>
<amazon:emotion name="excited" intensity="low">
Make sure you brag about your score to <alexa:name type="first" personId="{}"/> today.
Do you need a reminder on how to play the game?
</amazon:emotion>
"""

NEW_PACK_MESSAGE = """
<amazon:emotion name="excited" intensity="medium">
Great news, I've got some new words and clues for you today!
</amazon:emotion>
<amazon:emotion name="excited" intensity="low">
The theme or category for this game will be...
</amazon:emotion>
"""

REPLAY_GAME_START = """
<amazon:emotion name="excited" intensity="high">
Woohoo more Clue Countdown coming right up!
</amazon:emotion>
<amazon:emotion name="excited" intensity="low">
Get ready, next game starting in... 3... 2... 1... "
</amazon:emotion>
"""

HELP_MESSAGE = """
<amazon:emotion name="excited" intensity="low">
<prosody rate="90%">
Clue Countdown is played over five rounds.
Each round, I'll give you a series of clues and it's your job to figure out what word is related.
After each clue, you'll get a chance to guess the word, or you can ask for the next clue if you're stumped. 
The less clues you need, the more points you earn - each clue after the first will cost you 10 points! 
</prosody>
For extra fun, use the Voice Profiles feature of Alexa to compete against everyone in your house. 
New words and clues are being added all the time so check back often.
</amazon:emotion>
"""

HELP_MESSAGE_BEFORE_GAME = HELP_MESSAGE + \
    " Do you need to hear the rules again?"

HELP_MESSAGE_DURING_GAME = HELP_MESSAGE + \
    " Ok, back to your current game. The last clue was... "

GAME_STARTING = """
<amazon:emotion name="excited" intensity="low">
Ok get ready, starting your game in... 
3... 2... 1...
The first clue is...
</amazon:emotion>
"""

FIRST_GAME = "<amazon:emotion name=\"excited\" intensity=\"high\">" +\
    "Thanks for playing Clue Countdown!</amazon:emotion> " + \
    HELP_MESSAGE + \
    " Do you need to hear the rules again before we get started?"

FIRST_GAME_PERSONALIZED = "<amazon:emotion name=\"excited\" intensity=\"high\">" +\
    "Thanks for playing Clue Countdown <alexa:name type=\"first\" personId=\"{}\"/>!" +\
    "</amazon:emotion> " + HELP_MESSAGE + \
    " Do you need to hear the rules again before we get started?"

NEXT_CLUE = """
<amazon:emotion name="excited" intensity="low">
The next clue is...
</amazon:emotion>
"""

WRONG_ANSWER_CLUES_REMAIN = "<amazon:emotion name=\"excited\" intensity=\"medium\">" +\
    "Good guess, but that's not the word I am thinking of!</amazon:emotion> " + \
    NEXT_CLUE

WELCOME_REPROMPT = "Do you need to hear the rules for the game again?"

STANDARD_EXIT_MESSAGE = """
<amazon:emotion name="excited" intensity="medium">
Thanks so much for playing Clue Countdown, see you next time!
</amazon:emotion>
"""

EXIT_WITH_REVIEW_REQUEST = """
<amazon:emotion name="excited" intensity="medium">
Thanks for playing Clue Countdown!
If you had fun playing, please leave a 5 star review to support the creator."
</amazon:emotion>
"""

WRONG_ANSWER = "<amazon:emotion name=\"excited\" intensity=\"low\">" +\
    "Nope! The word was {}.</amazon:emotion>"

END_GAME_WRAP_UP = """
<amazon:emotion name="excited" intensity="medium">
Wow, nice job! You got {} points. Would you like to play Clue Countdown again?"
</amazon:emotion>
"""

NO_MORE_CLUES = """
<amazon:emotion name="excited" intensity="low">
I've already given you all the clues!  The last clue was: {}". What word am I thinking of?"
</amazon:emotion>
"""

NEXT_ROUND_WITH_CLUE = """
<amazon:emotion name="excited" intensity="medium">
Get ready.  Next round in 3... 2... 1...
</amazon:emotion>
{}
"""


def random_correct_answer_message(correct_answer):
    """ Return a random encouraging phrase for getting a right answer """
    phrases = [
        "Nailed it!",
        "Nice one!",
        "Great work!",
        "You got it!",
        "Woohoo nice job!",
        "You're amazing!",
        "Crushed it!"
    ]

    phrase = phrases[random.randint(0, len(phrases) - 1)]
    return """
    <amazon:emotion name="excited" intensity="high">
    {} 
    </amazon:emotion>
    <amazon:emotion name="excited" intensity="low">
    The word was {}.
    </amazon:emotion>
    """.format(phrase, correct_answer)
