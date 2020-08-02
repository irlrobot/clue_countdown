"""
Manage all the data for Code Word
"""
from __future__ import print_function
import datetime
import logging
import boto3
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def create_client():
    """ Create our DynamoDB client object using boto3 """
    logger.debug("=====create_client fired...")
    try:
        session = boto3.Session()
        client = session.client('dynamodb', region_name='us-east-1')
        return client
    except ClientError as err:
        logger.error(
            "[BOTO3_ERROR]Failed to create boto3 client: %s", str(err))


def get_player_info(customer_id, person_id):
    """ Get stats for returning players """
    logger.debug("=====get_player_info fired...")
    client = create_client()

    player = "{}:{}".format(customer_id, person_id)

    response = client.get_item(
        TableName='code_word',
        Key={
            'customerID': {
                'S': player
            }
        }
    )

    logger.debug("=====DDB Query Results: %s", response)

    # If we find a returning player return their profile.
    if 'Item' in response:
        logger.debug("=====found player: %s", str(response['Item']))
        return response['Item']

    logger.debug("=====new customer...")
    return {
        'customerID': {
            'S': player
        },
        'lifetimeScore': {
            'N': '0'
        },
        'gamesPlayed': {
            'N': '0'
        },
        'lastWordPackPlayed': {
            'N': '0'
        },
        'lastScore': {
            'N': '0'
        }
    }


def update_score_and_games(customer_id, score, games_played, last_score):
    """ Update the player's score and games played attribute """
    logger.debug("=====update_last_played_time fired...")
    client = create_client()

    try:
        client.update_item(
            TableName='code_word',
            Key={
                'customerID': {
                    'S': customer_id
                }
            },
            AttributeUpdates={
                'lifetimeScore': {
                    'Value': {
                        'N': str(score)
                    }
                },
                'gamesPlayed': {
                    'Value': {
                        'N': str(games_played)
                    }
                },
                'lastPlayed': {
                    'Value': {
                        'S': datetime.datetime.utcnow().isoformat()
                    }
                },
                'lastScore': {
                    'Value': {
                        'N': str(last_score)
                    }
                }
            }
        )
        return True
    except ClientError as err:
        # log the failure but don't crash
        print("[BOTO3_ERROR]Failed to update table: " + str(err))
        return False


def update_score_games_and_pack(customer_id, score, games_played, last_pack, last_score):
    """update the score, games, and last pack played attribute for the customer"""
    print("=====update_last_played_time fired...")
    client = create_client()

    try:
        client.update_item(
            TableName='code_word',
            Key={
                'customerID': {
                    'S': customer_id
                }
            },
            AttributeUpdates={
                'lifetimeScore': {
                    'Value': {
                        'N': str(score)
                    }
                },
                'gamesPlayed': {
                    'Value': {
                        'N': str(games_played)
                    }
                },
                'lastWordPackPlayed': {
                    'Value': {
                        'N': str(last_pack)
                    }
                },
                'lastPlayed': {
                    'Value': {
                        'S': datetime.datetime.utcnow().isoformat()
                    }
                },
                'lastScore': {
                    'Value': {
                        'N': str(last_score)
                    }
                }
            }
        )
        return True
    except ClientError as err:
        # log the failure but don't crash
        print("[BOTO3_ERROR]Failed to update table: " + str(err))
        return False


def get_others_in_household(household_id, person_id):
    """ Get all personId's for a household other than the current player """
    logger.debug("=====get_others_in_household fired...")
    client = create_client()

    response = client.get_item(
        TableName='code_word_households',
        Key={
            'householdID': {
                'S': household_id
            }
        }
    )

    logger.debug("=====DDB Query Results: %s", response)

    # Return all other people for a given household if a record exists.
    if 'Item' in response:
        logger.debug("=====Household: %s", str(response['Item']))
        people = response['Item']['people']['SS']

        # Remove the current player if they've played before.
        if person_id in people:
            people.remove(person_id)

        # If they are not in the list then we need to add them to the household!
        else:
            add_person_to_household(household_id, person_id)

        return people

    # Otherwise create a new household record and return an empty array.
    logger.debug("=====New household...")
    create_household(household_id, person_id)
    return []


def create_household(household_id, person_id):
    """ Create a new household record in DDB """
    logger.debug("=====create_household fired...")
    client = create_client()

    response = client.update_item(TableName="code_word_households",
                                  Key={'householdID': {'S': household_id}},
                                  UpdateExpression="ADD people :element",
                                  ExpressionAttributeValues={":element": {"SS": [person_id]}})

    return response


def add_person_to_household(household_id, person_id):
    """ Add someone new to a household record in DDB """
    logger.debug("=====add_person_to_household fired...")
    client = create_client()

    response = client.update_item(TableName="code_word_households",
                                  Key={'householdID': {'S': household_id}},
                                  UpdateExpression="ADD people :element",
                                  ExpressionAttributeValues={":element": {"SS": [person_id]}})

    return response
