from audit.app.util.constants.features import Features


class BasePage:
    def __init__(self, config):
        self.config = config
        self.features = Features(config)

    def run(self):
        raise NotImplementedError("Each page must implement its own `run` method.")
