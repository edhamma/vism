# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Visuddhimagga — Digital'
copyright = 'Digital'
author = 'Bhadantācariya Buddhaghosa'

import git, urllib.parse
vismCommit=(head:=git.Repo(search_parent_directories=True).head).object.hexsha[:7]

release = vismCommit
version = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.todo']
todo_include_todos=True

templates_path = ['_templates']
exclude_patterns = []


html_theme_options=dict(
    use_download_button=False,
    use_source_button=False,
    repository_provider='github',
    repository_url='https://github.com/edhamma/vism',
    use_edit_page_button=True,
    use_repository_button=True,
    use_issues_button=True,
)


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

#html_theme = 'alabaster'
html_theme = 'sphinx_book_theme'
html_title='Visuddhimagga'
html_static_path = ['_static']


epub_title = project
epub_author = author
epub_publisher = '~~ edhamma.github.io/vism WIP ~~'
epub_copyright = copyright
epub_cover = ('_static/cover.jpg','epub-cover.html')
epub_language='en'
epub_basename='vism'
epub_use_index=False
epub_scheme='ISBN'
epub_identifier = '978-955-24-0023-6'
# A unique identification for the text.
epub_uid = 'visuddhimagga'

