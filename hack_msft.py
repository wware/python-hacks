#!/usr/bin/env python
import sys
import time
import datetime
import os
import csv
import math
import pprint
import functools

TICKERS = [x.strip() for x in """
EIPCX ARCNX EAPCX BICSX BCSAX FLGT DAC
MSFT AMC TSLA NFLX TTM A NVDA B GME WMT BABA DIS
AAPL AMZN GOOG ORCL IBM DELL FB SBUX MU AMAT XLNX PYPL
NMM BGFV CAR SBLK EGLE COF LXU AUOTY OLN
""".split()]

HOUR = 3600
DAY = 24 * HOUR
WEEK = 7 * DAY
YEAR = 365 * DAY

# TICKERS = [x.strip() for x in """
# AAPL AMZN GOOG ORCL
# """.split()]

if len(sys.argv) > 1:
    years = float(sys.argv[1])
else:
    years = 3

TEST_PERIOD = YEAR
t3 = int(time.time())
t2 = int(t3 - TEST_PERIOD)
t1 = int(t2 - years * YEAR)
assert t1 < t2 < t3, (t1, t2, t3)

_cache = {}


def stock_history(ticker, t1, t2):
    assert isinstance(ticker, str), ticker
    assert isinstance(t1, int), t1
    assert isinstance(t2, int), t2
    assert t1 < t2
    url = 'https://query1.finance.yahoo.com/v7/finance/download/{0}?period1={1}&period2={2}&interval=1d&events=history&includeAdjustedClose=true'.format(
        ticker, t1, t2)
    cmd = 'curl -o - \'' + url + '\' 2> /dev/null'
    with os.popen(cmd) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                if row[5] != 'Adj Close':
                    yield ((row[0], float(row[5])))
            except:
                import logging
                logging.exception(row)
                raise


def stream_log(g, sel=None):
    if sel is None:
        sel = lambda x: x
    for x in g:
        x = sel(x)
        assert isinstance(x, float), x
        yield math.log(x)


def stream_mu_sigma(g, sel=None):
    ALPHA = 0.03
    mu = None
    sigmasq = 0.
    if sel is None:
        sel = lambda x: x
    for x in g:
        x = sel(x)
        if mu is None:
            mu = x
        else:
            mu = ALPHA * x + (1. - ALPHA) * mu
        sigmasq = ALPHA * (x - mu) ** 2 + (1. - ALPHA) * sigmasq
        yield (x, mu, sigmasq ** 0.5)


def second((u, v)):
    return v


for a, b, c in stream_mu_sigma(stream_log(stock_history('AMZN', t1, t2), sel=second)):
    print((math.exp(a), b, c))
    if a < b - c:
        print 'BUY'
    elif a > b + c:
        print 'SELL'
sys.exit(0)



def get_log_stock_price(ticker, t1, t2):
    assert isinstance(ticker, str), ticker
    assert isinstance(t1, int), t1
    assert isinstance(t2, int), t2
    assert t1 < t2
    key = (ticker, t1, t2)
    if key not in _cache:
        url = 'https://query1.finance.yahoo.com/v7/finance/download/{0}?period1={1}&period2={2}&interval=1d&events=history&includeAdjustedClose=true'.format(
            ticker, t1, t2)
        cmd = 'curl -o - \'' + url + '\' 2> /dev/null'
        dlst = []
        lst = []
        with os.popen(cmd) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                try:
                    if row[5] != 'Adj Close':
                        dlst.append(row[0])
                        lst.append(math.log(float(row[5])))
                except:
                    import logging
                    logging.exception(row)
                    raise
        assert len(lst) > 0, cmd
        _cache[key] = (dlst, lst)
    return _cache[key]


@functools.total_ordering
class MomentumModel(object):
    def __init__(self, name, lst):
        assert len(lst) > 0
        self.name = name
        sumx = sumy = sumxsq = sumysq = sumxy = 0.
        n = 0
        for y in lst:
            sumx += n
            sumy += y
            sumxsq += n ** 2
            sumysq += y ** 2
            sumxy += n * y
            n += 1
        self._n = n
        assert (n * sumxsq - sumx ** 2) > 0., (n, sumxsq, sumx)
        self._A = A = (n * sumxy - sumx * sumy) / (n * sumxsq - sumx ** 2)
        self._B = B = (sumy - A * sumx) / n
        esq = sumysq + A**2 * sumxsq + B**2 * n - 2*A*sumxy - 2*B*sumy + 2*A*B*sumx
        assert esq >= 0., esq
        self._sigma = (esq / n) ** 0.5

    def __lt__(self, other):
        assert isinstance(other, MomentumModel)
        return self._A < other._A

    def __eq__(self, other):
        assert isinstance(other, MomentumModel)
        return self._A == other._A

    def __repr__(self):
        return "<{0} {1} {2} {3}>".format(self.name, self._A, self._B, self._sigma)

    def predict(self, x):
        return self._A * x + self._B

    @property
    def sigma(self):
        return self._sigma

    @property
    def n(self):
        return self._n

    @classmethod
    def test(cls):
        m = cls('foo', [1, 2, 4, 5])
        print(m)
        print(m.predict(4))
        sys.exit(0)


# MomentumModel.test()


lst = []
for ticker in TICKERS:
    m = MomentumModel(ticker, get_log_stock_price(ticker, t1, t2)[1])
    lst.append(m)
lst.sort(reverse=True)

for m in lst:
    ticker = m.name
    t = t2
    dlst, xlst = get_log_stock_price(ticker, t2, t3)
    for i, y in enumerate(xlst):
        yt = m.predict(i + m.n)
        s = math.exp(yt + m.sigma) - math.exp(yt)
        # gap = 0.5 * s
        gap = 2 * s
        y, yt = math.exp(y), math.exp(yt)
        order = (
            "BUY" if y < yt - gap
            else (
                "SELL" if y > yt + gap
                else ""
            )
        )
        print("{0} {1} {2:.2f} {3} {4} {5}".format(
            ticker, dlst[i], y, yt, s, order
        ))
        t += DAY
