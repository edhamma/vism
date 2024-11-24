from lxml import etree
import itertools
import roman, textwrap
import os


def TOC_merge(
    vismTei='vism/book.6.tei',
    tocXml='vism/toc.xml',
    indexTei='vism/index.tei',
    glossTei='vism/gloss.tei',
    outTei='build/vism.sectioned.tei',
    outToc='build/vism.toc.xml'):



    def _one_only(pp):
        assert(len(pp)==1)
        return pp[0]




    def add_sections(book,tocXML,vimm=False):
        flatBook=list(book.iter())
        # hand-tuned toc, do not overwrite
        toc=etree.parse(tocXML,etree.XMLParser(remove_comments=True)).getroot()


        for toc_chap in toc:
            chap_num=toc_chap.attrib['num']
            print(chap_num)
            chap=_one_only(book.findall('.//head[@n="'+chap_num+'"]')).getparent()
            if not vimm:
                chapLastPara=str(max([int(e.attrib['n']) for e in chap if e.tag=='p' and 'n' in e.attrib]))
                toc_chap.attrib['para_last']=chapLastPara
            else:
                elem0=chap[0]
            ee0={}
            # find first DOM element for each sectioning piece
            for toc_sect in toc_chap.iter():
                if toc_sect.tag=='chapter': continue
                try: para,title,starts_at=toc_sect.get('para',None),toc_sect.attrib['title'],toc_sect.attrib.get('starts_at',None)
                except KeyError:
                    print(f'Missing keyword? line {toc_sect.sourceline} {toc_sect.tag}')
                    raise
                if not vimm: # Visuddhimagga
                    if para is None: raise RuntimeError(f'Missing para for Visuddhimagga {toc_sect.sourceline} {toc_sect.tag}')
                    if len(pp:=list(chap.findall('.//p[@n="'+para+'"]')))!=1:
                        print(f'{chap_num} {para=} {starts_at=}')
                    elem0=_one_only(chap.findall('.//p[@n="'+para+'"]'))
                if starts_at is not None:
                    for ix in itertools.count(flatBook.index(elem0)+1):
                        if ix>=len(flatBook): raise RuntimeError(f'No match for "{starts_at}".')
                        e=flatBook[ix]
                        if e.tag not in ('span','em'): continue
                        if not e.text.startswith(starts_at): continue
                        parent=e.getparent()
                        if parent.index(e)>0: raise RuntimeError(f'start_at matched on {e.tag} (line {e.sourceline}) but it is not the first child of its parent <{parent.tag}> (line {parent.sourceline}) — not splitting paragraphs.')
                        if parent.tag=='p': pass
                        elif parent.tag=='l':
                            parent=parent.getparent()
                            assert parent.tag=='lg'
                        else: raise RuntimeError(f'Matched content trouble: parent of {e.tag} (line {e.sourceline}) must be <p> or <line> (not {parent.tag}).')
                        elem0=parent
                        break
                    # if elem0 is None: raise RuntimeError(f'start_at did not match anything (chapter {chap_num}, line {e.sourceline}, {starts_at=})')
                ee0[toc_sect]=elem0
                assert elem0.getparent().tag=='div'
                assert elem0.getparent().attrib['type']=='2-chapter'
                if vimm: elem0=flatBook[flatBook.index(elem0)+1]
            def _subdivide(sects,level,lastPara):
                sect=None
                for isect,sect in enumerate(sects):
                    # print(sect.sourceline)
                    l2=level+3
                    new=etree.Element('div',type=f'{l2}-{level*"sub"}section')
                    new.append(head:=etree.Element(f'head'))
                    head.append(hSpan:=etree.Element('span'))
                    hSpan.text=sect.attrib['title']
                    # new[-1].text=_E('span'm,sect.attrib['title']
                    new.attrib['par_begin']=sect.attrib['para']
                    if isect==len(sects)-1:
                        eAfter=None
                        new.attrib['par_end']=sect.attrib['para_end']=lastPara
                    else:
                        sAfter=sects[isect+1]
                        eAfter=ee0[sAfter]
                        new.attrib['par_end']=sect.attrib['para_end']=str(int(sAfter.attrib['para'])-(0 if 'starts_at' in sAfter.attrib else 1))
                    e=ee0[sect]
                    e.addprevious(new)
                    pnum=new.getparent().get('n',None)
                    new.attrib['n']=f'{pnum}.{isect+1}' if pnum else f'{isect+1}'
                    while True:
                        ee=e.getnext()
                        new.append(e)
                        e=ee
                        if e==eAfter or e is None: break
                    _subdivide(sect,level=level+1,lastPara=new.attrib['par_end'])
                return [sect]
            _subdivide(toc_chap,level=0,lastPara=chapLastPara)
        return toc

    vimm=False # no Vimuttimagga

    teiDir=os.path.dirname(vismTei)
    book=etree.parse(vismTei,etree.XMLParser(remove_blank_text=True)).getroot()

    for inc in book.findall('.//include'):
        assert inc.attrib['file'].endswith('.xml')
        incRoot=etree.parse(teiDir+'/'+os.path.splitext(inc.attrib['file'])[0]+'.tei',etree.XMLParser(remove_blank_text=True,remove_comments=True)).getroot()
        inc.getparent().replace(inc,incRoot)

    toc=add_sections(book,tocXml)
    teiText=_one_only(book.findall('.//text'))
    teiText.append(back:=etree.Element('back'))
    back.append(etree.parse(indexTei,etree.XMLParser()).getroot())
    back.append(etree.parse(glossTei,etree.XMLParser()).getroot())

    open(outTei,'w').write(etree.tostring(book,encoding='unicode',pretty_print=True))
    # this is just for inspection
    open(outToc,'w').write(etree.tostring(toc,encoding='unicode',pretty_print=True))


