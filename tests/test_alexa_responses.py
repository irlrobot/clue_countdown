#!/usr/bin/env python
from src.alexa_responses import (
    speech, speech_with_card, play_end_message
)

###########################################
# speech()
###########################################


def test_speech_no_reprompt_answered_correctly_end_session():
    tts = 'blah'
    attributes = {}
    should_end_session = True
    answered_correctly = True
    expected = {
        'version': '1.0',
        'sessionAttributes': {},
        'response': {
            'shouldEndSession': True,
            'outputSpeech': {
                'type': 'SSML',
                'ssml': '<speak><audio src="https://s3.amazonaws.com/trainthatbrain/correct.mp3" />blah</speak>'
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': "Time's up!  What's your guess?"
                }
            }
        }
    }

    assert speech(tts, attributes, should_end_session,
                  answered_correctly) == expected


def test_speech_reprompt_answered_correctly_end_session():
    tts = 'blah'
    attributes = {}
    should_end_session = True
    answered_correctly = True
    reprompt = 'blah'
    expected = {
        'version': '1.0',
        'sessionAttributes': {},
        'response': {
            'shouldEndSession': True,
            'outputSpeech': {
                'type': 'SSML',
                'ssml': '<speak><audio src="https://s3.amazonaws.com/trainthatbrain/correct.mp3" />blah</speak>'
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': 'blah'
                }
            }
        }
    }

    assert speech(tts, attributes, should_end_session,
                  answered_correctly, reprompt) == expected


def test_speech_no_reprompt_answered_correctly_dont_end_session():
    tts = 'blah'
    attributes = {}
    should_end_session = False
    answered_correctly = True
    expected = {
        'version': '1.0',
        'sessionAttributes': {},
        'response': {
            'shouldEndSession': False,
            'outputSpeech': {
                'type': 'SSML',
                'ssml': '<speak><audio src="https://s3.amazonaws.com/trainthatbrain/correct.mp3" />blah<audio src="https://s3.amazonaws.com/trainthatbrain/prompt.mp3" /></speak>'
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': "Time's up!  What's your guess?"
                }
            }
        }
    }

    assert speech(tts, attributes, should_end_session,
                  answered_correctly) == expected


def test_speech_reprompt_answered_correctly_dont_end_session():
    tts = 'blah'
    attributes = {}
    should_end_session = False
    answered_correctly = True
    reprompt = 'blah'
    expected = {
        'version': '1.0',
        'sessionAttributes': {},
        'response': {
            'shouldEndSession': False,
            'outputSpeech': {
                'type': 'SSML',
                'ssml': '<speak><audio src="https://s3.amazonaws.com/trainthatbrain/correct.mp3" />blah<audio src="https://s3.amazonaws.com/trainthatbrain/prompt.mp3" /></speak>'
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': 'blah'
                }
            }
        }
    }

    assert speech(tts, attributes, should_end_session,
                  answered_correctly, reprompt) == expected

###########################################
# speech_with_card()
###########################################


def test_speech_with_card_no_reprompt_answered_correctly_end_session():
    tts = 'blah'
    attributes = {}
    should_end_session = True
    card_title = 'blah'
    card_text = 'blah'
    answered_correctly = True
    expected = {
        'version': '1.0',
        'sessionAttributes': {},
        'response': {
            'shouldEndSession': True,
            'outputSpeech': {
                'type': 'SSML',
                'ssml': '<speak><audio src="https://s3.amazonaws.com/trainthatbrain/correct.mp3" />blah</speak>'
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
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': "Time's up!  What's your guess?"
                }
            }
        }
    }

    assert speech_with_card(tts, attributes, should_end_session,
                            card_title, card_text,
                            answered_correctly) == expected


def test_speech_with_card_reprompt_answered_correctly_end_session():
    tts = 'blah'
    attributes = {}
    should_end_session = True
    card_title = 'blah'
    card_text = 'blah'
    answered_correctly = True
    reprompt = 'blah'
    expected = {
        'version': '1.0',
        'sessionAttributes': {},
        'response': {
            'shouldEndSession': True,
            'outputSpeech': {
                'type': 'SSML',
                'ssml': '<speak><audio src="https://s3.amazonaws.com/trainthatbrain/correct.mp3" />blah</speak>'
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
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': 'blah'
                }
            }
        }
    }

    assert speech_with_card(tts, attributes, should_end_session,
                            card_title, card_text,
                            answered_correctly, reprompt) == expected


def test_speech_with_card_no_reprompt_answered_correctly_dont_end_session():
    tts = 'blah'
    attributes = {}
    should_end_session = False
    card_title = 'blah'
    card_text = 'blah'
    answered_correctly = True
    expected = {
        'version': '1.0',
        'sessionAttributes': {},
        'response': {
            'shouldEndSession': False,
            'outputSpeech': {
                'type': 'SSML',
                'ssml': '<speak><audio src="https://s3.amazonaws.com/trainthatbrain/correct.mp3" />blah<audio src="https://s3.amazonaws.com/trainthatbrain/prompt.mp3" /></speak>'
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
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': "Time's up!  What's your guess?"
                }
            }
        }
    }

    assert speech_with_card(tts, attributes, should_end_session,
                            card_title, card_text,
                            answered_correctly) == expected


def test_speech_with_card_reprompt_answered_correctly_dont_end_session():
    tts = 'blah'
    attributes = {}
    should_end_session = False
    card_title = 'blah'
    card_text = 'blah'
    answered_correctly = True
    reprompt = 'blah'
    expected = {
        'version': '1.0',
        'sessionAttributes': {},
        'response': {
            'shouldEndSession': False,
            'outputSpeech': {
                'type': 'SSML',
                'ssml': '<speak><audio src="https://s3.amazonaws.com/trainthatbrain/correct.mp3" />blah<audio src="https://s3.amazonaws.com/trainthatbrain/prompt.mp3" /></speak>'
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
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': 'blah'
                }
            }
        }
    }

    assert speech_with_card(tts, attributes, should_end_session,
                            card_title, card_text,
                            answered_correctly, reprompt) == expected

###########################################
# play_end_message()
###########################################


def test_play_end_message_with_rating(mocker):
    # mock randint to always return 1
    mocker.patch('random.randint', return_value=1)
    expected = {
        'version': '1.0',
        'sessionAttributes': {},
        'response': {
            'shouldEndSession': True,
            'outputSpeech': {
                'type': 'SSML',
                'ssml': '<speak>Thanks for playing Words Plus Clues!</speak>'
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': "Time's up!  What's your guess?"
                }
            }
        }
    }
    assert play_end_message() == expected
