class PortfolioPerformance(object):
    '''
    Basic class for the storage of performance metrics for portfolios.
    '''

    def __init__(self, longPortfolioReturn : float, shortPortfolioReturn : float, portfolioReturn : float, longShortTurnoverRatio : float):
        self.LongPortfolioReturn = longPortfolioReturn
        self.ShortPortfolioReturn = shortPortfolioReturn 
        self.LongShortPortfolioReturn = longShortPortfolioReturn
        self.LongShortTuroverRatio = longShortTurnoverRatio

