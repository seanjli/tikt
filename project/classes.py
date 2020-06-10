class Problem:
    def __init__(self, prob_id, title, tags, subject, diff, statement, link, answer):
        self.prob_id = prob_id
        self.title = title
        self.tags = tags
        self.subject = subject
        self.diff = diff
        self.statement = statement
        self.link = link
        self.answer = answer

    def __repr__(self):
        return "{problem: " + self.title + "}"

