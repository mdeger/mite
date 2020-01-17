# calcluations on the subject of a credit for a large expense
# 

import numpy
import pylab


class credit(object):

    def __init__(self, expense=5.0e5, interest_rate=0.02, capital=0., \
        monthly_rate=1000., max_years=500, age0=None, age1=67, unit=1000):
        '''Compute how debt develops over years given initial capital, 
        monthly_rate of payments to repay the debt, and the (yearly) 
        interest_rate of the credit. 
        Further (optional) parameters control computation and plotting.'''
        self.expense = expense
        self.interest_rate = interest_rate
        self.capital = capital
        self.monthly_rate = monthly_rate
        self.max_years = max_years
        self.age0 = age0
        self.age1 = age1
        self.unit = unit
        self.compute()
        self.plot()
    
    
    def compute(self):
        '''iterate over years to see how debt develops'''
        self.years = numpy.arange(self.max_years+1)
        self.debt_y = numpy.zeros_like( self.years )
        self.expense_y = numpy.zeros_like( self.years )
        
        self.debt_y[0]    = self.expense - self.capital
        self.expense_y[0] = self.capital
        
        # iterate over years and months
        for y in self.years[1:]:
            debt_m    = self.debt_y[y-1]
            expense_m = self.expense_y[y-1]
            for m in range(12):
                expense_m += min( self.monthly_rate, debt_m * (debt_m>0) )
                debt_m = debt_m - self.monthly_rate + \
                         debt_m * self.interest_rate / 12.
            self.debt_y[y] = debt_m * ( debt_m > 0 )
            self.expense_y[y] = expense_m 
        
        # find year when debt hits crosses zero line
        self.y_done = numpy.searchsorted( -self.debt_y, 0 ) + 1
    
        self.bank_profit    = self.expense_y[-1] - self.capital - self.debt_y[0]
        self.bank_profit_ratio = self.bank_profit / self.debt_y[0]

        # print main results
        print('total debt:      '+str( self.debt_y[0] ))
        print('bank profit:     '+\
            str( int( numpy.round( self.bank_profit, decimals=0 ))))
        print('bank profit ratio: '+\
            str( int( numpy.round( self.bank_profit_ratio*100, decimals=0 ))) +\
            '%')
    
    
    def plot(self):
        '''plot the debt over time. 
        If age0 is given, plot as a function of age.'''
        pylab.ion()
        pylab.figure(1)
        pylab.clf()
        
        pylab.title( 'exp.:'+str(self.expense/self.unit)+\
            ', cap.:'+str(self.capital/self.unit)+\
            ', int.:'+str(self.interest_rate)+\
            ', m.r.:'+str(self.monthly_rate/self.unit) )
        
        # if we don't 'know the starting age, plot as a function of time
        if self.age0==None:
            x = self.years
            pylab.xlabel('time [years]')
        # if we know the starting age, plot as a function of person's age
        else:
            x = self.age0 + self.years
            pylab.xlabel('age [years]')
            pylab.xlim( self.age0-1, min( self.y_done + self.age0, 100 )+1 )
            if self.age1 < self.y_done + self.age0:
                pylab.axvline( self.age1, color='b' )
        pylab.plot( x[:self.y_done], self.debt_y[:self.y_done]/self.unit, 'k-', \
            marker='s', markersize=5, linewidth=2 )
        pylab.plot( x[:self.y_done], self.expense_y[:self.y_done]/self.unit, 'b-', \
            marker='o', markersize=3, linewidth=2 )
        pylab.axhline( 0., color='k' )
        pylab.axhline( self.debt_y[0]/self.unit, color='g' )
        pylab.axhline( self.expense_y[-1]/self.unit, color='r' )
        # show in units of self.unit (whatever currency)
        pylab.ylabel('debt ['+str(self.unit)+']')
        pylab.show()


# example usage (pass arguments to modify parameters)
c = credit()


