build:
	jupyter run 06-assemble.ipynb
	latexmk -cd latex/vism.tex
	#make -C sphinx html epub
	#cd latex; plastex -c plastex.ini vism.tex
build-parallel:
	jupyter run 06-assemble.ipynb
	rm -rf latex/html sphinx/build
	latexmk -cd latex/vism.tex & \
        make -C sphinx html epub & \
        bash -c "cd latex; plastex -c plastex.ini vism.tex" & \
        make docbook-xhtml & \
        make docbook-epub3 & \
        make docbook-pdf &\
        wait;
docbook-xhtml:
	xsltproc /usr/share/xml/docbook/stylesheet/docbook-xsl/xhtml5/docbook.xsl docbook/vism.xml > docbook/vism.xhtml
	mv docbook.css docbook/
docbook-epub:
	xsltproc /usr/share/xml/docbook/stylesheet/docbook-xsl/epub/docbook.xsl docbook/vism.xml > docbook/vism.epub
docbook-epub3:
	xsltproc /usr/share/xml/docbook/stylesheet/docbook-xsl/epub3/docbook.xsl docbook/vism.xml > docbook/vism.epub3
docbook-pdf:
	xsltproc -o docbook/vism.fo docbook/vism.fo.xsl docbook/vism.xml
	/home/eudoxos/build/fop-2.8/fop/fop -pdf docbook/vism.docbook.pdf -c docbook/vism.fop -fo docbook/vism.fo

deploy:
	rsync -rav --delete --relative latex/html sphinx/build/html gh-pages
	rsync -av --relative latex/vism.pdf sphinx/build/epub/*.epub docbook/docbook.css docbook/vism.docbook.pdf docbook/vism.xhtml docbook/docbook.css gh-pages
	git -C gh-pages add -A .
	git -C gh-pages commit -m 'updates build'
	git -C gh-pages push origin gh-pages
