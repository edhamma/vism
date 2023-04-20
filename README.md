# Visuddhimagga — digital

For overview of the this project, see https://eudoxos.github.io/vism ; this file describes mostly technicalities of the repository and building.

## Contributing

This is a WIP project and any contributions are welcome: especially edits in the `src/*.xml` files which are (as of now) machine-generated and contain some errors.

You are welcome to fork the repository and submit a pull request, or simply open an issue if you are not sure how to edit.

## Source data

## Repository structure

* `vism`, `vimm`: generic (almost-TEI) data for the e-book (book text, index, glossary, bibliography, and editorial sectioning)
* `vism/origin`: data which once served as the basis; not needed anymore
* `vimm/origin`: source for Vimuttimagga as ODT, plus other support files; the ODT is converted to our almost-TEI representation using the scripts (`*.ipynb` notebooks) in `vimm`, and then the same machinery as for Visuddhimagga is used.
* `vism/origin`: base data for this work
* `latex`, `docbook`, `sphinx`, `sphinx-vimm`, `html5`: format-specific files for e-books
* `Makefile`: describes the build process itself, is used both locally and by the CI
* `.github/workflows/ebook.yml`: CI workflow which will re-build all the e-books after each commit to the repository, and deploy the website

