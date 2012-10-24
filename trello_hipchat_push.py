from trollop import TrelloConnection
import os
import json
from time import sleep
import requests

HIPCHAT_URL = ("https://api.hipchat.com/v1/rooms/message?format=json&"
                       "auth_token=%s" % os.environ.get('HIPCHAT_TOKEN'))

config = json.loads(open('config.json', 'r').read())


def get_seen_list():
    try:
        return json.loads(open('seen.json', 'r').read())
    except:
        return []


def save_seen(seen):
    open('seen.json', 'w').write(json.dumps(seen))


def send_action_to_hipchat(room_id, action):
    message = unicode(action.creator.fullname)
    card = action._conn.get_card(action.data.get('card').get('id'))
    card_link = "%s (%s)" % (
        action.data.get('card').get('name'),
        card.url,
        )
    if action.type == 'moveCardToBoard':
        message += ' moved %s from %s to %s' % (
                card_link,
                action.data.get('boardSource').get('name'),
                action.data.get('board').get('name')
                )
    elif action.type == 'commentCard':
        message += ' commented on %s: %s' % (
                card_link,
                action.data.get('text')
                )
    elif action.type == 'addAttachmentToCard':
        message += ' added an attachment to %s: %s' % (card_link,
            action.data.get('attachment').get('url'))
    elif action.type == 'addMemberToCard':
        person_added = action._conn.get_member(action.data.get('idMember'))
        message += ' added %s to %s' % (person_added.fullname, card_link)
    elif action.type == 'addChecklistToCard':
        message += ' added the checklist "%s" to %s' % (
                action.data.get('checklist').get('name'),
                card_link
                )
    elif action.type == 'createCard':
        message += ' created the card %s' % card_link
    else:
        message += ' %s %s' % (
                action.type,
                card_link,
                )
    post_data = {
        'room_id': room_id,
        'from': os.environ.get('HIPCHAT_BOT_NAME'),
        'message_format': 'text',
        'message': message
    }
    res = requests.post(HIPCHAT_URL, data=post_data)
    if res.status_code != 200:
        raise ValueError('bad status code from HipChat: %s' % res.status_code,
                post_data)


def main():
    seen = get_seen_list()

    c = TrelloConnection(api_key=os.environ.get('TRELLO_KEY'),
                         oauth_token=os.environ.get('TRELLO_TOKEN'))
    eligible_boards = []
    for board in c.me.boards:
        if board._id in config.get('boards'):
            eligible_boards.append(board)
    if not eligible_boards:
        raise Exception("no trello boards found")

    print "boards to send to hipchat", ', '.join([u'"' + b.name + u'"' for b
                                                  in eligible_boards])
    while True:
        for board in eligible_boards:
            # otherwise the values are all cached and nothing changes
            board._lists = {}
            print board._lists
            for action in reversed(board.actions[:5]):
                if action._id not in seen:
                    for room_id in config.get('boards').get(board._id):
                        send_action_to_hipchat(room_id, action)
                    seen.append(action._id)
                    save_seen(seen)
        sleep(20)

if __name__ == "__main__":
    main()
