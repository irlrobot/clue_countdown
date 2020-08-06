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
           card_title=None, card_text=None,
           answered_correctly=None,
           prompt_sound=strings.PROMPT_SOUND,
           reprompt=strings.STANDARD_REPROMPT,
           music=strings.CLUE_READING_MUSIC):
    """ Build speech output """
    logger.debug("======speech fired...")
    logger.debug("+++++%s", answered_correctly)

    if answered_correctly:
        sound_effect = strings.CORRECT_SOUND
    elif answered_correctly is None:
        sound_effect = strings.BRIDGE_SOUND
    else:
        sound_effect = strings.WRONG_SOUND

    response = {
        "version": "1.0",
        "sessionAttributes": attributes,
        "response": {
            "shouldEndSession": should_end_session,
            "reprompt": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": reprompt
                }
            }
        }
    }

    if card_title and card_text:
        response['response'].update(
            add_card_to_response(card_title, card_text))

    response['response']['directives'] = add_apl_to_response(
        tts=tts,
        sound_effect=sound_effect,
        music=music,
        prompt_sound=prompt_sound)

    logger.debug(json.dumps(response))
    return response


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

    return speech(tts=tts,
                  should_end_session=True,
                  prompt_sound=strings.OUTRO_SOUND)


def add_apl_to_response(tts=None, sound_effect=None,
                        music=None, prompt_sound=None,
                        music_trim=3500, effect_trim=2000):
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
                                "type": "Audio",
                                "source": sound_effect,
                                "filter": [
                                    {
                                        "type": "Volume",
                                        "amount": 0.5
                                    },
                                    {
                                        "type": "Trim",
                                        "end": effect_trim
                                    }
                                ]
                            },
                            {
                                "type": "Mixer",
                                "items": [
                                    {
                                        "type": "Speech",
                                        "contentType": "SSML",
                                        "content": "<speak>{}</speak>".format(tts)
                                    },
                                    {
                                        "type": "Audio",
                                        "source": music,
                                        "filter": [
                                            {
                                                "type": "Volume",
                                                "amount": 0.7
                                            },
                                            {
                                                "type": "Trim",
                                                "end": music_trim
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "Audio",
                                "source": prompt_sound
                            }
                        ]
                    }
                }
            }
        }
    ]

    return directives


def add_card_to_response(card_title, card_text):
    """ Adds APL directives to a response """
    card = {
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
        }
    }

    return card
