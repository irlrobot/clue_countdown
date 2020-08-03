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
    game_status
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

    attributes = {
        "game_status": "not_yet_started",
        "player_info": player
    }

    return speech(tts=tts,
                  attributes=attributes,
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
        if game_status(session) == "not_yet_started":
            return speech(tts=strings.HELP_MESSAGE_BEFORE_GAME,
                          attributes=session['attributes'],
                          should_end_session=False,
                          answered_correctly=None,
                          reprompt=strings.WELCOME_REPROMPT)

    # We probably got here because the player said something other than
    # yes or no after asking if they wanted to play the game again.
    logger.debug("=====No attributes, ending game!")
    return play_end_message()


def next_clue_intent(session):
    """ Handle NextClueIntent """
    logger.debug("=====next_clue_intent fired...")

    if game_status(session) == "in_progress":
        return next_clue_request(session=session, was_wrong_answer=False)

    # If it's not started yet the player might have interrupted
    # Alexa during the rules being read so we repeat them.
    if game_status(session) == "not_yet_started":
        return speech(tts=strings.HELP_MESSAGE_BEFORE_GAME,
                      attributes=session['attributes'],
                      should_end_session=False,
                      reprompt=strings.WELCOME_REPROMPT)

    # Player probably got here because they said something other than
    # yes or no after asking if they wanted to play the game again.
    # TODO 2 perhaps we should start the game again instead to entice them?
    logger.debug("=====No attributes ending game!")
    return play_end_message()


def not_sure_intent(intent, session):
    """handle a NotSureIntent request"""
    print("=====not_sure_intent fired...")
    if 'attributes' in session:
        if session['attributes']['game_status'] == "in_progress":
            # if we're on the last clue then count this as an answer
            if session['attributes']['current_clue_index'] == 4:
                return handle_answer_request(intent, session)
            return next_clue_request(session, False)
        # if it's not started yet the player might have
        # interrupted during the rule being read
        if session['attributes']['game_status'] == "not_yet_started":
            return speech(HELP_MESSAGE_BEFORE_GAME, session['attributes'], False,
                          None, WELCOME_REPROMPT)

    # we probably got here because user said something other than
    # yes or no after asking if they wanted to play the game again
    print("=====no attributes ending game")
    return play_end_message()


def repeat_intent(session):
    """handle a RepeatIntent request"""
    print("=====repeat_intent fired...")
    if 'attributes' in session:
        if session['attributes']['game_status'] == "in_progress":
            return repeat_clue_request(session)
        # if it's not started yet the player might have
        # interrupted during the rule being read
        if session['attributes']['game_status'] == "not_yet_started":
            return speech(HELP_MESSAGE_BEFORE_GAME, session['attributes'], False,
                          None, WELCOME_REPROMPT)

    # we probably got here because user said something other than
    # yes or no after asking if they wanted to play the game again
    print("=====no attributes ending game")
    return play_end_message()


def start_over_intent(session):
    """handle a StartOverIntent request"""
    print("=====start_over_intent fired...")
    # first we figure out where we're at in a game
    if 'attributes' in session:
        # if in progress, start over
        if session['attributes']['game_status'] == "in_progress":
            return play_new_game(True, session['attributes']['player_info'])
        # if it's not started yet the player might have
        # interrupted during the rule being read
        if session['attributes']['game_status'] == "not_yet_started":
            return speech(HELP_MESSAGE_BEFORE_GAME, session['attributes'], False,
                          None, WELCOME_REPROMPT)
        # if the game is over start a new one
        if session['attributes']['game_status'] == "ended":
            return play_new_game(True, session['attributes']['player_info'])


def yes_intent(intent, session):
    """handle a YesIntent request"""
    print("=====yes_intent fired...")
    # first we figure out where we're at in a game
    if 'attributes' in session:
        # if there's a session and we're in a game treat this as a wrong answer
        if session['attributes']['game_status'] == "in_progress":
            return handle_answer_request(intent, session)
        # if it's not started yet the player wants the rules
        if session['attributes']['game_status'] == "not_yet_started":
            return speech(HELP_MESSAGE_BEFORE_GAME, session['attributes'], False,
                          None, WELCOME_REPROMPT)
    # otherwise they're trying to play the game again after finishing a game
    return play_new_game(True, session['attributes']['player_info'])


def no_intent(intent, session):
    """handle a NoIntent request"""
    print("=====no_intent fired...")
    # first we figure out where we're at in a game
    if 'attributes' in session:
        # if there's a session and we're in a game treat this as a wrong answer
        if session['attributes']['game_status'] == "in_progress":
            return handle_answer_request(intent, session)
        # if it's not started yet the player doesn't want the rules
        if session['attributes']['game_status'] == "not_yet_started":
            return play_new_game(False, session['attributes']['player_info'])
    # otherwise end the game
    return play_end_message()


def help_intent(session):
    """handle a HelpIntent request"""
    print("=====help_intent fired...")
    tts = strings.HELP_MESSAGE_BEFORE_GAME
    if 'attributes' in session:
        # if there's a session and we're in a game
        # give the last clue at the end of the rules
        if session['attributes']['game_status'] == "in_progress":
            clue = session['attributes']['current_clue']
            tts = strings.HELP_MESSAGE_DURING_GAME + clue

    return speech(tts, session['attributes'], False, None)
