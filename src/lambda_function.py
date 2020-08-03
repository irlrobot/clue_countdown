"""
AWS Lambda entrypoint and Intent router
"""
from __future__ import print_function
import json
import logging
import strings
from manage_data import get_player_info
from utility import (
    get_household_and_person_ids,
    determine_welcome_message,
    questions_loaded_in,
    get_game_status
)
from play_new_game import play_new_game
from handle_answer_request import (
    handle_answer_request,
    next_clue_request,
    repeat_clue_request
)
from alexa_responses import play_end_message, speech


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def lambda_handler(event, _context):
    """ AWS Lambda entry point """
    logger.debug('=====lambda handler started...')
    logger.debug(json.dumps(event))

    household_id, person_id = get_household_and_person_ids(event)

    # If a one-shot was used to start a new game treat it like a LaunchRequest.
    if event['session']['new'] and event['request']['type'] == "IntentRequest":
        return launch_request(household_id, person_id)
    if event['request']['type'] == "LaunchRequest":
        return launch_request(household_id, person_id)
    if event['request']['type'] == "IntentRequest":
        return on_intent(event['request']['intent'], event['session'])
    if event['request']['type'] == "SessionEndedRequest":
        return play_end_message()


def launch_request(household_id, person_id):
    """ Handles LaunchRequests """
    player = get_player_info(household_id, person_id)
    logger.debug("=====Player Info: %s", player)

    tts = determine_welcome_message(household_id, person_id, player)

    session_attributes = {
        "game_status": "not_yet_started",
        "player_info": player
    }

    return speech(tts=tts,
                  attributes=session_attributes,
                  should_end_session=False,
                  reprompt=strings.WELCOME_REPROMPT)


def on_intent(intent, session):
    """ Router for IntentRequest """
    intent_name = intent['name']
    logger.debug("=====IntentRequest: %s", intent_name)

    if intent_name == "AnswerIntent":
        return answer_intent(intent, session)
    if intent_name == "NextClueIntent":
        return next_clue_intent(session)
    if intent_name == "NotSureIntent":
        return not_sure_intent(intent, session)
    if intent_name == "RepeatIntent":
        return repeat_intent(session)
    if intent_name == "AMAZON.StartOverIntent":
        return start_over_intent(session)
    if intent_name == "AMAZON.YesIntent":
        return yes_intent(intent, session)
    if intent_name == "AMAZON.NoIntent":
        return no_intent(intent, session)
    if intent_name in ("AMAZON.StopIntent", "AMAZON.CancelIntent"):
        return play_end_message()
    if intent_name == 'AMAZON.HelpIntent':
        return help_intent(session)


def answer_intent(intent, session):
    """ Handles AnswerIntent """
    logger.debug("=====answer_intent fired...")
    if questions_loaded_in(session):
        return handle_answer_request(intent, session)

    # If the game hasn't started yet, the player may have
    # interrupted Alexa during the rules being read to them.
    if get_game_status(session) == "not_yet_started":
        return speech(tts=strings.HELP_MESSAGE_BEFORE_GAME,
                      attributes=session['attributes'],
                      should_end_session=False,
                      reprompt=strings.WELCOME_REPROMPT)

    # We probably got here because the player said something other than
    # yes or no after asking if they wanted to play the game again.
    logger.debug("=====No attributes, ending game!")
    return play_end_message()


def next_clue_intent(session):
    """ Handle NextClueIntent """
    logger.debug("=====next_clue_intent fired...")
    game_status = get_game_status(session)
    if game_status == "in_progress":
        return next_clue_request(session=session, was_wrong_answer=False)

    # If it's not started yet the player might have interrupted
    # Alexa during the rules being read so we repeat them.
    if game_status == "not_yet_started":
        return speech(tts=strings.HELP_MESSAGE_BEFORE_GAME,
                      attributes=session['attributes'],
                      should_end_session=False,
                      reprompt=strings.WELCOME_REPROMPT)

    # Player probably got here because they said something other than
    # yes or no after asking if they wanted to play the game again.
    # TODO 2 perhaps we should start the game again instead to entice them?
    logger.debug("=====No attributes ending game...")
    return play_end_message()


def not_sure_intent(intent, session):
    """ Handle NotSureIntent """
    logger.debug("=====not_sure_intent fired...")
    game_status = get_game_status(session)

    if game_status == "in_progress":
        # If we're on the last clue then count this as an answer.
        if session['attributes']['current_clue_index'] == 4:
            return handle_answer_request(intent, session)

        return next_clue_request(session, False)

    # If it's not started yet the player might have interrupted
    # Alexa during the rules being read so we repeat them.
    if game_status == "not_yet_started":
        return speech(tts=strings.HELP_MESSAGE_BEFORE_GAME,
                      attributes=session['attributes'],
                      should_end_session=False,
                      reprompt=strings.WELCOME_REPROMPT)

    # Player probably got here because they said something other than
    # yes or no after asking if they wanted to play the game again.
    # TODO 2 perhaps we should start the game again instead to entice them?
    logger.debug("=====No attributes ending game...")
    return play_end_message()


def repeat_intent(session):
    """ Handle RepeatIntent """
    logger.debug("=====repeat_intent fired...")
    game_status = get_game_status(session)

    if game_status == "in_progress":
        return repeat_clue_request(session)

    # If it's not started yet the player might have interrupted
    # Alexa during the rules being read so we repeat them.
    if game_status == "not_yet_started":
        return speech(tts=strings.HELP_MESSAGE_BEFORE_GAME,
                      attributes=session['attributes'],
                      should_end_session=False,
                      reprompt=strings.WELCOME_REPROMPT)

    # Player probably got here because they said something other than
    # yes or no after asking if they wanted to play the game again.
    # TODO 2 perhaps we should start the game again instead to entice them?
    logger.debug("=====no attributes ending game")
    return play_end_message()


def start_over_intent(session):
    """ Handle StartOverIntent """
    logger.debug("=====start_over_intent fired...")
    game_status = get_game_status(session)

    if game_status == "in_progress":
        return play_new_game(True, session['attributes']['player_info'])

    # If it's not started yet the player might have interrupted
    # Alexa during the rules being read so we repeat them.
    if game_status == "not_yet_started":
        return speech(tts=strings.HELP_MESSAGE_BEFORE_GAME,
                      attributes=session['attributes'],
                      should_end_session=False,
                      reprompt=strings.WELCOME_REPROMPT)

    # If the game is over start a new one.
    if game_status == "ended":
        return play_new_game(True, session['attributes']['player_info'])


def yes_intent(intent, session):
    """ Handle YesIntent """
    logger.debug("=====yes_intent fired...")
    game_status = get_game_status(session)

    # If there is a game in progress we treat this as a wrong answer.
    if game_status == "in_progress":
        return handle_answer_request(intent, session)

    # If it's not started yet the player wants to hear the rules.
    if game_status == "not_yet_started":
        return speech(tts=strings.HELP_MESSAGE_BEFORE_GAME,
                      attributes=session['attributes'],
                      should_end_session=False,
                      reprompt=strings.WELCOME_REPROMPT)

    # Otherwise they're trying to play the game again after finishing a game.
    return play_new_game(True, session['attributes']['player_info'])


def no_intent(intent, session):
    """ Handle NoIntent """
    logger.debug("=====no_intent fired...")
    game_status = get_game_status(session)

    # If there is a game in progress we treat this as a wrong answer.
    if game_status == "in_progress":
        return handle_answer_request(intent, session)

    # If it's not started yet the player does not want the rules.
    if game_status == "not_yet_started":
        return play_new_game(False, session['attributes']['player_info'])

    # Otherwise end the game.
    return play_end_message()


def help_intent(session):
    """ Handle HelpIntent """
    logger.debug("=====help_intent fired...")
    tts = strings.HELP_MESSAGE_BEFORE_GAME

    if get_game_status(session) == "in_progress":
        clue = session['attributes']['current_clue']
        tts = strings.HELP_MESSAGE_DURING_GAME + clue

    return speech(tts=tts,
                  attributes=session['attributes'],
                  should_end_session=False)
