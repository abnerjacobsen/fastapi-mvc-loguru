# -*- coding: utf-8 -*-
"""das_sankhya CLI root."""
import logging

import click
from das_sankhya.cli.commands.serve import serve
from das_sankhya.cli.commands.devserve import devserve


@click.group()
@click.option(
    "-v",
    "--verbose",
    help="Enable verbose logging.",
    is_flag=True,
    default=False,
)
def cli(**options):
    """das_sankhya CLI root."""
    if options["verbose"]:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(process)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %z",
    )


cli.add_command(serve)
cli.add_command(devserve)
