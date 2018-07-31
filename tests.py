import os
import platform
import pytest
import textwrap


# just to make things stick out in the logs online
def color_print(msg):
    for message in ["=" * 80, msg, "=" * 80]:
        print("\033[36;1m{message}\033[0m".format(message=message))


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


# create testroot, testroot/conf.py, and testroot/index.rst so we can app.build
def make_conf_and_index(testroot, extra_file=False):
    if not os.path.isdir(testroot):
        os.makedirs(testroot)
    color_print("==> testroot directory path created.")

    # create a conf.py
    conf_py_path = os.path.join(testroot, "conf.py")
    with open(conf_py_path, "w") as conf_py:
        conf_py.write(textwrap.dedent('''
            # -*- coding: utf-8 -*-
            project = 'super_long_names'
            master_doc = 'index'
            source_suffix = ['.rst']
        '''))
    color_print("==> The conf.py file has been written.")

    if extra_file:
        # scenario 2: create a file that has a name that will push it over the
        # 260 character path limit.  In this case, sphinx will crash generating
        # the doctree which should be solvable?
        #
        # tricky: we want the full path to be greater than 260, but not exceed
        # filesystem limits on file length (usually around 255?)
        curr_length = len(testroot)
        desired_length = 262
        # eeeeeeeeee......eeeeee.rst
        extra_file_name = "e" * (desired_length - curr_length - 4) + ".rst"
        with open(os.path.join(testroot, extra_file_name), "w") as ef:
            ef.write(textwrap.dedent('''
                Oh Look
                =======

                This is an extra file being generated!
            '''))
        color_print("==> Extra file created: {0}".format(os.path.join(
            testroot, extra_file_name
        )))

    # create an index.rst
    index_rst_path = os.path.join(testroot, "index.rst")
    with open(index_rst_path, "w") as index_rst:
        index_rst.write(textwrap.dedent('''
            Super Long Names
            ================

            This is an index.rst!!!!
        '''))

        if extra_file:
            # make sure this gets included in the build
            index_rst.write(textwrap.dedent('''
                .. toctree::
                   :maxdepth: 2

                   {extra_file_name}
            '''.format(extra_file_name=extra_file_name)))
    color_print("==> The index.rst has been written.")


# decorator to get sphinx and pytest to work together
def setup_sphinx_details(testroot, extra_file=False):
    # see: https://stackoverflow.com/a/5929165/3814202

    def real_decorator(function):
        make_conf_and_index(testroot, extra_file=extra_file)

        def wrapper(app):
            function(app)

        pytest.mark.sphinx(testroot=testroot)(wrapper)
        return wrapper
    return real_decorator


# do not call unless you already did app.build!
def cat_index_html(app):
    index_html_path = os.path.join(app.outdir, "index.html")
    color_print("==> Generated index.html contents:")
    with open(index_html_path) as index_html:
        print(index_html.read())


@setup_sphinx_details(full_absurd_path())
def test_testroot_too_long(app):
    app.build()
    cat_index_html(app)


@setup_sphinx_details(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "docs"),
    extra_file=True
)
def test_rst_doc_too_long(app):
    app.build()
    cat_index_html(app)
