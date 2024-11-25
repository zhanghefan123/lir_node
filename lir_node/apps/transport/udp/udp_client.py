from apps.user import user_input as uim


class UdpClient:
    def __init__(self, user_input: uim.UserInput):
        self.user_input = user_input

    def start(self):
        user_input = uim.UserInput()
