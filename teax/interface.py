#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""teax command-line interface"""

import os
import click
import subprocess

from teax import __version__, conf, tty, TEAX_WORK_PATH
from teax.system.core import CoreController
from teax.system.template import TemplateObject
from teax.system.parser import LaTeXFilter

@click.group()
@click.version_option()
def teax():
    """
    Command line utilities for TeX. Arm yourself with secret powers!
    """

@teax.command('build')
@click.argument('filename')
@click.option('--watch', is_flag=True, help='Observe changes and automatically rebuild.')
@click.option('--pdf/--no-pdf', default=True, help='Produce portable document format knows as PDF.')
def build(filename, watch, pdf):
    """Builds document from source."""
    conf['build.filename'] = filename
    conf['build.watch'] = watch

    core = CoreController()
    core.mount(conf['build.filename'])

    def _output(cmd):
        """Returns output for the given shell command."""
        return subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

    PLATFORM = _output(['uname', '-mnprs']).strip()

    tty.echo("Path:     {0}".format(TEAX_WORK_PATH))
    tty.echo("Platform: {0}".format(PLATFORM))
    tty.echo("Engine:   {0} [{1}]".format(core.shelf['engine'], __version__))

    tty.section('BUILD')
    core.build(pdf=pdf)

    tty.section('RESULT')
    logfile = TEAX_WORK_PATH + '/.teax/' + os.path.splitext(filename)[0] + '.log'
    lf = LaTeXFilter()
    lf.feed(open(logfile, 'rt').read())
    for message in lf.get_messages():
        tty.warning(message.msg)
        block = []
        if message.filename:
            head, filename = os.path.split(message.filename)
            block.append('file ' + filename)
        if message.lineno:
            block.append('line ' + str(message.lineno))
        if len(block) > 0:
            tty.echo('    $[BG_WHITE]$[BLACK] {0} $[NORMAL]'.format('; '.join(block)))


@teax.command('new')
@click.argument('template')
@click.option('--title', prompt=True)
@click.option('--authors', prompt=True)
@click.option('--keywords', prompt=True)
@click.option('--path')
def new(template, title, authors, keywords, path):
    """Creates a skeleton of document."""
    conf['general.title'] = title
    conf['general.authors'] = authors
    conf['general.keywords'] = keywords

    # If path option is not set, use title
    path = (path if path else title)

    TemplateObject(template).save(path)
