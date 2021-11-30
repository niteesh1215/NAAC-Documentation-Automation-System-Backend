# to install schedule
# RUN "python -m pip install schedule" in CMD

import schedule
import time

def job():
    print("I'm working...")


schedule.every().day.at("20:02").do(job)

# schedule.every(10).minutes.do(job)
# schedule.every().hour.do(job)
# schedule.every().monday.do(job)
# schedule.every().tuesday.do(job)
# schedule.every().wednesday.do(job)
# schedule.every().thursday.do(job)
# schedule.every().friday.do(job)
# schedule.every().saturday.do(job)
# schedule.every().sunday.do(job)
# schedule.every().minute.at(":17").do(job)

while True:
    schedule.run_pending()
    time.sleep(5)