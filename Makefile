build:
	latexmk -cd latex/vism.tex
	make -C sphinx html epub
	cd latex; plastex -c plastex.ini vism.tex
deploy:
	git checkout gh-pages
	git add --all index.html latex/html latex/vism.pdf sphinx/build/html sphinx/build/epub/*.epub
	git commit -m 'updated build'
	git push origin gh-pages
	git checkout main
