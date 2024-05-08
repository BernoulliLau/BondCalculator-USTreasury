# -*- coding: utf-8 -*-
"""USTreasurySecurity.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1tdXDImuqsOZWp4huAinjWWaPES_CNoQe
"""

import numpy as np
class FixedIncomeSecurities:
  def __init__(self, N=None, P=None, r=None, y=None, c=None, TimesPerYear=2, quoteString = ""):

    """
    N: number of coupon periods
    P: the bond price, P
    r: periodic discounting rate
    y: the yield to maturity
    c: periodic coupon
    """
    self.N = N
    self.P = P
    self.r = r
    self.y = y
    self.c = c
    self.TimesPerYear = TimesPerYear
    self.quoteString = quoteString

  def getPrice(self, N, r, c):
    """
    N: number of coupon periods
    r: periodic discounting rate
    c: periodic coupon
    """

    bondValue = 0
    couPay = self.c/self.TimesPerYear
    rate = self.r/(100 * self.TimesPerYear)

    for i in range(1, self.N + 1):
      bondValue += couPay/((1 + rate) ** i)
    bondValue += 100/((1 + rate) ** self.N)

    return bondValue

  def getPV01(self, N, r, c):
    """
    N: number of coupon periods
    r: periodic discounting rate
    c: periodic coupon
    dec: one basis point change in YTM.

    """
    dec = -0.01# In 1 year rate

    originP = self.getPrice(N, r, c)
    newRate = self.r + dec
    newP = self.getPrice(N, newRate, c)
    dP = originP - newP
    dr = dec/200
    priceChange = dP/dr
    delta = priceChange * (-0.005)
    print('The PV01 of bond is: ', + delta)
    return delta

  def getDerivative(self,Yield):
    """
    change: various conditions of r(%) input by user.
    """
    cashFlow = []
    length = self.N
    couPay = self.c/self.TimesPerYear
    for i in range(length - 1):
      cashFlow.append(couPay)
    cashFlow.append(couPay + self.P)
    # cashFlow is the cash flow process

    value = self.P * 1
    for j in range(length):
      value -= cashFlow[j] / ((1+Yield/self.TimesPerYear)**(1+j))

    d_value = 0
    for k in range(length):
      d_value += cashFlow[k] * (1/self.TimesPerYear) * (1+k) * (1+Yield/self.TimesPerYear) ** (-k - 2)

    d2_value = 0
    for m in range(length):
      d2_value += cashFlow[m] * (1/self.TimesPerYear**2) * (1+m) * (-m-2) * (1+Yield/self.TimesPerYear) ** (-m-3)

    return value, d_value, cashFlow, d2_value




  def getYTM(self,N,P,c):

    y = 0
    precision = 1.0E-14
    max_iter = 1000

    for i in range(max_iter):
      f_value, fd_values, _ ,_ = self.getDerivative(y)
      y_new = y - f_value/fd_values
      if abs(y_new - y) < precision:
        print('We get to there!')
        return y_new
      y = y_new

      #print(y)
      #print("——————————————————————")
    return y

  def getMacaulayDur(self, N, P, y, c):

    realYield = self.y / (100 * self.TimesPerYear)
    _, _, cashFlow, _ = self.getDerivative(realYield)
    print(cashFlow)

    num = 0
    weightedPV = 0
    totalPV = 0
    for i in np.arange(0 + 1/self.TimesPerYear, self.N/self.TimesPerYear + 0.1, 1/self.TimesPerYear):
      weightedPV += (cashFlow[num] * i)/((1+realYield)**i)
      totalPV += cashFlow[num]/((1+realYield)**i)
      num += 1

    result = weightedPV/totalPV
    #print(result)
    return result

  def getModDur(self, N, P, y, c):
    modDur = self.getMacaulayDur(N, P, y, c)/(1 + self.y/self.TimesPerYear)
    #print(modDur)
    return modDur

  def getConvexity(self, N, P, c):
    _, _, _, d2_value = self.getDerivative(self.y)

    convex = d2_value/self.P
    #print(convex)
    return convex

  def parseQuote(self, quoteString):
    parts = self.quoteString.split('-')
    base = int(parts[0])
    cent1 = int(parts[1].split('+')[0])/32
    length = len(parts[1].split('+'))
    for i in range(1,length):
        cent1 += 1/(32*(2**i))
    #print(cent1+base)
    return cent1+base

  def getCleanPrice(self):
    parts = self.quoteString.split('-')
    base = int(parts[0])
    cent1 = int(parts[1].split('+')[0])/32
    length = len(parts[1].split('+'))
    for i in range(1,length):
        cent1 += 1/(32*(2**i))
    cleanPrice = cent1+base

    return cleanPrice

c = 8
N = 10
P = 100
y = 1
r = 3
quoteString = '100-24++'
TimesPerYear = 2
print(np.arange(0+1/TimesPerYear, N/TimesPerYear+0.1, 1/TimesPerYear))

objec = FixedIncomeSecurities(N, P, r, y, c, TimesPerYear,quoteString)
objec.getYTM(N, P, c)
objec.getMacaulayDur(N, P, y, c)
objec.getModDur(N, P, y, c)
objec.getConvexity(N, P, c)
objec.parseQuote(quoteString)

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class USTreasurySecurity(FixedIncomeSecurities):
  def __init__(self, quoteString, N, a, tradeDate, prevCouponDate, nextCouponDate, holidayCalendar):
    super().__init__(quoteString=quoteString)

    #self.quoteString = quoteString
    self.N = N
    self.a = a
    self.tradeDate = tradeDate
    self.prevCouponDate = prevCouponDate
    self.nextCouponDate = nextCouponDate
    self.holidayCalendar = holidayCalendar

  def dateProcessing(self):

    tradeD = datetime.strptime(self.tradeDate, '%d-%m-%Y')
    prevCouponD = datetime.strptime(self.prevCouponDate, '%d-%m-%Y')
    nextCouponD = datetime.strptime(self.nextCouponDate, '%d-%m-%Y')

    holidays = []
    with open(self.holidayCalendar, 'r') as file:
      for line in file:
        dateStr = line.strip()
        dateObj = datetime.strptime(dateStr, "%d-%m-%Y")
        holidays.append(dateObj)

    settleTemp = tradeD + timedelta(days=1)

    while (settleTemp in holidays) or (settleTemp.weekday() > 4):
      settleTemp += timedelta(days=1)
    settleD = settleTemp

    z = (nextCouponD - settleD).days + 1
    x = (nextCouponD - prevCouponD).days

    countZ, countX = 0,0

    for holiday in holidays:
      if holiday >= settleD and holiday <= nextCouponD:
        countZ += 1
      if holiday > prevCouponD and holiday < nextCouponD:
        countX += 1
    z -= countZ
    #x -= countX
    #print('z,x,settleD,prevCouponD,daysBetween:',z, x, settleD,prevCouponD,abs(prevCouponD - settleD).days)


    return z, x, settleD,prevCouponD

  def getCleanPrice(self):

    return super().getCleanPrice()

  def getDirtyPrice(self):
    z,x,settleD,prevCouponD = self.dateProcessing()

    daysBetween = abs(prevCouponD - settleD).days
    accruedInterest = self.a/2 * daysBetween/x
    dirtyPrice = self.getCleanPrice() + accruedInterest
    return dirtyPrice

  def __getPrice(self,r):
    z,x,settleD,prevCouponD = self.dateProcessing()

    couponPay = self.a/2
    bondPrice = 0
    rate = r/200

    for i in range(0,self.N):
      bondPrice += couponPay/((1+rate)**(i+z/x))
    bondPrice += 100/((1+rate)**(self.N - 1 + z/x))
    return bondPrice

  def calculatePrice(self, r):

    return self.__getPrice(r)

  def getDerivative(self, ytm):
    z,x,settleD,prevCouponD = self.dateProcessing()

    length = self.N
    couponPay = self.a/2

    # value of f
    value = 0

    for j in range(self.N):
      value +=  couponPay / ((1 + ytm/2)**(j + z/x))
    value += 100/((1 + ytm/2)**(self.N-1+z/x))

    # value of d_f
    d_value = 0
    for k in range(self.N):
      d_value += couponPay*(k + z/x) /((1 + ytm/2)**(k + z/x +1))
    d_value *= -1/2
    d_value += (-100/2) * (self.N + z/x -1)/(1+ytm/2)**(self.N + z/x)

    # value of d2_f
    d2_value = 0
    for m in range(self.N):
      d2_value += -1/4 *couponPay*(m + z/x) * (-m - z/x -1) *(1+ytm/2)**(-m -z/x-2)
    d2_value += -100/4 *(self.N + z/x -1)*(-self.N - z/x)*(1+ytm/2)**(-self.N -z/x -1)

    return value, d_value, d2_value

  def getYTM(self):

    y = 0
    precision = 1.0E-14
    max_iter = 1000
    P = self.getDirtyPrice()

    for _ in range(max_iter):
      f_value, fd_values, _ = self.getDerivative(y)
      y_new = y - (f_value - P)/fd_values
      if abs(y_new - y) < precision:
        #print('We get to there!')
        return y_new*100
      y = y_new
    return y*100

  def getPV01(self):
    ytm = self.getYTM()
    delta = 0.01
    value1 = self.__getPrice(ytm + delta)
    value2 = self.__getPrice(ytm - delta)
    pv01 = (value2 - value1)/2
    return pv01

  def getModDur(self):
    P = self.getDirtyPrice()
    ytm = self.getYTM()/100

    _,fd_value,fd2_value = self.getDerivative(ytm)
    modDuration = -fd_value/P
    return modDuration

  def getMacaulayDur(self):
    modDuration = self.getModDur()
    ytm = self.getYTM()/200
    macaulayDur = modDuration * (1+ytm)
    return macaulayDur

  def getConvexity(self):
    P = self.getDirtyPrice()
    ytm = self.getYTM()/100
    _, _, fd2_values = self.getDerivative(ytm)
    convexity = fd2_values/P
    return convexity

quoteString = '101-19+'
N = 10
a = 4.125
tradeDate = "17-08-2007"
prevCouponDate = "15-08-2007"
nextCouponDate = "15-02-2008"
holidayCalendar = 'holidayCalendar.txt'
sec = USTreasurySecurity(quoteString, N, a, tradeDate, prevCouponDate, nextCouponDate, holidayCalendar)

print("New case")
print(sec.dateProcessing())
print("_________")
print("The YTM is:",+sec.getYTM())
print("The PV01 is:",+sec.getPV01())
print("The modified duration is:",+sec.getModDur())
print("_________")
print("The dirty price is:",+sec.getDirtyPrice())
print("The macaulay duration is:",+sec.getMacaulayDur())
print("_________")
print("The convexity is:",+sec.getConvexity())
print("The clean price is:",+sec.getCleanPrice())
print("_________")

print("New case")
quoteString = '101-19+'
N = 16
a = 4.65
tradeDate = "17-08-2007"
prevCouponDate = "15-08-2007"
nextCouponDate = "15-02-2008"
holidayCalendar = 'holidayCalendar.txt'
sec = USTreasurySecurity(quoteString, N, a, tradeDate, prevCouponDate, nextCouponDate, holidayCalendar)

print(sec.dateProcessing())
print("_________")
print("The YTM is:",+sec.getYTM())
print("The PV01 is:",+sec.getPV01())
print("The modified duration is:",+sec.getModDur())
print("_________")
print("The dirty price is:",+sec.getDirtyPrice())
print("The macaulay duration is:",+sec.getMacaulayDur())
print("_________")
print("The convexity is:",+sec.getConvexity())
print("The clean price is:",+sec.getCleanPrice())
print("_________")

print("New case")
quoteString = '101-19+'
N = 20
a = 4.75
tradeDate = "20-08-2007"
prevCouponDate = "15-08-2007"
nextCouponDate = "15-02-2008"
holidayCalendar = 'holidayCalendar.txt'
sec = USTreasurySecurity(quoteString, N, a, tradeDate, prevCouponDate, nextCouponDate, holidayCalendar)

print(sec.dateProcessing())
print("_________")
print("The YTM is:",+sec.getYTM())
print("The PV01 is:",+sec.getPV01())
print("The modified duration is:",+sec.getModDur())
print("_________")
print("The dirty price is:",+sec.getDirtyPrice())
print("The macaulay duration is:",+sec.getMacaulayDur())
print("_________")
print("The convexity is:",+sec.getConvexity())
print("The clean price is:",+sec.getCleanPrice())
print("_________")

print("New case")
quoteString = '102-16+'
N = 60
a = 5.0
tradeDate = "20-08-2007"
prevCouponDate = "15-05-2007"
nextCouponDate = "15-11-2007"
holidayCalendar = 'holidayCalendar.txt'
sec = USTreasurySecurity(quoteString, N, a, tradeDate, prevCouponDate, nextCouponDate, holidayCalendar)

print(sec.dateProcessing())
print("_________")
print("The YTM is:",+sec.getYTM())
print("The PV01 is:",+sec.getPV01())
print("The modified duration is:",+sec.getModDur())
print("_________")
print("The dirty price is:",+sec.getDirtyPrice())
print("The macaulay duration is:",+sec.getMacaulayDur())
print("_________")
print("The convexity is:",+sec.getConvexity())
print("The clean price is:",+sec.getCleanPrice())
print("_________")