"""
Start a new game
"""
from __future__ import print_function
import logging
from random import sample, shuffle
from alexa_responses import speech
from word_bank import WORDS, CURRENT_PACK_ID, CURRENT_PACK_THEME, CURRENT_PACK
from strings import REPLAY_GAME_START, GAME_STARTING, NEW_PACK_MESSAGE


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def play_new_game(this_game, replay=None):
    """ Play new game intro and build question bank for the session """
    logger.debug("=====play_new_game fired...")
    logger.debug("=====Player Info: %s", this_game.player_info)
    should_play_newest_word_pack = this_game.should_play_newest_word_pack(
        CURRENT_PACK_ID)
    questions = pick_random_questions(5, should_play_newest_word_pack)

    if replay:
        new_game_message = REPLAY_GAME_START
    else:
        new_game_message = GAME_STARTING

    if should_play_newest_word_pack:
        new_game_message = NEW_PACK_MESSAGE + CURRENT_PACK_THEME + "... " + GAME_STARTING

    speech_output = new_game_message + questions[0]['clues'][0]
    this_game.setup_new_game_attributes(
        questions, should_play_newest_word_pack)

    return speech(tts=speech_output,
                  attributes=this_game.attributes,
                  should_end_session=False)


def pick_random_questions(num_questions, should_play_newest_word_pack):
    """ Pick random questions from the bank to form the game """
    logger.debug("=====pick_random_questions fired...")
    if should_play_newest_word_pack:
        logger.debug("=====loading CURRENT_PACK...")
        content = CURRENT_PACK
    else:
        logger.debug("=====loads WORDS...")
        content = WORDS

    shuffle(content)
    questions = sample(list(content), k=num_questions)

    # Shuffle up the clues too so customers
    # don't hear the same order everytime.
    for question in questions:
        shuffle(question['clues'])
        # Truncate to 5 clues only to give some variation.
        del question['clues'][5:]

    shuffle(questions)
    return questions
