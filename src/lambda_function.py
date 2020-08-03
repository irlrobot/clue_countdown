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
    determine_welcome_message
)
from play_new_game import play_new_game
from handle_answer_request import (
    handle_answer_request,
    next_clue_request,
    repeat_clue_request
)
from alexa_responses import play_end_message, speech
from session_attributes import SessionAttributes


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

    if 'attributes' in session:
        this_game = SessionAttributes(session['attributes'])
    else:
        # TODO if they used a one-shot and no game in progress, start a new game?
        this_game = {}

    if intent_name == "AnswerIntent":
        return answer_intent(intent, this_game)
    if intent_name == "NextClueIntent":
        return next_clue_intent(this_game)
    if intent_name == "NotSureIntent":
        return not_sure_intent(intent, this_game)
    if intent_name == "RepeatIntent":
        return repeat_intent(this_game)
    if intent_name == "AMAZON.StartOverIntent":
        return start_over_intent(this_game)
    if intent_name == "AMAZON.YesIntent":
        return yes_intent(intent, this_game)
    if intent_name == "AMAZON.NoIntent":
        return no_intent(intent, this_game)
    if intent_name in ("AMAZON.StopIntent", "AMAZON.CancelIntent"):
        return play_end_message()
    if intent_name == 'AMAZON.HelpIntent':
        return help_intent(this_game)


def answer_intent(intent, this_game):
    """ Handles AnswerIntent """
    logger.debug("=====answer_intent fired...")
    game_status = this_game.game_status()
    if game_status == "in_progress":
        return handle_answer_request(intent, this_game)

    # If the game hasn't started yet, the player may have
    # interrupted Alexa during the rules being read to them.
    if game_status == "not_yet_started":
        return speech(tts=strings.HELP_MESSAGE_BEFORE_GAME,
                      attributes=this_game.attributes,
                      should_end_session=False,
                      reprompt=strings.WELCOME_REPROMPT)

    # We probably got here because the player said something other than
    # yes or no after asking if they wanted to play the game again.
    logger.debug("=====No attributes, ending game!")
    return play_end_message()


def next_clue_intent(this_game):
    """ Handle NextClueIntent """
    logger.debug("=====next_clue_intent fired...")
    game_status = this_game.game_status()

    if game_status == "in_progress":
        return next_clue_request(this_game, False)

    # If it's not started yet the player might have interrupted
    # Alexa during the rules being read so we repeat them.
    if game_status == "not_yet_started":
        return speech(tts=strings.HELP_MESSAGE_BEFORE_GAME,
                      attributes=this_game.attributes,
                      should_end_session=False,
                      reprompt=strings.WELCOME_REPROMPT)

    # Player probably got here because they said something other than
    # yes or no after asking if they wanted to play the game again.
    # TODO 2 perhaps we should start the game again instead to entice them?
    logger.debug("=====No attributes ending game...")
    return play_end_message()


def not_sure_intent(intent, this_game):
    """ Handle NotSureIntent """
    logger.debug("=====not_sure_intent fired...")
    game_status = this_game.game_status()

    if game_status == "in_progress":
        # If we're on the last clue then count this as an answer.
        if this_game.current_clue_index == 4:
            return handle_answer_request(intent, this_game)

        # Otherwise we go to the next clue.
        return next_clue_request(this_game, False)

    # If it's not started yet the player might have interrupted
    # Alexa during the rules being read so we repeat them.
    if game_status == "not_yet_started":
        return speech(tts=strings.HELP_MESSAGE_BEFORE_GAME,
                      attributes=this_game.attributes,
                      should_end_session=False,
                      reprompt=strings.WELCOME_REPROMPT)

    # Player probably got here because they said something other than
    # yes or no after asking if they wanted to play the game again.
    # TODO 2 perhaps we should start the game again instead to entice them?
    logger.debug("=====No attributes ending game...")
    return play_end_message()


def repeat_intent(this_game):
    """ Handle RepeatIntent """
    logger.debug("=====repeat_intent fired...")
    game_status = this_game.game_status()

    if game_status == "in_progress":
        return repeat_clue_request(this_game)

    # If it's not started yet the player might have interrupted
    # Alexa during the rules being read so we repeat them.
    if game_status == "not_yet_started":
        return speech(tts=strings.HELP_MESSAGE_BEFORE_GAME,
                      attributes=this_game.attributes,
                      should_end_session=False,
                      reprompt=strings.WELCOME_REPROMPT)

    # Player probably got here because they said something other than
    # yes or no after asking if they wanted to play the game again.
    # TODO 2 perhaps we should start the game again instead to entice them?
    logger.debug("=====no attributes ending game")
    return play_end_message()


def start_over_intent(this_game):
    """ Handle StartOverIntent """
    logger.debug("=====start_over_intent fired...")
    game_status = this_game.game_status()

    if game_status == "in_progress":
        return play_new_game(True, this_game.player_info)

    # If it's not started yet the player might have interrupted
    # Alexa during the rules being read so we repeat them.
    if game_status == "not_yet_started":
        return speech(tts=strings.HELP_MESSAGE_BEFORE_GAME,
                      attributes=this_game.attributes,
                      should_end_session=False,
                      reprompt=strings.WELCOME_REPROMPT)

    # If the game is over start a new one.
    if game_status == "ended":
        return play_new_game(True, this_game.player_info)


def yes_intent(intent, this_game):
    """ Handle YesIntent """
    logger.debug("=====yes_intent fired...")
    game_status = this_game.game_status()

    # If there is a game in progress we treat this as a wrong answer.
    if game_status == "in_progress":
        return handle_answer_request(intent, this_game)

    # If it's not started yet the player wants to hear the rules.
    if game_status == "not_yet_started":
        return speech(tts=strings.HELP_MESSAGE_BEFORE_GAME,
                      attributes=this_game.attributes,
                      should_end_session=False,
                      reprompt=strings.WELCOME_REPROMPT)

    # Otherwise they're trying to play the game again after finishing a game.
    return play_new_game(True, this_game.player_info)


def no_intent(intent, this_game):
    """ Handle NoIntent """
    logger.debug("=====no_intent fired...")
    game_status = this_game.game_status()

    # If there is a game in progress we treat this as a wrong answer.
    if game_status == "in_progress":
        return handle_answer_request(intent, this_game)

    # If it's not started yet the player does not want the rules.
    if game_status == "not_yet_started":
        return play_new_game(False, this_game.player_info)

    # Otherwise end the game.
    return play_end_message()


def help_intent(this_game):
    """ Handle HelpIntent """
    logger.debug("=====help_intent fired...")
    tts = strings.HELP_MESSAGE_BEFORE_GAME

    if this_game.game_status() == "in_progress":
        tts = strings.HELP_MESSAGE_DURING_GAME + this_game.current_clue

    return speech(tts=tts,
                  attributes=this_game.attributes,
                  should_end_session=False)
