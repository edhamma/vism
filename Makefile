build:
	latexmk -cd latex/vism.tex
	make -C sphinx html
	cd latex; plastex -c plastex.ini vism.tex
deploy:
	git checkout gh-pages
	git add latex/html latex/vism.pdf sphinx/build/html
	git commit -m 'updated build'
	git push origin gh-pages
	git checkout main
	# evince vism.pdf &
