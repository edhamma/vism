
FOP?=/home/eudoxos/build/fop-2.8/fop/fop
XSLTNG?=/home/eudoxos/build/xslTNG/build/xslt

.PHONY: latex html5 sphinx docbook xsltng assemble clean

build/vism.sectioned.xml: vism/*.tei 10-assemble-TEI.ipynb
	make assemble

assemble:
	mkdir -p build
	cp -r latex build/
	cp -r html5 build/
	cp -r sphinx build/
	cp -r docbook build/
	cp -r sphinx-vimm build/
	cd vimm; jupyter execute 03-styles.ipynb; jupyter execute 05-export-tei.ipynb
	jupyter execute 10-assemble-TEI.ipynb

build: latex docbook sphinx web

latex: build/vism.sectioned.tei latex/*
	cd build/latex && \
		latexmk vism.tex && \
		plastex -c plastex.ini vism.tex
html5:
	weasyprint -s html5/style.A4.css build/html5/vism.html build/html5/vism.weasyprint.pdf
	vivliostyle build --style build/html5/style.A4.css --single-doc --timeout 1200 --output build/html5/vism.vivliostyle.pdf build/html5/vism.html
sphinx: build/vism.sectioned.tei sphinx/source/*
	make -C build/sphinx html singlehtml epub
docbook: build/vism.sectioned.tei docbook/*
	cd build/docbook && \
		xsltproc -o vism.xhtml vism.xhtml5.xsl vism.xml && \
		xsltproc -o vism.fo vism.fo.xsl vism.xml && \
		$(FOP) -pdf vism.docbook.pdf -c vism.fop -fo vism.fo
xsltng:
	# docker build --build-arg VERSION=2.0.9 -t docbook-xsltng .
	# vism.xsml: must change the header to the following
	# <book version="5.2" xmlns="http://docbook.org/ns/docbook" xmlns:xlink="http://www.w3.org/1999/xlink">
	#
	docker run -v $(realpath build/docbook):/tmp -v $(XSLTNG):/xslt docbook-xsltng:latest /tmp/vism.xml -xsl:/xslt/epub.xsl -o:/tmp/vism.xsltng.epub
	docker run -v $(realpath build/docbook):/tmp -v $(XSLTNG):/xslt docbook-xsltng:latest /tmp/vism.xml -xsl:/xslt/docbook.xsl -o:/tmp/vism.xsltng.html
	#docker run -v $(realpath build/docbook):/tmp -v $(XSLTNG):/xslt docbook-xsltng:latest /tmp/vism.xml -xsl:/xslt/docbook-paged.xsl -o:/tmp/vism.xsltng.html

vimuttimagga: build/vimm.tei
	#cd vimm; jupyter execute 03-styles.ipynb; jupyter execute 04-export.ipynb
	#cp vimm/origin/vimm7a.exported.xml build/
	cd build/latex && latexmk vimm.tex && plastex -c plastex-vimm.ini vimm.tex
	make -C build/sphinx-vimm html singlehtml epub
	weasyprint -s html5/style.A4.css build/html5/vimm.html build/html5/vimm.weasyprint.pdf
	#vivliostyle build --style build/html5/style.A4.css --single-doc --timeout 1200 --output build/html5/vimm.vivliostyle.pdf build/html5/vimm.html
	# TODO? DocBook

web:
	cp index.html build/index.html

clean:
	rm -rf build
