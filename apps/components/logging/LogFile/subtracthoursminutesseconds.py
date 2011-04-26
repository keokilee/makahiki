import datetime as dt
start="09:35:23"
end="10:23:00"
start_dt = dt.datetime.strptime(start, '%H:%M:%S')
end_dt = dt.datetime.strptime(end, '%H:%M:%S')
diff = (end_dt - start_dt) 
diff.seconds/60 
print diff