"""
Send responses back to the Alexa service
"""
from __future__ import print_function
import logging
import random
from strings import STANDARD_EXIT_MESSAGE, EXIT_WITH_REVIEW_REQUEST


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def speech(tts=None, attributes=None, should_end_session=None,
           answered_correctly=None, reprompt=None):
    """ Build speech output """
    logger.debug("======speech fired...")
    sound = get_sound_effect_for_answer(answered_correctly)
    prompt = prompt_sound(should_end_session)

    if reprompt is None:
        reprompt_tts = """
        <amazon:emotion name="excited" intensity="medium">
        Time's up!  What's your guess?"
        </amazon:emotion>
        """
    else:
        reprompt_tts = reprompt

    response = {
        "version": "1.0",
        "sessionAttributes": attributes,
        "response": {
            "shouldEndSession": should_end_session,
            "outputSpeech": {
                "type": "SSML",
                "ssml": "<speak>" + sound + tts + prompt + "</speak>"
            },
            "reprompt": {
                "outputSpeech": {
                    "type": "SSML",
                    "ssml": "<speak>" + str(reprompt_tts) + "</speak>"
                }
            }
        }
    }

    logger.debug("=====Response back:  %s", str(response))
    return response


def speech_with_card(tts=None, attributes=None, should_end_session=None,
                     card_title=None, card_text=None,
                     answered_correctly=None, reprompt=None):
    """ Build speech output with a card """
    logger.debug("======speech_with_card fired...")
    sound = get_sound_effect_for_answer(answered_correctly)
    prompt = prompt_sound(should_end_session)

    if reprompt is None:
        reprompt_tts = "Time's up!  What's your guess?"
    else:
        reprompt_tts = reprompt
    response = {
        "version": "1.0",
        "sessionAttributes": attributes,
        "response": {
            "shouldEndSession": should_end_session,
            "outputSpeech": {
                "type": "SSML",
                "ssml": "<speak>" + sound + tts + prompt + "</speak>"
            },
            "card": {
                "type": "Standard",
                "title": card_title,
                "text": card_text,
                "image": {
                    "smallImageUrl":
                        "https://s3.amazonaws.com/trainthatbrain/code_word_card_small.png",
                    "largeImageUrl":
                        "https://s3.amazonaws.com/trainthatbrain/code_word_card_large.png"
                }
            },
            "reprompt": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": str(reprompt_tts)
                }
            }
        }
    }

    logger.debug("=====Response:  %s", str(response))
    return response


def play_end_message():
    """ Play a standard message when exiting the skill """
    logger.debug("=====play_end_message fired...")
    standard_message = STANDARD_EXIT_MESSAGE
    review_message = EXIT_WITH_REVIEW_REQUEST

    # Don't always ask for a review.
    if random.randint(1, 10) == 1:
        tts = review_message
    else:
        tts = standard_message

    return speech(tts, {}, True, None)


def get_sound_effect_for_answer(answer_was_right):
    """ Get the appropriate sound effect """
    # Do not add any sound effects if player isn't guessing.
    if answer_was_right is None:
        return ""
    if answer_was_right:
        return "<audio src=\"https://s3.amazonaws.com/trainthatbrain/correct.mp3\" />"

    return "<audio src=\"https://s3.amazonaws.com/trainthatbrain/wrong.mp3\" />"


def prompt_sound(should_end_session):
    """ Determine if the prompt sound should play """
    if should_end_session:
        return ''

    return "<audio src=\"https://s3.amazonaws.com/trainthatbrain/prompt.mp3\" />"
