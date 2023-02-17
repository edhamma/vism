
FOP:=/home/eudoxos/build/fop-2.8/fop/fop

assemble:
	jupyter execute 06-assemble.ipynb
	# latexmk -cd latex/vism.tex
	#make -C sphinx html epub
	#cd latex; plastex -c plastex.ini vism.tex
build-all: build-latex build-docbook build-sphinx

build-latex:
	cp latex/* build/latex
	cd build/latex; \
		latexmk -quiet vism.tex \
		plastex -c plastex.ini vism.tex

build-sphinx:
	cp -r sphinx build/sphinx
	make -C build/sphinx html epub
build-docbook:
	cp -r docbook build/docbook
	cd build/docbook; \
		xsltproc -o vism.xhtml vism.xhtml5.xsl vism.xml \
		xsltproc -o vism.fo vism.fo.xsl vism.xml \
		$(FOP) -pdf vism.docbook.pdf -c vism.fop -fo vism.fo
clean:
	rm -rf build gh-pages/docbook gh-pages/latex gh-pages/sphinx

deploy:
	rm -rf gh-pages/docbook gh-pages/latex gh-pages/sphinx
	mkdir -p gh-pages/latex gh-pages/sphinx/build gh-pages/docbook
	rsync -rav build/latex/html gh-pages/latex/
	rsync -rav build/sphinx/build/html gh-pages/sphinx/build/
	rsync -av build/sphinx/build/epub/vism.epub gh-pages/sphinx/build/epub/
	rsync -av build/latex/vism.pdf gh-pages/latex/
	rsync -av build/docbook/vism.docbook.pdf gh-pages/docbook/
	rsync -av build/docbook/vism.xhtml gh-pages/docbook/
	rsync -av build/docbook/docbook.css gh-pages/docbook/
	git -C gh-pages add -A .
	git -C gh-pages commit -m 'updates build'
	git -C gh-pages push origin gh-pages
