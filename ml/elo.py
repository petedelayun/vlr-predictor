class ELO:
    def __init__(self, k=32, initial=1500):
        self.k = k
        self.ratings = {}
        self.initial = initial

    def get_rating(self, team_id):
        return self.ratings.get(team_id, self.initial)

    def expected(self, rating_a, rating_b):
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def update(self, team_a, team_b, team_a_won):
        rating_a = self.get_rating(team_a)
        rating_b = self.get_rating(team_b)

        expected_a = self.expected(rating_a, rating_b)
        actual_a = 1.0 if team_a_won else 0.0

        self.ratings[team_a] = rating_a + self.k * (actual_a - expected_a)
        self.ratings[team_b] = rating_b + self.k * ((1 - actual_a) - (1 - expected_a))

    def predict(self, team_a, team_b):
        return self.expected(self.get_rating(team_a), self.get_rating(team_b))
