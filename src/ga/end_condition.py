class MaxTrials:
    def __init__(self, max_trials) -> None:
        self.max_trials = max_trials
        self.num_trials = 0

    def __call__(self):
        self.num_trials += 1
        return self.num_trials > self.max_trials
