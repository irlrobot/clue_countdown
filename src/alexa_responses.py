"""
Send responses back to the Alexa service
"""
from __future__ import print_function
import json
import logging
import random
import strings


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def speech(tts=None, attributes=None, should_end_session=None,
           answered_correctly=None, reprompt=None):
    """ Build speech output """
    logger.debug("======speech fired...")
    sound_effect = get_sound_effect_for_answer(answered_correctly)
    prompt_sound = get_prompt_sound(should_end_session)

    if reprompt is None:
        reprompt_tts = strings.STANDARD_REPROMPT
    else:
        reprompt_tts = reprompt

    response = {
        "version": "1.0",
        "sessionAttributes": attributes,
        "response": {
            "shouldEndSession": should_end_session,
            # "outputSpeech": {
            #    "type": "SSML",
            #    "ssml": "<speak>" + sound + tts + prompt + "</speak>"
            # },
            "reprompt": {
                "outputSpeech": {
                    "type": "SSML",
                    "ssml": "<speak>{}</speak>".format(reprompt_tts)
                }
            },
        }
    }

    response_with_apl = add_apl_to_response(
        response, sound_effect, tts, prompt_sound)
    logger.debug(json.dumps(response_with_apl))
    return response_with_apl


def speech_with_card(tts=None, attributes=None, should_end_session=None,
                     card_title=None, card_text=None,
                     answered_correctly=None, reprompt=None):
    """ Build speech output with a card """
    logger.debug("======speech_with_card fired...")
    sound_effect = get_sound_effect_for_answer(answered_correctly)
    prompt_sound = get_prompt_sound(should_end_session)

    if reprompt is None:
        reprompt_tts = "Time's up!  What's your guess?"
    else:
        reprompt_tts = reprompt
    response = {
        "version": "1.0",
        "sessionAttributes": attributes,
        "response": {
            "shouldEndSession": should_end_session,
            # "outputSpeech": {
            #    "type": "SSML",
            #    "ssml": "<speak>{}{}{}</speak>".format(sound_effect, tts, prompt_sound)
            # },
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

    response_with_apl = add_apl_to_response(
        response, sound_effect, tts, prompt_sound)
    logger.debug(json.dumps(response_with_apl))
    return response_with_apl


def play_end_message():
    """ Play a standard message when exiting the skill """
    logger.debug("=====play_end_message fired...")
    standard_message = strings.STANDARD_EXIT_MESSAGE
    review_message = strings.EXIT_WITH_REVIEW_REQUEST

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


def get_prompt_sound(should_end_session):
    """ Determine if the prompt sound should play """
    if should_end_session:
        return ''

    return "<audio src=\"https://s3.amazonaws.com/trainthatbrain/prompt.mp3\" />"


def add_apl_to_response(response, sound_effect, tts, prompt_sound):
    """ Adds APL directives to a response """
    directives = [
        {
            "type": "Alexa.Presentation.APLA.RenderDocument",
            "token": "code-countdown",
            "document": {
                "version": "0.8",
                "type": "APLA",
                "mainTemplate": {
                    "item": {
                        "type": "Sequencer",
                        "items": [
                            {
                                "type": "Mixer",
                                "items": [
                                    {
                                        "type": "Sequencer",
                                        "items": [{
                                            "type": "Speech",
                                            "contentType": "SSML",
                                            "content": "<speak>{}{}</speak>".format(sound_effect, tts)
                                        }]
                                    },
                                    {
                                        "type": "Audio",
                                        "description": "https://developer.amazon.com/en-US/docs/alexa/custom-skills/ask-soundlibrary.html",
                                        "source": "soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_countdown_loop_64s_minimal_01",
                                        "filter": [
                                            {
                                                "type": "Volume",
                                                "amount": 0.7
                                            },
                                            {
                                                "type": "Trim",
                                                "end": 3500
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "Speech",
                                "contentType": "SSML",
                                "content": "<speak>{}</speak>".format(prompt_sound)
                            }
                        ]
                    }
                }
            }
        }
    ]

    response["response"]["directives"] = directives
    return response
