"""
AWS Lambda Entrypoint
"""
from __future__ import print_function
import json
import logging
import random
import datetime
from play_new_game import play_new_game
from handle_answer_request import (
    handle_answer_request, next_clue_request, repeat_clue_request
)
from alexa_responses import play_end_message, speech
from manage_data import get_player_info, get_others_in_household
from strings import (
    HELP_MESSAGE_DURING_GAME, HELP_MESSAGE_BEFORE_GAME, FIRST_GAME_MESSAGE,
    WELCOME_REPROMPT, WELCOME_BACK_MESSAGE_1, WELCOME_BACK_MESSAGE_2,
    WELCOME_BACK_MESSAGE_PERSONALIZED_1, WELCOME_BACK_MESSAGE_PERSONALIZED_2,
    WELCOME_BACK_MESSAGE_OPPONENT_1, WELCOME_BACK_MESSAGE_OPPONENT_2,
    FIRST_GAME_MESSAGE_PERSONALIZED
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def lambda_handler(event, _context):
    """ AWS Lambda entry point """
    logger.debug('=====lambda handler started...')
    logger.debug(json.dumps(event))

    user_id = event['session']['user']['userId']
    if 'person' in event['context']['System']:
        person_id = event['context']['System']['person']['personId']
    else:
        person_id = "default"

    logger.debug("=====Person ID: %s", person_id)

    # If a one-shot was used to start a new game treat it like a LaunchRequest.
    if event['session']['new'] and event['request']['type'] == "IntentRequest":
        return launch_request(user_id, person_id)
    if event['request']['type'] == "LaunchRequest":
        return launch_request(user_id, person_id)
    if event['request']['type'] == "IntentRequest":
        return on_intent(event['request']['intent'], event['session'])
    if event['request']['type'] == "SessionEndedRequest":
        return play_end_message()


def launch_request(user_id, person_id):
    """ Handles LaunchRequests """
    player = get_player_info(user_id, person_id)
    logger.debug("=====Player Info: %s", player)

    # Pick a random number for use when picking a welcome message.
    random_number = random.randint(0, 1)

    # Here we pick a welcome back message for a returning customer.
    if player['gamesPlayed']['N'] != "0":
        # No voice profile, no personalization.
        if person_id == "default":
            if player['lastScore']['N'] == "0":
                tts = WELCOME_BACK_MESSAGE_1.format(
                    player['lifetimeScore']['N'])
            # If their last score was greater than 0 we have more options.
            elif random_number == 0:
                tts = WELCOME_BACK_MESSAGE_1.format(
                    player['lifetimeScore']['N'])
            elif random_number == 1:
                tts = WELCOME_BACK_MESSAGE_2.format(player['lastScore']['N'])
        # If we have a returning player with a voice profile we personalize.
        else:
            # If other people in the same household are playing, we can start
            # some friendly competition by using personalization to tell
            # the scores of others on the account to the current player.
            others_in_household = get_others_in_household(
                user_id, person_id)

            if others_in_household:
                logger.debug("=====Checking for household opponent....")
                # TODO 1 (NOTES.md)
                opponent_id = random.choice(others_in_household)
                opponent = get_player_info(user_id, opponent_id)

                # Check if opponent has played recently.
                if 'lastPlayed' in opponent:
                    logger.debug("=====Valid opponent found....")
                    date_opponent_last_played = datetime.datetime.strptime(
                        opponent['lastPlayed']['S'], "%Y-%m-%dT%H:%M:%S.%f")
                    date_7_days_ago = datetime.datetime.today() - datetime.timedelta(days=7)

                    if date_opponent_last_played > date_7_days_ago:
                        logger.debug(
                            "=====Opponent has played within the last week....")
                        tts = WELCOME_BACK_MESSAGE_OPPONENT_1.format(
                            person_id, opponent_id, opponent['lastScore']['N'])
                    else:
                        logger.debug(
                            "=====Opponent has not played recently....")
                        tts = WELCOME_BACK_MESSAGE_OPPONENT_2.format(
                            person_id, opponent_id)
                else:
                    logger.debug("=====No valid opponent found....")
                    # If opponent has never completed a game, fallback.
                    tts = WELCOME_BACK_MESSAGE_PERSONALIZED_1.format(person_id,
                                                                     player['lifetimeScore']['N'])
            # If nobody else playing in the household then we just
            # personalize for the current player only.
            elif player['lastScore']['N'] == "0":
                tts = WELCOME_BACK_MESSAGE_PERSONALIZED_1.format(person_id,
                                                                 player['lifetimeScore']['N'])
            # If their last score was greater than 0 we have more options.
            elif random_number == 0:
                tts = WELCOME_BACK_MESSAGE_PERSONALIZED_1.format(person_id,
                                                                 player['lifetimeScore']['N'])
            elif random_number == 1:
                tts = WELCOME_BACK_MESSAGE_PERSONALIZED_2.format(person_id,
                                                                 player['lastScore']['N'])
    # Otherwise it looks like a new customer and they get a welcome experience.
    else:
        # If no voice profile detected give the non-personalized experience.
        if person_id == "default":
            tts = FIRST_GAME_MESSAGE
        # Otherwise we personalize the greeting.
        else:
            tts = FIRST_GAME_MESSAGE_PERSONALIZED

    # Prepping session attributes to be used during gameplay.
    attributes = {
        "game_status": "not_yet_started",
        "player_info": player
    }

    return speech(tts=tts,
                  attributes=attributes,
                  should_end_session=False,
                  reprompt=WELCOME_REPROMPT)


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
    if 'attributes' in session:
        if 'questions' in session['attributes']:
            return handle_answer_request(intent, session)

        # If the game hasn't started yet, the player may have
        # interrupted Alexa during the rules being read to them.
        if session['attributes']['game_status'] == "not_yet_started":
            return speech(tts=HELP_MESSAGE_BEFORE_GAME,
                          attributes=session['attributes'],
                          should_end_session=False,
                          answered_correctly=None,
                          reprompt=WELCOME_REPROMPT)

    # We probably got here because the player said something other than
    # yes or no after asking if they wanted to play the game again.
    logger.debug("=====No attributes, ending game!")
    return play_end_message()


def next_clue_intent(session):
    """handle a NextClueIntent request"""
    print("=====next_clue_intent fired...")
    if 'attributes' in session:
        if session['attributes']['game_status'] == "in_progress":
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
    tts = HELP_MESSAGE_BEFORE_GAME
    if 'attributes' in session:
        # if there's a session and we're in a game
        # give the last clue at the end of the rules
        if session['attributes']['game_status'] == "in_progress":
            clue = session['attributes']['current_clue']
            tts = HELP_MESSAGE_DURING_GAME + clue

    return speech(tts, session['attributes'], False, None)
