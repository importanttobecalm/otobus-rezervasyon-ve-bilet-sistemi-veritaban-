from datetime import datetime, timedelta
print((datetime.now() + timedelta(days=0)).strftime("%Y-%m-%d").split(" ")[0])