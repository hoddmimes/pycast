import random
import sys
from time import perf_counter

from pymc.connection_timers import ConnectionTimerTask, ConnectionTimerExecutor
from pymc.aux.aux import Aux
from pymc.connection import Connection


##
## The TrafficFlow Task is monitoring and regulator the traffic flow i.e. update/sec
## and bits/sec. The flow task is recalculate the rates periodically 'recalc_interval_ms'
## the key method is calculateWaitTime which called each time an update is to be published
## This method will ensure that we do not exceed the 'max_bandwidth_kbit' (per intervall).
##

class TrafficFlowTask(ConnectionTimerTask):

	def __init__(self, connection_id:int, recalc_interval_ms:int, max_bandwidth_kbit:int):
		super().__init__(connection_id)
		self.max_bandwidth_kbit:int = max_bandwidth_kbit			# same bandwidth limitation, if 0 flow regulation is off
		self.recalc_interval_ms:int = recalc_interval_ms
		self.connection_id:int = connection_id

		self.mIntervalFactor:float = 1000.0 / recalc_interval_ms

		self.mBitsRateIncrement:int = 0 		# number bits published in the interval
		self.mUpdatesIncremet:int = 0			# number of updates published in the interval

		self.mLastRecalcTimestamp = perf_counter()
		self.mLastRelativeTimeFactor:float = 1.0
		self.mMaxBandWithInInterval:int = (max_bandwidth_kbit * 1024) / self.mIntervalFactor


	def execute( self, connection:Connection ):
		tRealTimeMs:float = (perf_counter() - self.mLastRecalcTimestamp) * 1000.0
		self.mLastRelativeTimeFactor = tRealTimeMs / float( self.recalc_interval_ms )
		self.mBitsRateIncrement = 0
		self.mUpdatesIncremet = 0
		self.mLastRecalcTimestamp = perf_counter()
		#print("TrafficFlowTask: {} bit-increment: {} upd-increment: {}".format( self,  self.mBitsRateIncrement, self.mUpdatesIncremet))

	def increment(self, segmentSize:int):
		self.mBitsRateIncrement += float( segmentSize * 8)
		self.mUpdatesIncremet += 1

	## get current update rate / sec
	def getUpdateRate(self) -> int:
		tUpdRateRate:int = int(float(self.mCurrentUpdateRate * self.mIntervalFactor) * self.mLastRelativeTimeFactor)
		return tUpdRateRate
	##
	## This method if called if flow regulation is enabled i.e. max_bandwidth_kbits != 0
	## The method is called each time after a segment has been published. It will calculate
	## if the flow rate has been exceeded and if so how long the send flow should be delayed
	## inorder not to exceed the max bandwidth
	##

	def calculateWaitTimeMs( self ) -> int:
		# If bandwidth control is not enforced just return wait time eq zero
		if self.max_bandwidth_kbit == 0:
			return 0

		if self.mBitsRateIncrement > (self.mMaxBandWithInInterval * self.mLastRelativeTimeFactor):
			# Bandwidth is exceeded, calculate suspend time
			tRatio:float = float(self.mBitsRateIncrement) / (float(self.mMaxBandWithInInterval) * self.mLastRelativeTimeFactor)
			tWaitTime:float = float(self.recalc_interval_ms) * tRatio
			#print("self: {} increment: {} max-in-interval: {} wait-ms: {}".format( self, self.mBitsRateIncrement,
			#																 int(float(self.mMaxBandWithInInterval) * self.mLastRelativeTimeFactor),
			#																 int(tWaitTime)))
			return int(tWaitTime)
		else:
			return 0


## ========================================
##     Test
## ========================================

def test():
	flowTask = TrafficFlowTask( connection_id=0, recalc_interval_ms=100, max_bandwidth_kbit=256)
	ConnectionTimerExecutor.getInstance().queue(interval=flowTask.recalc_interval_ms, task=flowTask, repeat=True)

	_startTime = Aux.currentMilliseconds()
	_tot_bytes = 0
	for i in range(100):
		_bytes = random.randrange( start=100, stop=8192)
		flowTask.increment(_bytes)
		_tot_bytes += _bytes
		wt = flowTask.calculateWaitTimeMs()
		if wt > 0:
			print('loop: {} wait: {}'.format(i, wt))
			Aux.sleepMs( wt )

	_rate = float((_tot_bytes * 8 * 1000) / (Aux.currentMilliseconds() - _startTime)) / 1024.0
	print('kbit-rate: {} '.format( _rate))
	sys.exit()
if __name__ == '__main__':
    test()