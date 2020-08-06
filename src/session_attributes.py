"""
Manages session attributes during the game
"""
import datetime


class SessionAttributes():
    """ Session Attributes manager """

    def __init__(self, attributes):
        self.__dict__ = attributes

    @property
    def attributes(self):
        """ All attributes """
        return self.__dict__

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
        new_total_score = int(self.total_score) + int(additional_points)
        new_lifetime_score = int(
            self.player_info['lifetimeScore']['N']) + additional_points

        setattr(self, 'total_score', new_total_score)
        self.player_info['lifetimeScore']['N'] = new_lifetime_score
        self.player_info['lastScore']['N'] = self.new_total_score

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

    def get_last_played_work_pack_id(self):
        """ Return the id of the last played word pack """
        try:
            return int(self.player_info['lastWordPackPlayed']['N'])
        except KeyError as _err:
            # If the lastWordPackPlayed key is missing we
            # just set play_newest_word_pack to True.
            self.update_last_word_pack_played(0)
            return int(self.player_info['lastWordPackPlayed']['N'])

    def should_play_newest_word_pack(self, newest_pack_id):
        """ Return whether or not the player
        should play the newest word pack """
        if self.get_last_played_work_pack_id() < newest_pack_id:
            return True

        return False

    def setup_new_game_attributes(self, questions, play_newest_word_pack):
        """ Setup game attributes when starting a new game """
        attributes = {
            "questions": questions,
            "total_score": 0,
            "current_question_index": 0,
            "current_clue_index": 0,
            "game_length": len(questions),
            "game_status": "in_progress",
            "current_clue": questions[0]['clues'][0],
            "play_newest_word_pack": play_newest_word_pack
        }

        for key, value in attributes.items():
            setattr(self, key, value)
