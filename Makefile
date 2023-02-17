
FOP?=/home/eudoxos/build/fop-2.8/fop/fop

build/book.sectioned.xml: src/*.xml
	mkdir -p build
	jupyter execute 06-assemble.ipynb

build: build-latex build-docbook build-sphinx build-web

build-latex: build/book.sectioned.xml
	cp -r latex build/
	cd build/latex; \
		latexmk -quiet vism.tex; \
		plastex -c plastex.ini vism.tex;

build-sphinx: build/book.sectioned.xml
	cp -r sphinx build/
	make -C build/sphinx html epub
build-docbook: build/book.sectioned.xml
	cp -r docbook build/
	cd build/docbook; \
		xsltproc -o vism.xhtml vism.xhtml5.xsl vism.xml; \
		xsltproc -o vism.fo vism.fo.xsl vism.xml; \
		$(FOP) -pdf vism.docbook.pdf -c vism.fop -fo vism.fo;

build-web:
	cp src/index.html build/index.html

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
