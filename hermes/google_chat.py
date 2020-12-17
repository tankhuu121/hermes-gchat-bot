import json
import random
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
import requests


class GoogleChat:
  def __init__(self):
    self.KEYFILE = 'KarrosHermes-22b221b76b8a.json'
    self.SCOPES = 'https://www.googleapis.com/auth/chat.bot'
    self.CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_name(
        self.KEYFILE, self.SCOPES)
    self.CHAT = build(
        'chat', 'v1', http=self.CREDENTIALS.authorize(Http()), cache_discovery=False)
    self.DEFAULT_MESSAGES = ['Have a nice day!', "What's up!",
                              "I'm feeling unsettled today!", "There's a cow next to the window."]
    self.HERMES_ROOM = 'AAAAe1Zy3YM'
    self.HERMES_LOGO_URL = 'https://edulogvn-devops.s3.us-east-2.amazonaws.com/resource/avatar/hermes.jpg'
    self.HERMES_APP_URL = 'https://hermes.karrostech.io'
    self.BACKEND_URL = 'https://hermes-be.karrostech.net'

    with open('default_messages.json') as dm:
      if dm:
        messages = json.load(dm).get('messages')
        if messages:
          self.DEFAULT_MESSAGES = messages
        # print('GoogleChat.DEFAULT_MESSAGES', self.DEFAULT_MESSAGES)

  def extract_command(self, text: str):
    command_detail = text.split(':')
    command = command_detail.pop(0).strip().lower()

    if command:
      return {'command': command, 'command_detail': ' '.join(command_detail)}

    return {}

  def create_cards(self, content: dict):
    """ Google Chat Cards Message Format Create

    Args:
      content (dict): {
        'title': '',
        'subtitle': '',
        'main': {
          'title': '',
          'content': ''
        },
        'second': {
          'title': '',
          'content': ''
        },
        'button': {
          'icon': '',
          'iconUrl': '',
          'text': '',
          'link': ''
        }
      }

    Raises:
      err: format cards failure

    Returns:
      dict: formatted cards
    """
    try:
      header = {
        "title": content.get('title'),
        "subtitle": content.get('subtitle'),
        "imageUrl": self.HERMES_LOGO_URL,
        "imageStyle": "IMAGE"
      }

      if not header.get('title'):
          header['title'] = "Hermes is with your work"
      if not header.get('subtitle'):
          header['subtitle'] = "hermes-bot@karrostech.com"

      # print('header', header)

      cards = []
      card_detail = {}
      card_button = {}

      main_content = content.get('main')
      second_content = content.get('second')
      button = content.get('button')

      if main_content or second_content:
        card_detail = {"widgets": []}
        if main_content:
          main = {
            "keyValue": {
              "topLabel": main_content.get('title'),
              "content": main_content.get('content')
            }
          }
          card_detail['widgets'].append(main)

        if second_content:
          second = {
            "keyValue": {
              "topLabel": second_content.get('title'),
              "content": second_content.get('content')
            }
          }
          card_detail['widgets'].append(second)

      if button:
        card_button = {
          "widgets": [
            {
              "buttons": [
                {
                  "imageButton": {
                    "iconUrl": button.get('icon'),
                    "onClick": {
                      "openLink": {
                        "url": button.get('iconLink')
                      }
                    }
                  }
                },
                {
                  "textButton": {
                    "text": button.get('text'),
                    "onClick": {
                      "openLink": {
                        "url": button.get('link')
                      }
                    }
                  }
                }
              ]
            }
          ]
        }

      if card_detail or card_button:
        cards = [{
          'header': header,
          "sections": [
            {**card_detail},
            {**card_button}
          ]}]

      # print('GC.create_card.cards', cards)

      return cards
    except Exception as err:
      print('GC.create_card.error', err)
      raise err

  def reply_message(self, code=200, text: str = '', cards: list = []):
    try:
      body = {}
      if text:
        body = {'text': text}
      elif cards:
        body = {'cards': cards}

      print('GC.reply_message.body', body)
      return {
        "statusCode": code,
        "body": json.dumps(body),
      }
    except Exception as err:
        print('GC.reply_message.error', err)
        raise err

  def reply_default(self):
      return self.reply_message(200, random.choice(self.DEFAULT_MESSAGES))

  def send_message(self, target_id: str, text: str = '', cards: list = []):
    try:
      body = {}

      # build body
      if text:
        body = {"text": text}
      elif cards:
        body = {"cards": cards}

      resp = self.CHAT.spaces().messages().create(
        parent=f'spaces/{target_id}', body=body).execute()

      # print('GC.send_message.resp', resp)
      return self.reply_default()
    except Exception as err:
      print('GC.send_message.error', err)
      raise err

  def send_card_message(self, target_id: str, id: str, name: str, message: str):
    try:
      sla_url = f'{self.HERMES_APP_URL}/#/sla/detail/{id}'
      body = {}

      card_content = {
        'title': "Message from Hermes",
        'subtitle': 'Powered by @Kupids',
        'main': {
            'title': 'SLA',
            'content': name
        },
        'second': {
            'title': 'Result',
            'content': message
        },
        'button': {
            'icon': self.HERMES_LOGO_URL,
            'iconLink': self.HERMES_APP_URL,
            'text': 'SLA Detail',
            'link': sla_url
        }
      }
      cards = self.create_cards(card_content)
      body = {"cards": cards}
      resp = self.CHAT.spaces().messages().create(
        parent=f'spaces/{target_id}', body=body).execute()

      print('GC.send_message.resp', resp)
      return self.reply_default()

    except Exception as err:
      print('GC.send_card_message.error', err)
      raise err

  def send_notification(self):
    pass

  def handle_message(self, space: str, message: dict):
    try:
      print('message', message)
      text = message.get('text')
      if not text:
        return self.reply_default()

      sender = message.get('sender')
      if sender:
        # won't handler message from non human
        sender_type = sender.get('type')
        if sender_type != 'HUMAN':
            return self.reply_default()

        sender_name = sender.get('displayName')
        email = sender.get('email')
        text = message.get('argumentText')

        message_content = self.extract_command(text)
        print('message_content', message_content)
        command = message_content.get('command')
        command_detail = message_content.get('command_detail')
        print('command_detail', command_detail)

        if command:
        # if command and command_detail:
          if command == 'sla':
            sla_name = command_detail

            if sla_name:
              resp_message = "Hi there! Hermes is not here now, please leave the message after he comes back!"
              source = 'CHAT_BOT'
              url = f'{self.BACKEND_URL}/api/v1/sla/execute'
              headers = {'Content-Type': 'application/json'}
              request_body = {'name': sla_name, 'source': source}

              # message = f"Your {profile} is still working well! Congratulations!"
              resp = requests.post(url, headers=headers, data=json.dumps(request_body))
              print('resp', resp.json())
              resp_message = resp.json().get('result').get('summary')
              card_content = {
                'title': f"Hermes got the result",
                'subtitle': 'Powered by @Kupids',
                'main': {
                    'title': 'SLA',
                    'content': sla_name
                },
                'second': {
                    'title': 'Result',
                    'content': resp_message
                },
                'button': {
                    'icon': self.HERMES_LOGO_URL,
                    'iconLink': self.HERMES_APP_URL,
                    'text': 'View more SLA',
                    'link': f'{self.HERMES_APP_URL}/#/dashboard'
                }
              }
              cards = self.create_cards(card_content)
              return self.reply_message(code=200, cards=cards)
          if command == 'list' or command == 'show':
            source = 'CHAT_BOT'
            url = f'{self.BACKEND_URL}/api/v1/sla'

            # message = f"Your {profile} is still working well! Congratulations!"
            resp = requests.get(url)
            print('resp', resp.json())
            sla_list = resp.json().get('result')
            print('sla_list', sla_list)
            resp_message = ''
            for sla in sla_list:
              name = sla.get('name')
              last_execution = sla.get('lastExecution')
              if last_execution.get('success'):
                status = 'Success'
              else:
                status = 'Failure'
              resp_message += f"{name}: {status}\n"
            card_content = {
              'title': f"Hermes got the list SLA",
              'subtitle': 'Powered by @Kupids',
              'main': {
                  'title': 'Total',
                  'content': f'{len(sla_list)} SLA'
              },
              'second': {
                  'title': 'Last Execution',
                  'content': resp_message
              },
              'button': {
                  'icon': self.HERMES_LOGO_URL,
                  'iconLink': self.HERMES_APP_URL,
                  'text': 'View more SLA',
                  'link': f'{self.HERMES_APP_URL}/#/dashboard'
              }
            }
            cards = self.create_cards(card_content)
            return self.reply_message(code=200, cards=cards)
      return self.reply_default()
    except Exception as err:
        print('GC.handle_message.error', err)
        raise err
