from lxml import etree
import itertools
import roman, textwrap
import os
import sys
sys.path.append('.')
import tei_exporters
import vism_tei_utils

vimmTei='build/vimm.tei'
vismTei='build/vism.sectioned.tei'

# Vishuddmagga has the TOC separately, needs to be merged into the TEI
vism_tei_utils.TOC_merge(
    vismTei='vism/book.6.tei',
    tocXml='vism/toc.xml',
    indexTei='vism/index.tei',
    glossTei='vism/gloss.tei',
    outTei=vismTei,
    outToc='build/vism.toc.xml'
)

os.makedirs('build/latex',exist_ok=True)
tei_exporters.latex_write_defs('build/latex/vism-defs.tex')

for title,tei,out,vimm in [
    ('Visuddhimagga',vismTei,'build/latex/vism-body.tex',False),
    ('Vimuttimagga',vimmTei,'build/latex/vimm-body.tex',True),
    ]:
    print(title)
    writer=tei_exporters.LatexWriter()
    book=etree.parse(tei,etree.XMLParser(remove_comments=True)).getroot()
    open(out,'w').write(writer.write(book))

for title,tei,outdir,vimm in [
    ('Visuddhimagga',vismTei,'build/sphinx-rst-/source',False),
    ('Vimuttimagga',vimmTei,'build/sphinx-rst-vimm/source',True),
    ]:
    os.makedirs(outdir,exist_ok=True)
    writer=tei_exporters.SphinxWriter(outdir=outdir,vimm=vimm)
    book=etree.parse(tei,etree.XMLParser()).getroot()
    writer.write(book)
    writer.writeIndex(title=title)

for title,tei,outdir,vimm in [
    ('Visuddhimagga',vismTei,'build/sphinx/source',False),
    ('Vimuttimagga',vimmTei,'build/sphinx-vimm/source',True),
    ]:
    os.makedirs(outdir,exist_ok=True)
    writer=tei_exporters.SphinxWriterMyST(outdir=outdir,vimm=vimm)
    book=etree.parse(tei,etree.XMLParser()).getroot()
    writer.write(book)
    writer.writeIndex(title=title)

for title,tei,metaXml,stem in [
    ('Visuddhimagga',vismTei,'docbook/vism-meta.xml','vism'),
    ('Vimuttimagga',vimmTei,'docbook/vimm-meta.xml','vimm'),
    ]:
    bk=etree.parse(tei,etree.XMLParser(remove_blank_text=True)).getroot()
    meta=etree.parse(metaXml,etree.XMLParser(remove_blank_text=True)).getroot()
    bk.insert(0,meta)

    for xslTNG in False,True:
        docb=tei_exporters._docb_writer(bk,xslTNG=xslTNG)
        docb=tei_exporters._docbook_fix_formalpara(docb)
        kw=dict(doctype=None,xml_declaration=True,encoding='utf-8')
        os.makedirs('build/docbook',exist_ok=True)
        if xslTNG: stem+='.xslTNG'
        # stem='vism.xslTNG' if xslTNG else 'vism'
        open(f'build/docbook/{stem}.xml','wb').write(etree.tostring(docb,pretty_print=False,**kw))
        open(f'build/docbook/{stem}.pretty.xml','wb').write(etree.tostring(docb,pretty_print=True,**kw))
        print(f'→ build/docbook/{stem}.xml build/docbook/{stem}.pretty.tei.xml')



os.makedirs('build/html5',exist_ok=True)
for title,tei,stem in [
    ('Vissudhimagga',vismTei,'vism'),
    ('Vimuttimagga',vimmTei,'vimm'),
    ]:
    bk=etree.parse(tei,etree.XMLParser(remove_blank_text=True)).getroot()

    ht=tei_exporters.Html5Writer().write(bk)
    open(f'build/html5/{stem}.book.xml','wb').write(etree.tostring(bk,pretty_print=True))
    kw=dict(doctype=None,xml_declaration=True,encoding='utf-8',method='xml')
    os.makedirs('build/html5',exist_ok=True)
    open(f'build/html5/{stem}.html','wb').write(etree.tostring(ht,**kw))
    open(f'build/html5/{stem}.pretty.html','wb').write(etree.tostring(ht,pretty_print=True,**kw))
    print(f'→ build/html5/{stem}.html build/html5/{stem}.pretty.html')
