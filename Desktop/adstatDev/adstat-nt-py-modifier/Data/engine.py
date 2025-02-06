class SearchEngine:
    def __init__(self, id, link, xpath):
        self.id = id
        self.link = link
        self.xpath = xpath

    @staticmethod
    def getEngines():
        engines = []
        engines.append(SearchEngine('google', 'https://www.google.com/search?q=', '//div[@class="r"]//a'))
        return engines
