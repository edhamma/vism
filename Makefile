build:
	latexmk -cd xml/vism.tex
	make -C sphinx html
deploy:
	# checkout gh-pages branch, copy output from build there, commit, checkout main again
	# evince vism.pdf &
