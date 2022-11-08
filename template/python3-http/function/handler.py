def handle(event, context):
     """handle a request to the function
    Args:
        req (str): request body
        context (???): function context
   """
   return {
        "statusCode": 200,
        "body": "Hello from OpenFaaS!"
    }
