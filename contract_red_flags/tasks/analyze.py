from celery import Celery

app = Celery("contract_red_flags.tasks.analyze.app",
             broker='amqp://',
             backend='rpc://')

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

@app.task
def analyze_text(contract_text):
    return True

@app.task
def analyze_file(contract_file):
    return True

if __name__ == '__main__':
    app.start()