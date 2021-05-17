from crontab import CronTab

cron = CronTab(tab="""* * * * * python C:\\Users\\nguye\\PycharmProjects\\pythonProject\\main.py""")
# job = cron.new(command="python C:\\Users\\nguye\\PycharmProjects\\pythonProject\\main.py")
# job.minute.every(1)

for tab in cron:
    print(tab)
cron.write()
