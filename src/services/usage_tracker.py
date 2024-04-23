class UsageTracker:
    def __init__(self):
        self.usage = 0
        pass

    def add_usage(self, usage: int):
        self.usage += usage
