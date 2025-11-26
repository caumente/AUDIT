from audit.app.util.constants.features import Features
from audit.app.util.constants.metrics import Metrics
from audit.app.util.constants.sidebars import Sidebar


class BasePage:
    def __init__(self, config):
        self.config = config
        self.features = Features(config)
        self.metrics = Metrics()
        self.sidebar = Sidebar(self.features, self.metrics)
        self.template = "light"

    def run(self):
        raise NotImplementedError("Each page must implement its own `run` method.")
