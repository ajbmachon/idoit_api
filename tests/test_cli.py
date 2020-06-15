#!/usr/bin/env python

"""Tests for `idoit.cli` module."""

import pytest
from idoit_api.__about__ import __version__
from click.testing import CliRunner
from idoit_api import cli

# TODO refactor to testclass with different methods
def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    # assert 'idoit API Client Version: {}'.format(__version__) in result.output
    assert 'Console script for idoit_api' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--env-file TEXT' in help_result.output
    assert '-l, --log-level INTEGER         [default: 20]' in help_result.output


