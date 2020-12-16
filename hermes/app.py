import json
from google_chat import GoogleChat

# import requests


def lambda_handler(event, context):
  """Pure Lambda function

  Parameters
  ----------
  event: dict, required
      API Gateway Lambda Proxy Input Format

      Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

  context: object, required
      Lambda Context runtime methods and attributes

      Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

  Returns
  ------
  API Gateway Lambda Proxy Output Format: dict

      Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
  """

  # try:
  #     ip = requests.get("http://checkip.amazonaws.com/")
  # except requests.RequestException as e:
  #     # Send some context about this error to Lambda Logs
  #     print(e)

  #     raise e

  APP_NAME = 'Hermes'
  try:
    print(f'{APP_NAME}.event', event)

    GC = GoogleChat()
    body = event.get('body')
    if body:
      content = json.loads(body)
      room_id = content.get('roomId')
      sla_id = content.get('slaId')
      sla_name = content.get('slaName')
      message = content.get('message')

      # handle simple call Jarvis
      if room_id:
        if message:
          return GC.send_card_message(target_id=room_id, id=sla_id, name=sla_name, message=message)
        else:
          return GC.send_message(target_id=room_id, text=message)
        # message = json.loads(body).get('message')
        # if message:
        #     return GC.handle_message(message)

    return GC.reply_default()

  except Exception as err:
    print(f"{APP_NAME}.error", err)
    raise err
