from utils import LOG

class Progress:
    def __init__(self, progress_bar, progress_text):
        self.cur = 0
        self.all = 1
        self.progress_bar = progress_bar
        self.progress_text = progress_text

    def getRate(self):
        return self.cur / self.all

    def addCur(self):
        self.cur += 1
        rate = self.getRate()
        self.progress_bar.progress(rate)
        self.progress_text.text(f'Progress penerjemahan: {int(rate * 100)}%')

    def resetCur(self):
        self.cur = 0

    def setAll(self, value):
        self.all = value
        LOG.info(f'Total tugas yang akan diproses: {value}')
