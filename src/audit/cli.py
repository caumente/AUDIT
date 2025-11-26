import click

from audit.app.launcher import run_streamlit_app
from audit.feature_extraction import run_feature_extraction
from audit.metric_extraction import run_metric_extraction


@click.group()
def cli():
    pass


@cli.command()
@click.option("--config", type=str, default="./configs/app.yml", help="Path to the configuration file for the app")
def run_app(config):
    run_streamlit_app(config)


@cli.command()
@click.option(
    "--config",
    type=str,
    default="./configs/feature_extraction.yml",
    help="Path to the configuration file for feature extraction.",
)
def feature_extraction(config):
    run_feature_extraction(config)


@cli.command()
@click.option(
    "--config",
    type=str,
    default="./configs/metric_extraction.yml",
    help="Path to the configuration file for metric extraction.",
)
def metric_extraction(config):
    run_metric_extraction(config)


if __name__ == "__main__":
    cli()
