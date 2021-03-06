import datetime
from django.utils import dateparse , timezone
from django.test import TestCase
from django.db import IntegrityError
from time_series.models import *
from .context import TestContext

class RegularTimeSeriesTest(TestCase):

    def test_create(self):

        ts = RegularTimeSeries( start = timezone.now( ) , 
                                step = 0)
        with self.assertRaises(IntegrityError):
            ts.save()

        ts.step = -1
        with self.assertRaises(IntegrityError):
            ts.save()
            
        ts = RegularTimeSeries( start = timezone.now( ) , 
                                step = 100)

        self.assertEqual( len(ts) , 0 )
        with self.assertRaises(IndexError):
            ts[0]        

        ts.addValue( 1 )
        ts.addValue( 2 )
        ts.addValue( 3 )
        ts.addValue( 4 )
        ts.addValue( 5 )
        
        self.assertEqual( len(ts) , 5 )
        with self.assertRaises(IndexError):
            ts[6]

        self.assertEqual( ts[4] , 5 )

        ts.addList( [6,7,8,9,10] )
        self.assertEqual( len(ts) , 10 )
        self.assertEqual( ts[8] , 9 )
        self.assertEqual( ts[9] , 10 )

        ts.addList( (16,17,18,19,110) )
        self.assertEqual( ts[14] , 110 )
        self.assertEqual( len(ts) , 15 )

        data = RegularTimeSeries.createArray( size = 3 )
        self.assertEqual( data.shape[0] , 3 )
        data[0] = 99
        data[1] = 99
        data[2] = 109
        ts.addList( data )
        self.assertEqual( ts[17] , 109 )
        self.assertEqual( len(ts) , 18 )
        
        ts.save()

        ts2 = RegularTimeSeries.objects.get( pk = 1 )
        self.assertEqual( ts2[17] , 109 )
        self.assertEqual( len(ts2) , 18 )
        ts[0] = 100
        ts2[0] = 200


        
    def test_extend(self):
        context = TestContext( )
        start = context.ts.start
        last_time = context.ts.lastTime( )
        
        dt = last_time - start
        self.assertEqual( dt.seconds + dt.days * 3600 * 24 , context.ts.step * len( context.ts ))
    
        start = timezone.now( ).replace( microsecond = 0 )
        ts1 = RegularTimeSeries( start = start , 
                                 step = 100)
        ts1.addList( [0 , 1 , 2 , 3 , 4 ] )

        delta_600 = datetime.timedelta( seconds = 600 )
        ts2 = RegularTimeSeries( start = ts1.start + delta_600 , 
                                 step = 99 )
        ts2.addList( [0 , 1 , 2 , 3 , 4 ] )

        # ts1 and ts2 are not commensurable - different step
        with self.assertRaises(ValueError):
            ts1.addTimeSeries( ts2 )

        delta_m600 = datetime.timedelta( seconds = -600 )
        ts2 = RegularTimeSeries( start = ts1.start + delta_m600 , 
                                 step = 100 )
        ts2.addList( [0 , 1 , 2 , 3 , 4 ] )

        # ts2 must come after ts1
        with self.assertRaises(ValueError):
            ts1.addTimeSeries( ts2 )

        
        
        delta_550 = datetime.timedelta( seconds = 550 )
        ts2 = RegularTimeSeries( start = ts1.start + delta_550 , 
                                 step = 100 )
        ts2.addList( [0 , 1 , 2 , 3 , 4 ] )

        # ts1 and ts2 are not commensurable
        with self.assertRaises(ValueError):
            ts1.addTimeSeries( ts2 )

        delta_800 = datetime.timedelta( seconds = 800 )            
        ts2 = RegularTimeSeries( start = ts1.start + delta_800 , 
                                 step = 100 )
        ts2.addList( [100 , 10 , 20 , 30 , 40 ] )
        ts1.addTimeSeries( ts2 )
        self.assertEqual( len( ts1 ) , 12 )
        
        self.assertTrue( math.isnan( ts1[5] ))
        self.assertTrue( math.isnan( ts1[6] ))
        self.assertEqual( ts1[7] , 100 )
        self.assertEqual( ts1[11] ,  40 )

        e_data = ts2.export( )
        self.assertEqual(len(e_data) , 5)
        self.assertEqual(TimeArray.parse_datetime( e_data[0][0] ), ts2.start)
        self.assertEqual(e_data[0][1] , 100)
        
