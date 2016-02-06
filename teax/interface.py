#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""teax command-line interface"""

import os

import click

from teax import conf, tty
from teax.utils.slugify import slugify
from teax.system.core import CoreController
from teax.system.template import TemplateObject


@click.group()
@click.version_option()
def teax():
    """
    Command line utilities for TeX. Arm yourself with secret powers!

    maciejczyzewski.me/teax/                       #teax on freenode
    """

@teax.command('build')
@click.argument('filename')
@click.option('--watch', is_flag=True,
              help='Observe for changes and automatically rebuild.')
@click.option('--pdf/--no-pdf', default=True,
              help='Produce portable document format knows as PDF.')
def build(filename, watch, pdf):
    """Build document from source files."""

    # Default configuration.
    conf['build.filename'] = filename
    conf['build.watch'] = watch

    # Initialize teax and mount the specified file.
    core = CoreController()
    core.mount(conf['build.filename'])

    # Build document using defined flags.
    core.build(pdf=pdf)

    # Prepare list of warning and error messages.
    core.result()

@teax.command('new')
@click.argument('template')
@click.option('--title', prompt=True)
@click.option('--authors', prompt=True)
@click.option('--keywords', prompt=True)
@click.option('--path',
              help='Destination directory (defaults to ./$title)')
def new(template, title, authors, keywords, path):
    """Create a skeleton of empty document."""

    # Default configuration.
    conf['general.title'] = title
    conf['general.authors'] = authors
    conf['general.keywords'] = keywords

    # If path option is not set, use title.
    path = (path if path else slugify(title))

    # Load template and save to the indicated path.
    TemplateObject(template).save(path)
