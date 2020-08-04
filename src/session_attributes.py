"""
A class for managing session attributes during the game
"""


class SessionAttributes():
    def __init__(self, attributes):
        self.__dict__ = attributes

    def get_answer_for_current_question(self):
        return self.questions[self.current_question_index]['code_word'].lower()

    def update_last_word_pack_played(self, pack_num):
        player_info = self.player_info
        player_info['lastWordPackPlayed']['N'] = pack_num
        setattr(self, 'player_info', player_info)

    def update_total_score(self, new_score):
        setattr(self, 'total_score', new_score)

        player_info = self.player_info
        new_lifetime_score = int(
            player_info['lifetimeScore']['N']) + new_score
        player_info['lifetimeScore']['N'] = new_lifetime_score
        player_info['lastScore']['N'] = new_score

    def move_on_to_next_question(self):
        setattr(self, 'current_question_index',
                self.current_question_index + 1)
        setattr(self, 'current_clue_index', 0)
        setattr(self, 'current_clue',
                self.questions[self.current_question_index]['clues'][0])

    def get_first_clue(self):
        return self.questions[self.current_question_index]['clues'][0]

    def move_on_to_next_clue(self):
        setattr(self, 'current_clue_index',
                self.current_clue_index + 1)
        setattr(self, 'current_clue',
                self.questions[self.current_question_index]['clues'][self.current_clue_index])

    def get_customer_id(self):
        return self.player_info['customerID']['S']

    def increment_total_games_played(self):
        player_info = self.player_info
        games_played = int(player_info['gamesPlayed']['N']) + 1
        player_info['gamesPlayed']['N'] = games_played

    def update_game_status(self, status):
        setattr(self, 'game_status', status)

    @property
    def attributes(self):
        return self.__dict__

    def ddb_stats_only(self):
        ddb = self.player_info.copy()
        ddb.pop('customerID')
        return ddb
