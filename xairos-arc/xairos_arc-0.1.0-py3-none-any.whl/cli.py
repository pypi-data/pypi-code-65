import typer
from xairos_arc.scan import scan
# I guess we can make this a command line app
# arc --scan-log log.csv --output-log data.csv

app = typer.Typer()


@app.command()
def collect(scan_log: str = 'scan-log.csv', output_log: str = 'output-log.csv'):
    scan(scan_log_filename=scan_log,output_log_filename=output_log)


def main():
    app()