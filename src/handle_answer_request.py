"""
Handles the main flow of the game
"""
from __future__ import print_function
import logging
from fuzzywuzzy import fuzz
from alexa_responses import speech_with_card, speech
from manage_data import update_dynamodb
import strings
from word_bank import CURRENT_PACK_ID
from session_attributes import SessionAttributes


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def handle_answer_request(intent, session_attributes):
    """ Check if the answer is right, adjust score, and continue """
    logger.debug("=====handle_answer_request fired...")
    logger.debug(session_attributes)

    this_game = SessionAttributes(session_attributes)
    answer_heard = get_answer_from_(intent)
    current_question_value = 50 - int(this_game.current_clue_index * 10)
    correct_answer = this_game.get_answer_for_current_question()

    # Use Levenshtein distance algo to see if the words are similar enough.
    fuzzy_score = fuzz.partial_ratio(answer_heard, correct_answer)

    # Currently using a hardcoded score of 60 or better.
    if correct_answer in answer_heard or fuzzy_score >= 60:
        this_game.update_total_score(
            current_question_value + this_game.total_score)
        answered_correctly = True
    else:
        log_wrong_answer(answer_heard, correct_answer)
        answered_correctly = False
        # If clues remain give them the next clue instead of moving on.
        if this_game.current_clue_index != 4:
            return next_clue_request(attributes=this_game, last_guess_was_wrong=True)

    # If that was the last word and no clues remain, end the game.
    if this_game.current_question_index == this_game.game_length - 1:
        # If this was the latest word pack mark it
        # as played so the player doesn't get it again.
        if this_game.play_newest_word_pack:
            this_game.update_last_word_pack_played(CURRENT_PACK_ID)

        return end_game_return_score(this_game, answered_correctly,
                                     answer_heard, correct_answer)

    # If that wasn't the last word in the game continue on to next word.
    this_game.move_on_to_next_question()
    speech_output = strings.NEXT_ROUND_WITH_CLUE.format(
        this_game.get_first_clue())

    if answered_correctly:
        speech_output = strings.random_correct_answer_message(
            correct_answer) + speech_output
        card_text = "The word was:  " + correct_answer + ". You got " + \
            str(current_question_value) + " points!"
        card_title = "You figured out the word!"
    else:
        speech_output = strings.WRONG_ANSWER.format(
            correct_answer) + speech_output
        card_text = "The word was:  " + correct_answer + "\n" + \
            "You said:  " + str(answer_heard)
        card_title = "That wasn't the word!"

    return speech_with_card(tts=speech_output,
                            attributes=this_game.attributes,
                            should_end_session=False,
                            card_title=card_title,
                            card_text=card_text,
                            answered_correctly=answered_correctly)


def end_game_return_score(this_game, answered_correctly,
                          answer_heard, correct_answer):
    """ If the customer answered the last question we end the game """
    logger.debug("=====end_game_return_score fired...")
    this_game.increment_total_games_played()
    update_dynamodb(this_game.get_customer_id(), this_game.player_info)

    wrap_up_speech = strings.END_GAME_WRAP_UP.format(
        str(this_game.total_score))

    if answered_correctly:
        speech_output = strings.random_correct_answer_message(
            correct_answer) + wrap_up_speech
        card_text = "Your score is " + str(this_game.total_score) + " points!\n" + \
            "The last word was: " + correct_answer
    else:
        speech_output = strings.WRONG_ANSWER.format(
            str(correct_answer)) + wrap_up_speech
        card_text = "Your score is " + str(this_game.total_score) + " points!\n" + \
            "\nThe last word was: " + correct_answer + "\nYou said: " + answer_heard

    card_title = "Clue Countdown Results"
    reprompt = "Would you like to play Clue Countdown again?"

    return speech_with_card(tts=speech_output,
                            attributes=this_game.attributes,
                            should_end_session=False,
                            card_title=card_title,
                            card_text=card_text,
                            answered_correctly=answered_correctly,
                            reprompt=reprompt)


def next_clue_request(attributes=None, last_guess_was_wrong=None):
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


def get_answer_from_(intent):
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
