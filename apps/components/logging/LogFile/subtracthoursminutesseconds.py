import datetime as dt
start = "2011-05-03 03:00:00"
end = "2011-05-04 04:00:00"
start_dt = dt.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
end_dt = dt.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
diff = (end_dt - start_dt) 
diff.seconds/60 
# test = dt.datetime.strptime(str(diff), '%Y-%m-%d %H:%M:%S')
print str(diff)