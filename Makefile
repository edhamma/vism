build:
	latexmk -cd latex/vism.tex
	make -C sphinx html epub
	cd latex; plastex -c plastex.ini vism.tex
build-parallel:
	rm -rf latex/html sphinx/build
	latexmk -cd latex/vism.tex & make -C sphinx html epub & bash -c "cd latex; plastex -c plastex.ini vism.tex" & wait;
	
deploy:
	rsync -rav --delete --relative latex/html sphinx/build/html gh-pages
	rsync -av --relative latex/vism.pdf sphinx/build/epub/*.epub gh-pages
	git -C gh-pages add -A .
	git -C gh-pages commit -m 'updates build'
	git -C gh-pages push origin gh-pages
