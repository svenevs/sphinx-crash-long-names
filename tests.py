import os
import platform
import pytest
import sys
import textwrap


def make_it_big(prefix):
    """Return a ridiculously long path."""
    big = [
        prefix, "that", "is", "longer", "than", "two", "hundred", "and",
        "fifty", "five", "characters", "long", "which", "is", "an",
        "absolutely", "and", "completely", "ridiculous", "thing", "to", "do",
        "and", "if", "you", "did", "this", "in", "the", "real", "world", "you",
        "put", "yourself", "comfortably", "in", "a", "position", "to", "be",
        "downsized", "and", "outta", "here", "as", "soul", "position", "would",
        "explain", "to", "you"
    ]
    return os.sep.join(big)


# Going to generate a Sphinx docs/ dir and conf.py dynamically.
# Always call full_absurd_path(), never use directly :p
ABSURD_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), make_it_big("path")
)


def full_absurd_path():
    # on windows, always return path prefixed with \\?\
    if platform.system() == "Windows":
        return "{magic}{insanity}".format(
            magic="{slash}{slash}?{slash}".format(slash="\\"),  # \\?\
            insanity=ABSURD_PATH
        )
    return ABSURD_PATH


# decorator to get sphinx and pytest to work together
def setup_sphinx_details(method):
    try:
        if not os.path.isdir(full_absurd_path()):
            os.makedirs(full_absurd_path())
        print("==> Absurd directory path created.")

        # create a conf.py
        conf_py_path = os.path.join(full_absurd_path(), "conf.py")
        with open(conf_py_path, "w") as conf_py:
            conf_py.write(textwrap.dedent('''
                # -*- coding: utf-8 -*-
                project = 'super_long_names'
                master_doc = 'index'
                source_suffix = ['.rst']
            '''))
        print("==> The conf.py file has been written.")

        # create an index.rst
        index_rst_path = os.path.join(full_absurd_path(), "index.rst")
        with open(index_rst_path, "w") as index_rst:
            index_rst.write(textwrap.dedent('''
                Super Long Names
                ================

                This project is able to be generated, but then will fail on
                Windows because Sphinx is not checking for >= 260 characters
                and inserting the magicial prefix.

                It should fail during the doctree generation phase on AppVeyor.
            '''))
        print("==> The index.rst has been written.")

        # mark the testing function so that the sphinx tests will be run
        pytest.mark.sphinx(testroot=full_absurd_path())(method)

        return method
    except Exception as e:
        sys.stderr.write("Could not perform test setup: {0}\n".format(e))
        sys.exit(1)


@setup_sphinx_details
def test_it(app):
    app.build()
    index_html_path = os.path.join(
        full_absurd_path(), "_build", "html", "index.html"
    )
    print("==> Generated index.html contents:")
    with open(index_html_path) as index_html:
        print(index_html.read())
