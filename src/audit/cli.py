import click
from audit.app.launcher import main as app_main
from audit.feature_extractor import run_feature_extractor
from audit.metric_extractor import run_metric_extractor


@click.group()
def cli():
    pass


@cli.command()
def run_app():
    app_main()


@cli.command()
@click.option(
    '--config',
    type=str,
    default='./configs/feature_extractor.yml',
    help="Path to the configuration file for feature extraction."
)
def feature_extractor(config):
    run_feature_extractor(config)


@cli.command()
@click.option(
    '--config',
    type=str,
    default='./configs/metric_extractor.yml',
    help="Path to the configuration file for metric extraction."
)
def metric_extractor(config):
    run_metric_extractor(config)


if __name__ == "__main__":
    cli()
