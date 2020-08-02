"""
Code Word Strings
"""
WELCOME_BACK_MESSAGE_1 = """
<amazon:emotion name="excited" intensity="medium">
Hey there, welcome back to Code Word!
</amazon:emotion>
<amazon:emotion name="excited" intensity="low">
You've earned a grand total of {} points playing. Nice! Do you need a refresher on the rules of the game?
</amazon:emotion>
"""

WELCOME_BACK_MESSAGE_2 = """
<amazon:emotion name="excited" intensity="medium">
Look who's back for more code words! 
</amazon:emotion>
<amazon:emotion name="excited" intensity="low">
Last time you played you earned {} points. Let's see what you can do this game! Do you need to hear the rules?
</amazon:emotion>
"""

WELCOME_BACK_MESSAGE_PERSONALIZED_1 = """
<amazon:emotion name="excited" intensity="medium">
Hey <alexa:name type="first" personId="{}"/>, welcome back to Code Word! 
</amazon:emotion>
<amazon:emotion name="excited" intensity="low">
You've earned a grand total of {} points playing. Nice! Do you need a refresher on the rules of the game?
</amazon:emotion>
"""

WELCOME_BACK_MESSAGE_PERSONALIZED_2 = """
<amazon:emotion name="excited" intensity="medium">
Look who's back for more code words it's <alexa:name type="first" personId="{}"/>! 
</amazon:emotion>
<amazon:emotion name="excited" intensity="low">
Last time you played you earned {} points. Let's see what you can do this game! Do you need to hear the rules?
</amazon:emotion>
"""

WELCOME_BACK_MESSAGE_OPPONENT_1 = """
<amazon:emotion name="excited" intensity="medium">
Welcome back to Code Word <alexa:name type="first" personId="{}"/>! 
</amazon:emotion>
<amazon:emotion name="excited" intensity="low">
Hope you brought your A game today to beat <alexa:name type="first" personId="{}"/>'s recent score of {}.
Do you need me to remind you of the rules before we start the game?
</amazon:emotion>
"""

WELCOME_BACK_MESSAGE_OPPONENT_2 = """
<amazon:emotion name="excited" intensity="medium">
<alexa:name type="first" personId="{}"/> is in the house and ready for more Code Word! 
</amazon:emotion>
<amazon:emotion name="excited" intensity="low">
Make sure you brag about your score to <alexa:name type="first" personId="{}"/> today.
Do you need a reminder on how to play the game?
</amazon:emotion>
"""

NEW_PACK_MESSAGE = """
<amazon:emotion name="excited" intensity="medium">
Great news, I've got some new code words for you to try and crack!
</amazon:emotion>
<amazon:emotion name="excited" intensity="low">
The theme or category for this game will be...
</amazon:emotion>
"""

REPLAY_GAME_START = """
<amazon:emotion name="excited" intensity="high">
Woohoo let's play again!
</amazon:emotion>
<amazon:emotion name="excited" intensity="low">
Get ready, next game starting in... 3... 2... 1... "
</amazon:emotion>
"""

HELP_MESSAGE = """
<prosody rate="90%">
Code Word is played in five rounds.
Each round, I'll give you a series of clues and it's your job to figure out what word is related to the clues.
After each clue, you get a chance to guess the code word, or you can ask for the next clue if you're stumped. 
The faster you figure out the code word, the more points you earn! 
For extra fun, use the Voice Profiles feature of Alexa to compete against everyone in your house. 
New code words are being added all the time so check back often.
</prosody>
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

FIRST_GAME_MESSAGE = "<amazon:emotion name=\"excited\" intensity=\"high\">" +\
    "Welcome to Code Word!</amazon:emotion> " + \
    HELP_MESSAGE + \
    " Do you need to hear the rules again before we get started?"

NEXT_CLUE = """
<amazon:emotion name="excited" intensity="low">
The next clue is...
</amazon:emotion>
"""

WRONG_ANSWER_CLUES_REMAIN = "<amazon:emotion name=\"excited\" intensity=\"low\">" +\
    "Good guess, but that's not the Code Word!</amazon:emotion> " + \
    NEXT_CLUE

WELCOME_REPROMPT = "Do you need to hear the rules for the game again?"

STANDARD_EXIT_MESSAGE = """
<amazon:emotion name="excited" intensity="medium">
Thanks for playing Code Word!
</amazon:emotion>
"""

EXIT_WITH_REVIEW_REQUEST = """
<amazon:emotion name="excited" intensity="medium">
Thanks for playing Code Word!
If you had fun, please leave a 5 star review to support the developer."
</amazon:emotion>
"""
