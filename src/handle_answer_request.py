"""
Handles the main flow of the game
"""
from __future__ import print_function
import logging
from fuzzywuzzy import fuzz
from alexa_responses import speech_with_card, speech
from manage_data import update_score_and_games, update_score_games_and_pack
from strings import (
    WRONG_ANSWER_CLUES_REMAIN, NEXT_CLUE, random_correct_answer_message,
    WRONG_ANSWER, END_GAME_WRAP_UP, NO_MORE_CLUES
)
from word_bank import CURRENT_PACK_ID


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def handle_answer_request(intent, session):
    """ Check if the answer is right, adjust score, and continue """
    logger.debug("=====handle_answer_request fired...")
    # Setup.
    attributes = {}
    answer = get_answer_from_intent(intent)
    questions = session['attributes']['questions']
    game_length = session['attributes']['game_length']
    current_score = session['attributes']['score']
    current_question_index = session['attributes']['current_question_index']
    current_clue_index = session['attributes']['current_clue_index']
    player_info = session['attributes']['player_info']
    play_newest_word_pack = session['attributes']['play_newest_word_pack']
    current_question_value = 50 - int((current_clue_index * 10))
    correct_answer = questions[current_question_index]['code_word'].lower()
    answered_correctly = None
    # Use Levenshtein distance algo to see if the words are similar enough.
    fuzzy_score = fuzz.partial_ratio(answer, correct_answer)

    # Currently using a hardcoded score of 60 or better.
    if correct_answer in answer or fuzzy_score >= 60:
        current_score += current_question_value
        answered_correctly = True
    else:
        log_wrong_answer(answer, correct_answer)
        answered_correctly = False
        # If clues remain give them the next clue instead of moving on.
        if current_clue_index != 4:
            return next_clue_request(session=session, was_wrong_answer=True)

    # If that was the last word end the game.
    if current_question_index == game_length - 1:
        if play_newest_word_pack:
            player_info['lastWordPackPlayed']['N'] = CURRENT_PACK_ID
        if answered_correctly:
            current_score += current_question_value
        return end_game_return_score(current_score, player_info, answered_correctly,
                                     answer, correct_answer, play_newest_word_pack)

    # If that wasn't the last word in the game continue on to next word.
    current_question_index += 1
    speech_output = "Get ready.  Next round in 3... 2... 1... " +\
        questions[current_question_index]['clues'][0]
    attributes = {
        "current_question_index": current_question_index,
        "current_clue_index": 0,
        "questions": questions,
        "score": current_score,
        "game_length": game_length,
        "game_status": "in_progress",
        "current_clue": questions[current_question_index]['clues'][0],
        "player_info": player_info,
        "play_newest_word_pack": play_newest_word_pack
    }

    if answered_correctly:
        speech_output = random_correct_answer_message(
            str(correct_answer)) + speech_output
        card_text = "The word was:  " + correct_answer + ". You got " + \
            str(current_question_value) + " points!"
        card_title = "You figured out the word!"
    else:
        speech_output = WRONG_ANSWER.format(
            str(correct_answer)) + speech_output
        card_text = "The word was:  " + correct_answer + "\n" + \
            "You said:  " + str(answer)
        card_title = "That wasn't the word!"

    return speech_with_card(tts=speech_output,
                            attributes=attributes,
                            should_end_session=False,
                            card_title=card_title,
                            card_text=card_text,
                            answered_correctly=answered_correctly)


def end_game_return_score(current_score, player_info, answered_correctly,
                          answer, correct_answer, play_newest_word_pack):
    """ If the customer answered the last question end the game """
    logger.debug("=====end_game_return_score fired...")
    wrap_up = END_GAME_WRAP_UP.format(str(current_score))

    if answered_correctly:
        speech_output = random_correct_answer_message(
            str(correct_answer)) + wrap_up
        card_text = "Your score is " + str(current_score) + " points!\n" + \
            "The last word was: " + correct_answer
    else:
        speech_output = WRONG_ANSWER.format(
            str(correct_answer)) + wrap_up
        card_text = "Your score is " + str(current_score) + " points!\n" + \
            "\nThe last word was: " + correct_answer + "\nYou said: " + answer

    customer_id = player_info['customerID']['S']
    new_lifetime_score = int(current_score) + \
        int(player_info['lifetimeScore']['N'])
    new_games_played = 1 + int(player_info['gamesPlayed']['N'])
    last_word_pack_played = player_info['lastWordPackPlayed']['N']
    should_end_session = False
    attributes = {
        "game_status": "ended",
        "player_info": {
            'customerID': {
                'S': customer_id
            },
            'lifetimeScore': {
                'N': str(new_lifetime_score)
            },
            'gamesPlayed': {
                'N': str(new_games_played)
            },
            'lastWordPackPlayed': {
                'N': str(last_word_pack_played)
            }
        }
    }

    if play_newest_word_pack:
        update_score_games_and_pack(customer_id, new_lifetime_score, new_games_played,
                                    last_word_pack_played, current_score)
    else:
        update_score_and_games(
            customer_id, new_lifetime_score, new_games_played, current_score)

    card_title = "Game Results"
    reprompt = "Would you like to play Words Plus Clues again?"
    return speech_with_card(speech_output, attributes, should_end_session,
                            card_title, card_text, answered_correctly, reprompt)


def next_clue_request(session=None, was_wrong_answer=None):
    """ Give player the next clue """
    logger.debug("=====next_clue_request fired...")
    attributes = {}
    game_questions = session['attributes']['questions']
    game_length = session['attributes']['game_length']
    current_score = session['attributes']['score']
    current_question_index = session['attributes']['current_question_index']
    current_clue_index = session['attributes']['current_clue_index']
    play_newest_word_pack = session['attributes']['play_newest_word_pack']
    current_clue = game_questions[current_question_index]['clues'][current_clue_index]
    should_end_session = False
    max_clues = len(game_questions[current_question_index]['clues']) - 1

    if current_clue_index < max_clues:
        current_clue_index += 1
        next_clue = game_questions[current_question_index]['clues'][current_clue_index]
        speech_output = NEXT_CLUE + next_clue
        if was_wrong_answer:
            speech_output = WRONG_ANSWER_CLUES_REMAIN + next_clue
    else:
        next_clue = current_clue
        speech_output = NO_MORE_CLUES.format(current_clue)

    attributes = {
        "current_question_index": current_question_index,
        "current_clue_index": current_clue_index,
        "questions": game_questions,
        "score": current_score,
        "game_length": game_length,
        "game_status": "in_progress",
        "current_clue": next_clue,
        "player_info": session['attributes']['player_info'],
        "play_newest_word_pack": play_newest_word_pack
    }

    return speech(speech_output, attributes, should_end_session, None)


def repeat_clue_request(session):
    """give player the last clue"""
    print("=====repeat_clue_request fired...")
    attributes = {}
    game_questions = session['attributes']['questions']
    game_length = session['attributes']['game_length']
    current_score = session['attributes']['score']
    current_question_index = session['attributes']['current_question_index']
    current_clue_index = session['attributes']['current_clue_index']
    play_newest_word_pack = session['attributes']['play_newest_word_pack']
    current_clue = game_questions[current_question_index]['clues'][current_clue_index]
    should_end_session = False
    speech_output = "The last clue was:  " + current_clue

    attributes = {
        "current_question_index": current_question_index,
        "current_clue_index": current_clue_index,
        "questions": game_questions,
        "score": current_score,
        "game_length": game_length,
        "game_status": "in_progress",
        "current_clue": current_clue,
        "player_info": session['attributes']['player_info'],
        "play_newest_word_pack": play_newest_word_pack
    }

    return speech(speech_output, attributes, should_end_session, None)


def log_wrong_answer(answer, correct_answer):
    """log all questions answered incorrectly so i can analyze later"""
    logger.debug("[WRONG ANSWER]:" + answer +
                 ". Correct answer: " + correct_answer)


def get_answer_from_intent(intent):
    """parse the request to get the answer Alexa heard"""
    logger.debug("=====get_answer_from_intent fired...")
    if 'slots' in intent:
        try:
            synonym = intent['slots']['CatchAllAnswer']['resolutions']['resolutionsPerAuthority'][0]
            # If the answer shows up in entity resolution/synonyms grab it.
            if synonym['status']['code'] == "ER_SUCCESS_MATCH":
                answer = synonym['values'][0]['value']['name']
            else:
                # Otherwise grab the non-ER slot value.
                answer = intent['slots']['CatchAllAnswer']['value']
        except KeyError:
            # Grab the non-ER slot value if ER keys missing too.
            answer = intent['slots']['CatchAllAnswer']['value']
    else:
        # If we got this far we should mark it as no response because
        # another word wasn't caught by the catchcall slot (e.g. NoIntent).
        answer = "no response"
    logger.debug("=====Answer Heard:  %s", answer.lower())
    return answer.lower()
