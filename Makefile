
FOP?=/home/eudoxos/build/fop-2.8/fop/fop
XSLTNG?=/home/eudoxos/build/xslTNG/build/xslt

build/book.sectioned.xml: src/*.xml 06-assemble.ipynb
	make assemble

assemble:
	mkdir -p build
	jupyter execute 06-assemble.ipynb

build: build-latex build-docbook build-sphinx build-web

build-latex: build/book.sectioned.xml latex/*
	cp -r latex build/
	cd build/latex && \
		latexmk vism.tex && \
		plastex -c plastex.ini vism.tex

build-sphinx: build/book.sectioned.xml sphinx/source/*
	cp -r sphinx build/
	make -C build/sphinx html epub
build-docbook: build/book.sectioned.xml docbook/*
	cp -r docbook build/
	cd build/docbook && \
		xsltproc -o vism.xhtml vism.xhtml5.xsl vism.xml && \
		xsltproc -o vism.fo vism.fo.xsl vism.xml && \
		$(FOP) -pdf vism.docbook.pdf -c vism.fop -fo vism.fo
xsltng:
	# docker build --build-arg VERSION=2.0.9 -t docbook-xsltng .
	# vism.xsml: must change the header to the following
	# <book version="5.2" xmlns="http://docbook.org/ns/docbook" xmlns:xlink="http://www.w3.org/1999/xlink">
	docker run -v $(realpath build/docbook):/tmp -v $(XSLTNG):/xslt docbook-xsltng:latest /tmp/vism.xml -xsl:/xslt/epub.xsl -o:/tmp/vism.xsltng.epub

build-web:
	cp src/index.html build/index.html

clean:
	rm -rf build gh-pages/docbook gh-pages/latex gh-pages/sphinx
