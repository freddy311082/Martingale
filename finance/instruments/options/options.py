from abc import ABC, abstractmethod
from math import exp, sqrt

from martingale.finance.instruments import Pricer
from enum import Enum


class BinomialTreePricer(Pricer):

    def __init__(self):
        super(BinomialTreePricer, self).__init__()
        self.steps = 0
        self.option = None
        self.u = self.d = 0
        self.cache = {}

    def setup(self, steps, option):
        self.cache = {}
        self.steps = steps
        self.option = option

    def price_in_steps(self, j, m):
        if (j, m) in self.cache:
            return self.cache[(j, m)]

        if m == self.option.steps:
            self.cache[(j, m)] = self.option.FSm(j, m)

        else:
            discount_factor = exp(-self.option.rate * self.option.delta_t())
            p = self.option.probability()
            self.cache[(j, m)] = discount_factor * (
                    p * self.price_in_steps(j + 1, m + 1) + (1 - p) * self.price_in_steps(j, m + 1))

        return self.cache[(j, m)]

    def price(self):
        return self.price_in_steps(0, 0)


class PricerType(Enum):
    BINOMIAL_TREE = BinomialTreePricer

    def pricer_object(self):
        return self.value()


class Option(ABC):

    def __init__(self,
                 stock_price,
                 strike_price_up,
                 rate,
                 maturity,
                 volatility,
                 steps,
                 strike_price_down=0,
                 pricer_type=PricerType.BINOMIAL_TREE):
        self.option_price_cache = {}
        self.pricer_type = pricer_type

        self.stock_price = stock_price
        self.strike_price_up = strike_price_up
        self.strike_price_dow = strike_price_down
        self.rate = rate
        self.maturity = maturity
        self.volatility = volatility
        self.steps = steps
        self.u = 1 + self.volatility * sqrt(self.delta_t())
        self.d = 1 - self.volatility * sqrt(self.delta_t())

    def probability(self):
        return (exp(self.rate * self.delta_t()) - self.d) / (self.u - self.d)

    def delta_t(self):
        return self.maturity / self.steps

    def Sm(self, j, m):
        return self.stock_price * pow(self.u, j) * pow(self.d, m - j)

    def max_value(self):
        return 0

    @abstractmethod
    def FSm(self, j, m):
        pass

    def _calculate_price(self, j, m):
        if (j, m) not in self.option_price_cache:
            pricer = self.pricer_type.pricer_object()
            pricer.setup(
                steps=self.steps,
                option=self
            )

            self.option_price_cache[(j, m)] = pricer.price_in_steps(j, m)

        return self.option_price_cache[(j, m)]

    def price(self, clean_cache=False):
        if clean_cache:
            self.option_price_cache.clear()

        return self._calculate_price(0, 0)


class EuropeanCallOption(Option):

    def FSm(self, j, m):
        return max(self.Sm(j, m) - self.strike_price_up, self.max_value())


class EuropeanPutOption(Option):

    def FSm(self, j, m):
        return max(self.strike_price_up - self.Sm(j, m), self.max_value())


class AmericanOption(Option):

    @abstractmethod
    def _max_value(self, j, m):
        pass

    def FSm(self, j, m):
        if m == self.steps:
            return max(self.Sm(j, m) - self.strike_price_up, 0)

        p = self.probability()
        v_j1n1 = self._calculate_price(j + 1, m + 1)
        v_jn1 = self._calculate_price(j, m + 1)

        return max(self._max_value(),
                   exp(-self.rate * self.delta_t()) * (p * v_j1n1) + (1 - p) * v_jn1)


class AmericanCallOption(AmericanOption):
    def _max_value(self, j, m):
        return self.Sm(j, m) - self.strike_price_up


class AmericanPutOption(AmericanOption):
    def _max_value(self, j, m):
        return self.strike_price_up - self.Sm(j, m)


if __name__ == '__main__':
    a = AmericanCallOption(stock_price=60,
                           strike_price_up=62,
                           rate=0.06,
                           maturity=0.5,
                           volatility=0.13,
                           steps=5)
    print(a.price())

    a = EuropeanCallOption(stock_price=60,
                           strike_price_up=62,
                           rate=0.06,
                           maturity=0.5,
                           volatility=0.13,
                           steps=5)
    print(a.price())
