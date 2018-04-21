from cc_settings import Settings
import ccxt


class Information(Settings):

    def __init__(self):
        super().__init__()
        self.exchanges = {
            "bitmex": {
                "api_key": self.api_key,
                "secret": self.api_secret
            },
        }
        self.bitmex = ccxt.bitmex()
        self.bitmex.apiKey = self.exchanges["bitmex"]["api_key"]
        self.bitmex.secret = self.exchanges["bitmex"]["secret"]
