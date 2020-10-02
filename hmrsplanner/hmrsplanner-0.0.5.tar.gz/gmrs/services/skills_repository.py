
class SkillRepository:
    def __init__(self):
        self.repo = {}

    def queryFromTaskName(self, taskName):
        ref = self.normalizeName(taskName)
        return ref

    def register(self, taskName, skill):
        ref = self.normalizeName(taskName)
        if self.repo[ref] is None:
            self.repo[ref] = []
        self.repo[ref].append(skill)

    def normalizeName(self, taskName):
        return taskName
