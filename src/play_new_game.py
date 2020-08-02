"""
Start a new game of Code Word
"""
from __future__ import print_function
import logging
from random import sample, shuffle
from alexa_responses import speech
from word_bank import QUESTIONS, CURRENT_PACK_ID, CURRENT_PACK_THEME, CURRENT_PACK
from strings import REPLAY_GAME_START, GAME_STARTING, NEW_PACK_MESSAGE


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def play_new_game(replay, player_info):
    """ Play new game intro and build question bank for the session """
    logger.debug("=====play_new_game fired...")
    logger.debug("=====Player Info: %s", player_info)

    if replay:
        new_game_message = REPLAY_GAME_START
    else:
        new_game_message = GAME_STARTING

    # Determine if the player needs to play the newest word pack or not.
    try:
        play_newest_word_pack = bool(
            int(player_info['lastWordPackPlayed']['N']) < CURRENT_PACK_ID)
    except KeyError as err:
        # If the lastWordPackPlayed key is missing we just set play_newest_word_pack to True.
        logger.debug(
            "=====caught KeyError looking for lastWordPackPlayed: %s", str(err))
        play_newest_word_pack = True
        # We also need to set the attribute
        player_info['lastWordPackPlayed'] = {'N': '0'}

    if play_newest_word_pack:
        new_game_message = NEW_PACK_MESSAGE + CURRENT_PACK_THEME + "... " + GAME_STARTING
        questions = get_newest_pack_questions(5)
    else:
        questions = pick_random_questions(5)

    speech_output = new_game_message + questions[0]['clues'][0]
    should_end_session = False
    attributes = {
        "questions": questions,
        "score": 0,
        "current_question_index": 0,
        "current_clue_index": 0,
        "game_length": len(questions),
        "game_status": "in_progress",
        "current_clue": questions[0]['clues'][0],
        "player_info": player_info,
        "play_newest_word_pack": play_newest_word_pack
    }
    return speech(speech_output, attributes, should_end_session, None)


def pick_random_questions(num_questions):
    """pick random questions from the bank to form the game"""
    print("=====pick_random_questions fired...")
    shuffle(QUESTIONS)
    questions = sample(list(QUESTIONS), k=num_questions)

    # shuffle up the clues so customers don't
    # hear the same order everytime
    for question in questions:
        shuffle(question['clues'])
        # truncate to 5 clues only to give some variation
        del question['clues'][5:]

    shuffle(questions)
    return questions


def get_newest_pack_questions(num_questions):
    """pick questions from the current pack to form the game"""
    print("=====get_pack_questions fired...")
    shuffle(CURRENT_PACK)
    questions = sample(list(CURRENT_PACK), k=num_questions)

    # shuffle up the clues so customers don't
    # hear the same order everytime
    for question in questions:
        shuffle(question['clues'])
        # truncate to 5 clues only to give some variation
        del question['clues'][5:]

    shuffle(questions)
    return questions
