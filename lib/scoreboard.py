import json
import os

class Scoreboard:
    def __init__(self):
        self.scores_file = "highscores.json"
        self.high_scores = self.load_scores()

    def load_scores(self):
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_score(self, score):
        self.high_scores.append(score)
        self.high_scores.sort(reverse=True)
        self.high_scores = self.high_scores[:10]  # 只保留前10名
        
        with open(self.scores_file, 'w') as f:
            json.dump(self.high_scores, f)

    def get_high_scores(self):
        return self.high_scores
