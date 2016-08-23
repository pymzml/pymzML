import pymzml
import plot as pfac
import pprint
fac = pfac.Factory()


print ('made new Plot')
fac.newPlot(header='headerTest')
print('add peaks')
fac.add([(x,y) for x,y in zip(range(0,1000, 100), range(0, 1000, 100))], name='data', color=(255,0,0), style='sticks')
fac.add([(1363.56, 1417.56, 20000,'TEST'),(1100, 1200, 1000, 'TEST')], style='label.spline.bottom', name='label.spline.bottom', color=(0,0,0))
fac.add([(1373.56, 1417.56, 20000,'TEST'),(1100, 1200, 1000, 'TEST')], style='label.linear.bottom', name='label.linear.bottom', color=(255,0,0))
fac.add([(1383.56, 1417.56, 20000,'TEST'),(1100, 1200, 1000, 'TEST')], style='label.linear.bottom', name='label.spline.bottom', color=(255,0,0))
fac.add([(200, 200, 200, "TEST"),(400, 400, 400, "TEST")], style='label.sticks', name='sticks', color=(0,255,0))
fac.add([(200, 200, 200, "TEST"),(400, 400, 400, "TEST")], style='label.triangle', name='triangle', color=(0, 0, 255))
fac.add([(200, 200, 200, "TEST"),(400, 400, 400, "TEST")], style='label.triangle.big', name='triangle.big', color=(0, 0, 255))
fac.add([(200+20, 200+20, 200+20, "TEST"),(400+20, 400+20, 400+20, "TEST")], style='label.triangle.big', name='triangle.big', color=(0, 0, 255))



fac.info()
fac.save(filename='filenameTest')
