

class Websocket(object):

    def __init__(self, receiver_id):
        self.receiver_id = receiver_id

    def send(cls, message):
        url = "https://gouhuoapp.com/amumu/server_to_client/"
        _ = {"path": "/amumu/websocket/%s/" % self.receiver_id, "message": message, "type": 1}
        data = {"data": json.dumps(_)}
        requests.post(url, data=data)
