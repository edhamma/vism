# Visuddhimagga — digital

For overview of the this project, see https://eudoxos.github.io/vism ; this file describes mostly technicalities of the repository and building.

## Contributing

This is a WIP project and any contributions are welcome: especially edits in the `src/*.xml` files which are (as of now) machine-generated and contain some errors.

You are welcome to fork the repository and submit a pull request, or simply open an issue if you are not sure how to edit.

## Repository structure

* `origin`: Original source data plus scripts applied to them to have them machine-readable. This is now not to be used anymore (or in emergency only): its result (in src/) may now be hand-edited.
* `src`: generic (format-agnostic) data for the e-book (book text, index, glossary and editorial sectioning)
* `latex`, `docbook`, `sphinx`: format-specific files for e-books
* `Makefile`: describes the build process itself, is used both locally and by the CI
* `.github/workflows/ebook.yml`: CI workflow which will re-build all the e-books after each commit to the repository, and deploy the website

