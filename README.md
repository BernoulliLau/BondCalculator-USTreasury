# BondCalculator-USTreasury
⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️
In the first class: FixedIncomeSecurity, the basic metrics of treasury bonds are calculated, with the time stamp being the year.
In the second class: USTreasurySecurity, I consider the real dates and time is processed in the rule:
There are 3 time stamps need to be given: trade date, previous coupon payment date and next coupon payment date.
Due to T+1, the day after trade date is the settlement date. Settlement date could not be holiday or weekend days.
The days between settlement date and next coupon payment date should be counted excluding the holidays.
While the days between next coupon payment date and previous coupon payment date are directly get by substraction.
For dirty price, it is calculated as: abs(prevCouponD - settleD)/(nextCouponD - prevCouponD) * semi-annualy coupon payment.

In USTreasurySecurity class, the date can be implemented through holidayCalendar.txt (holidays in 2007) and FedHolidayCalendar.txt (holidays from 2020-2031).

The Powerpoint is the theory reference for building the codes.

Note: this code only considers the coupon payment times > 1, and the payment is made semi-annual.
⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️

