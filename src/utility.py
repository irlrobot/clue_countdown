"""
Utility and helper functions
"""
import datetime
import logging
import random
from manage_data import get_player_info, get_others_in_household
import strings


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_household_and_person_ids(event):
    """ Parse the householdID and personID from the session """
    household_id = event['session']['user']['userId']
    if 'person' in event['context']['System']:
        person_id = event['context']['System']['person']['personId']
    else:
        person_id = "default"

    logger.debug("=====Person ID: %s", household_id)
    logger.debug("=====Person ID: %s", person_id)
    return household_id, person_id


def determine_welcome_message(household_id, person_id, player):
    """ Determines the welcome message content including
    whether or not to personalize the speech """
    # Pick a random number for use when picking a welcome message.
    random_number = random.randint(0, 1)

    # Here we pick a welcome back message for a returning customer.
    if player['gamesPlayed']['N'] != "0":
        # No voice profile, no personalization.
        if person_id == "default":
            if player['lastScore']['N'] == "0":
                tts = strings.WELCOME_BACK_MESSAGE_1.format(
                    player['lifetimeScore']['N'])
            # If their last score was greater than 0 we have more options.
            elif random_number == 0:
                tts = strings.WELCOME_BACK_MESSAGE_1.format(
                    player['lifetimeScore']['N'])
            elif random_number == 1:
                tts = strings.WELCOME_BACK_MESSAGE_2.format(
                    player['lastScore']['N'])
        # If we have a returning player with a voice profile we personalize.
        else:
            # If other people in the same household are playing, we can start
            # some friendly competition by using personalization to tell
            # the scores of others on the account to the current player.
            others_in_household = get_others_in_household(
                household_id, person_id)

            if others_in_household:
                logger.debug("=====Checking for household opponent....")
                # TODO 1 (NOTES.md)
                opponent_id = random.choice(others_in_household)
                opponent = get_player_info(household_id, opponent_id)

                # Check if opponent has played recently.
                if 'lastPlayed' in opponent:
                    logger.debug("=====Valid opponent found....")
                    date_opponent_last_played = datetime.datetime.strptime(
                        opponent['lastPlayed']['S'], "%Y-%m-%dT%H:%M:%S.%f")
                    date_7_days_ago = datetime.datetime.today() - datetime.timedelta(days=7)

                    if date_opponent_last_played > date_7_days_ago:
                        logger.debug(
                            "=====Opponent has played within the last week....")
                        tts = strings.WELCOME_BACK_MESSAGE_OPPONENT_1.format(
                            person_id, opponent_id, opponent['lastScore']['N'])
                    else:
                        logger.debug(
                            "=====Opponent has not played recently....")
                        tts = strings.WELCOME_BACK_MESSAGE_OPPONENT_2.format(
                            person_id, opponent_id)
                else:
                    logger.debug("=====No valid opponent found....")
                    # If opponent has never completed a game, fallback.
                    tts = strings.WELCOME_BACK_PERSONALIZED_1.format(person_id,
                                                                     player['lifetimeScore']['N'])
            # If nobody else playing in the household then we just
            # personalize for the current player only.
            elif player['lastScore']['N'] == "0":
                tts = strings.WELCOME_BACK_PERSONALIZED_1.format(person_id,
                                                                 player['lifetimeScore']['N'])
            # If their last score was greater than 0 we have more options.
            elif random_number == 0:
                tts = strings.WELCOME_BACK_PERSONALIZED_1.format(person_id,
                                                                 player['lifetimeScore']['N'])
            elif random_number == 1:
                tts = strings.WELCOME_BACK_PERSONALIZED_2.format(person_id,
                                                                 player['lastScore']['N'])
    # Otherwise it looks like a new customer and they get a welcome experience.
    else:
        # If no voice profile detected give the non-personalized experience.
        if person_id == "default":
            tts = strings.FIRST_GAME
        # Otherwise we personalize the greeting.
        else:
            tts = strings.FIRST_GAME_PERSONALIZED.format(person_id)

    return tts
