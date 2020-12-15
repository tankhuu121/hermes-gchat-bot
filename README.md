# Hermes

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- hermes - Code for the application's Lambda function.
- events - Invocation events that you can use to invoke the function.
- tests - Unit tests for the application code.
- template.yaml - A template that defines the application's AWS resources.

The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

## Features

- Check the SLA
- Check status on-demand: service, api, website
- Create SLA

## Intents

check profile

story of hermes

## Training phrases

## Action

- send request to check sla
- send the introduction about Hermes

## Parameters

- sla_name:
  - entity_type: string
- service_name:
  - entity_type: string
- website_url:
  - entity_type: @sys.url
- api

## Responses

Text, speech, or visual responses to return to the end-user.

![Intent Match Respond Basic](./images/intent-match-respond-basic.svg)

## Contexts

![Context](./images/contexts-overview.svg)

## Follow-up intents

## Dialogflow Hangouts integration
