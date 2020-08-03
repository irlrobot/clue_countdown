"""
A class for managing session attributes during the game
"""


class SessionAttributes():
    def __init__(self, attributes):
        self.attributes = attributes
        self.game_status = None
        self.player_info = None
        self.questions = None
        self.game_length = None
        self.score = None
        self.current_clue_index = None
        self.play_newest_word_pack = None
        self.parse_attributes()

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        self._attributes = attributes
        self.parse_attributes()

    @property
    def game_status(self):
        return self._game_status

    @game_status.setter
    def game_status(self, game_status):
        self._game_status = game_status

    @property
    def player_info(self):
        return self._player_info

    @player_info.setter
    def player_info(self, player_info):
        self._player_info = player_info

    @property
    def questions(self):
        return self._questions

    @questions.setter
    def questions(self, questions):
        self._questions = questions

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, score):
        self._score = score

    @property
    def current_clue_index(self):
        return self._current_clue_index

    @current_clue_index.setter
    def current_clue_index(self, current_clue_index):
        self._current_clue_index = current_clue_index

    @property
    def play_newest_word_pack(self):
        return self._play_newest_word_pack

    @play_newest_word_pack.setter
    def play_newest_word_pack(self, play_newest_word_pack):
        self._play_newest_word_pack = play_newest_word_pack

    def parse_attributes(self):
        for key, value in self.attributes.items():
            print(key, value)
            setattr(self, key, value)
