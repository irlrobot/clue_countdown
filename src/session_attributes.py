"""
Manages session attributes during the game
"""
import datetime


class SessionAttributes():
    """ Session Attributes manager """

    def __init__(self, attributes):
        self.__dict__ = attributes

    def get_answer_for_current_question(self):
        """ Returns the correct answer for the current question """
        return self.questions[self.current_question_index]['code_word'].lower()

    def update_last_word_pack_played(self, pack_num):
        """ Updates the lastWordPackPlayed attribute """
        player_info = self.player_info
        player_info['lastWordPackPlayed']['N'] = pack_num
        setattr(self, 'player_info', player_info)

    def update_total_score(self, additional_points):
        """ Updates the score for the current game and lifetime score """
        setattr(self, 'total_score', additional_points)

        player_info = self.player_info
        new_lifetime_score = int(
            player_info['lifetimeScore']['N']) + additional_points
        player_info['lifetimeScore']['N'] = new_lifetime_score
        player_info['lastScore']['N'] = self.total_score

    def move_on_to_next_word(self):
        """ Update appropriate attributes when moving to the next word """
        setattr(self, 'current_question_index',
                self.current_question_index + 1)
        setattr(self, 'current_clue_index', 0)
        setattr(self, 'current_clue',
                self.questions[self.current_question_index]['clues'][0])

    def get_first_clue(self):
        """ Get the first clue for the current word """
        return self.questions[self.current_question_index]['clues'][0]

    def move_on_to_next_clue(self):
        """ Update appropriate attributes when moving to the next clue """
        setattr(self, 'current_clue_index',
                self.current_clue_index + 1)
        setattr(self, 'current_clue',
                self.questions[self.current_question_index]['clues'][self.current_clue_index])

    def get_customer_id(self):
        """ Get the customerID """
        return self.player_info['customerID']['S']

    def increment_total_games_played(self):
        """ Increment the gamesPlayed counter """
        player_info = self.player_info
        games_played = int(player_info['gamesPlayed']['N']) + 1
        player_info['gamesPlayed']['N'] = games_played

    def update_game_status(self, status):
        """ Changes the state of the game """
        setattr(self, 'game_status', status)

    @property
    def attributes(self):
        """ All attributes """
        return self.__dict__

    def ddb_formatted_attributes(self):
        """ Attributes formatted for sending to DDB """
        return {
            'lifetimeScore': {
                'Value': {
                    'N': str(self.player_info['lifetimeScore']['N'])
                }
            },
            'gamesPlayed': {
                'Value': {
                    'N': str(self.player_info['gamesPlayed']['N'])
                }
            },
            'lastWordPackPlayed': {
                'Value': {
                    'N': str(self.player_info['lastWordPackPlayed']['N'])
                }
            },
            'lastPlayed': {
                'Value': {
                    'S': str(datetime.datetime.utcnow().isoformat())
                }
            },
            'lastScore': {
                'Value': {
                    'N': str(self.total_score)
                }
            }
        }
