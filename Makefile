build:
	jupyter run 06-assemble.ipynb
	latexmk -cd latex/vism.tex
	#make -C sphinx html epub
	#cd latex; plastex -c plastex.ini vism.tex
build-all: build-latex build-docbook build-shpinx

build-latex:
	mkdir -p build/latex
	cp latex/vism.tex latex/vism-bib.tex latex/plastex.ini build/latex
	latexmk -q -cd build/latex/vism.tex
	bash -c "cd build/latex; plastex -c plastex.ini vism.tex"
build-sphinx:
	mkdir -p build/sphinx/source
	cp sphinx/Makefile build/sphinx
	cp -r sphinx/source/_static sphinx/source/bib.rst sphinx/source/conf.py sphinx/source/index.rst build/sphinx/source
	make -C build/sphinx html epub
build-docbook:
	mkdir -p build/docbook
	xsltproc /usr/share/xml/docbook/stylesheet/docbook-xsl/xhtml5/docbook.xsl build/docbook/vism.xml > build/docbook/vism.xhtml
	mv docbook.css build/docbook/
	#xsltproc /usr/share/xml/docbook/stylesheet/docbook-xsl/epub/docbook.xsl docbook/vism.xml > build/docbook/vism.epub
	#xsltproc /usr/share/xml/docbook/stylesheet/docbook-xsl/epub3/docbook.xsl docbook/vism.xml > build/docbook/vism.epub3
	cp docbook/vism.fo.xsl docbook/vism.xml docbook/bib.xml build/docbook
	xsltproc -o build/docbook/vism.fo build/docbook/vism.fo.xsl build/docbook/vism.xml
	mv docbook/vism.fop build/docbook
	/home/eudoxos/build/fop-2.8/fop/fop -pdf build/docbook/vism.docbook.pdf -c build/docbook/vism.fop -fo build/docbook/vism.fo
clean:
	rm -rf build gh-pages/docbook gh-pages/latex gh-pages/sphinx

deploy:
	rm -rf gh-pages/docbook gh-pages/latex gh-pages/sphinx
	mkdir -p gh-pages/latex gh-pages/sphinx/build gh-pages/docbook
	rsync -rav build/latex/html gh-pages/latex/html
	rsync -rav build/sphinx/build/html gh-pages/sphinx/build/html
	rsync -av build/latex/vism.pdf gh-pages/latex/
	rsync -av build/docbook/vism.docbook.pdf gh-pages/docbook/
	rsync -av build/docbook/vism.xhtml gh-pages/docbook/
	rsync -av build/docbook/docbook.css gh-pages/docbook/
	#rsync -av --relative latex/vism.pdf sphinx/build/epub/*.epub docbook/docbook.css docbook/vism.docbook.pdf docbook/vism.xhtml docbook/docbook.css gh-pages
	#git -C gh-pages add -A .
	#git -C gh-pages commit -m 'updates build'
	#git -C gh-pages push origin gh-pages
