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
        self.total_score = None
        self.current_clue_index = None
        self.play_newest_word_pack = None
        self.current_score = None
        self.current_question_index = None
        self.parse_attributes()

    def parse_attributes(self):
        for key, value in self.attributes.items():
            setattr(self, key, value)

    def get_answer_for_current_question(self):
        return self.questions[self.current_question_index]['code_word'].lower()

    def update_last_word_pack_played(self, pack_num):
        player_info = self.player_info
        player_info['lastWordPackPlayed']['N'] = pack_num
        setattr(self, 'player_info', player_info)

    def update_total_score(self, total_score):
        setattr(self, 'total_score', total_score)

        player_info = self.player_info
        new_lifetime_score = int(
            player_info['lifetimeScore']['N']) + total_score
        player_info['lifetimeScore']['N'] = new_lifetime_score
        player_info['lastScore']['N'] = total_score

    def move_on_to_next_question(self):
        setattr(self, 'current_question_index',
                self.current_question_index + 1)
        setattr(self, 'current_clue_index', 0)
        setattr(self, 'current_clue',
                self.questions[self.current_question_index]['clues'][0])

    def get_first_clue(self):
        return self.questions[self.current_question_index]['clues'][0]

    def get_customer_id(self):
        return self.player_info['customerID']['S']

    def increment_total_games_played(self):
        player_info = self.player_info
        games_played = int(player_info['gamesPlayed']['N']) + 1
        player_info['gamesPlayed']['N'] = games_played
