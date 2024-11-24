import os, re
import textwrap
##
## LaTeX output
##
#editorial_titles=False
#vimm=False
#mainmatter=False

import git, urllib.parse
vismCommit=(head:=git.Repo(search_parent_directories=True).head).object.hexsha[:7]
vismCommitTimestampQuery=urllib.parse.quote('in version '+vismCommit+' dated '+head.commit.committed_datetime.date().isoformat())

def latex_write_defs(out):
    vismCommitTimestampQuery_=vismCommitTimestampQuery.replace("%","\\%")
    open(out,'w').write(f'''
        \\def\\vismCommit{{{vismCommit}}}\n
        \\def\\vismCommitTimestampQuery{{{vismCommitTimestampQuery_}}}\n
    ''')

class LatexWriter(object):
    def __init__(self,vimm=False,editorial_titles=False):
        self.vimm=vimm
        self.editorial_titles=editorial_titles
        self.bookMatter=-1
        self.lev=-1
    # def _latex_writer(e,lev=0,ord=-1):
    def _rep(self,t): return t.replace('&','\\&').replace('#','\\#').replace('$','\\$')
    def _recurse(self,e,*,incLev=True):
        if incLev: self.lev+=1
        if e.text is not None and len(e)==0: ret=self._rep(e.text)
        else: ret=''.join([self.write(e2,ord=ord) for ord,e2 in enumerate(e)])
        self.lev-=1
        return ret
    def _nobraces(self,t):
        return t.replace('[','').replace(']','')
    def _title(self,sect,e,hyper=None):
        t=self._recurse(e)
        if sect in ('chapter','part'):
            hy=('' if hyper is None else '\\vismHypertarget{'+hyper+'}')
            if 'subtitle_pali' not in e.attrib: return f'\\{sect}'+'['+t+']{'+t+hy+'}'
            else: return f'\\{sect}[{t}]{{{t}{hy}\\newline{{\\textnormal{{\\emph{{{e.attrib["subtitle_pali"]}}}}}}}}}'
        struct=e.getparent()
        if 'par_begin' in struct.attrib:
            p0,p1=int(struct.attrib['par_begin']),int(struct.attrib['par_end'])
            if p0==p1: t2=f'§{p0}'
            else: t2=f'§{p0}–{p1}'
            # return '\\'+sect+'[\\protect\\numberline{'+t2+'}'+t+']{\\ifplastex\\else\\kern-1em\\fi{}'+t+'}'
            return '\\'+sect+'[\\vismAlignedParas{'+t2+'}'+t+']{'+t+'}' #'\\ifplastex\\else\\hfill '+t2+'\\fi}'
            # return '\\def\\vismNextParRange{'+t2+'}\\'+sect+'{'+t+'}'
        else: return '\\'+sect+'{'+t+'}'

    def write(self,e,ord=-1):
        ret=''
        ind=2*self.lev*'  '

        if isinstance(e,etree._Comment): return ''
        if e.tag=='TEI': return self._recurse(e)
        elif e.tag=='teiHeader': return ''
        elif e.tag=='text': return self._recurse(e,incLev=True)
        elif e.tag=='em':
            if len(e)>0: raise RuntimeError(f'<em> with child elements, line {e.sourceline}')
            if e.text is None: return ''
            return '\\emph{'+self._rep(e.text)+'}'
        elif e.tag=='span':
            if len(e)>0: raise RuntimeError(f'<span> with child elements, line {e.sourceline}')
            if e.text is None: return ''
            tx=self._rep(e.text)
            if (fam:=e.attrib.get('rend',None)) is None: return tx
            elif fam=='italic': return '\\emph{'+tx+'}'
            elif fam=='bold': return '\\textbf{'+tx+'}'
            elif fam=='smallcaps': return '\\textsc{'+tx+'}'
            elif fam=='bold-italic': return '\\textbf{\\emph{'+tx+'}}'
            else: raise RuntimeError(f'Unrecognized family {fam}')
        elif e.tag=='p':
            if not self.editorial_titles and e.get('type',None)=='editorial_title': return ''
            ret='\n\n'+ind if ord>0 else ''
            if 'id' in e.attrib:
                num,anchor=e.attrib['n'],e.attrib['id']
                # ret+='\\paragraph{§'+num+'.}\\vismHypertarget{'+anchor+'}{}\\marginnote{\\footnotesize\\textcolor{purple}{'+anchor+'}}{}\n'+ind
                ret+='\\vismParagraph{'+anchor+'}{'+num+'}{}\n'+ind
            return ret+self._recurse(e)
        elif e.tag=='note':
            if e.get('place',None)=='foot':
                check=r'\vismAssertFootnoteCounter{'+e.attrib['n']+'}'
                if 'reference_existing_footnote' in e.attrib: return check+r'\footnotemark[\value{footnote}]'
                # elif anchor:=e.attrib.get('anchor',None): return '\\footnote{'+check+'\\vismHypertarget{'+anchor+'}{}\\marginnote{\\footnotesize\\textcolor{purple}{'+anchor+'}}'+self._recurse(e)+'}'
                elif anchor:=e.attrib.get('anchor',None): return '\\footnote{'+check+'\\vismHypertarget{'+anchor+'}{}'+self._recurse(e)+'}'
                else: return '\\footnote{'+check+self._recurse(e)+'}'
            elif e.attrib['type']=='TODO':
                if e.text is None: raise RuntimeError(f'TODO not with no text, line {e.sourceline}')
                return r'\textbf{[TODO: '+e.text+']}'
            assert False
        elif e.tag=='lg':
            #assert e[-1].tag=='l'
            #e[-1].attrib['last-line']="1"
            assert all([e2.tag=='l' for e2 in e])
            return '\n'+ind+'\\begin{verse}\n'+self._recurse(e)+ind+'\\end{verse}\n'
        elif e.tag=='l':
            if len(e)==0: return ind+'\n'
            isLast=(e.getnext() is None)
            return ind+self._recurse(e)+(r'\\{}' if not isLast else '')+'\n'
        elif e.tag.startswith('head'): return ''
        elif e.tag in ('front','main','back'):
            if e.tag=='front': return '\n'+self._recurse(e) #\frontmatter added in vism/vimm.tex already (before ToC which is also there)
            elif e.tag=='main':
                ret='\n'+ind+'\\mainmatter'
                if self.vimm: ret+='\n'+ind+'\\vismUnnumberedPart{The Path of Freedom (\\emph{Vimuttimagga})}{The Path of Freedom\\\\ \\emph{Vimuttimagga}}\n'
                return ret+'\n'+self._recurse(e,incLev=False)
            if e.tag=='back': return '\n'+ind+'\\backmatter\n'+self._recurse(e,incLev=False)
        elif e.tag=='div':
            level,tail=int((m:=re.match('(?P<tail>(?P<level>[0-9]+)-.*)',e.attrib['type'])).group('level')),m.group('tail')
            heading=e[0]
            assert heading.tag=='head'
            toc_num=heading.attrib.get('n',None)
            def _recurse_wrap(e2):
                if e2.get('rend',None)=='hanging': return r'\begin{vismHanging}'+self._recurse(e2)+r'\end{vismHanging}'
                else: return self._recurse(e2)
            if level==1: # part
                ret='\n'+ind
                ret+='\n'+ind+self._title('part',heading,hyper=toc_num) # no heading for frontmatter
                if toc_num: ret+='\n'+ind+'    \\label{'+toc_num+'}\n\n'
                ret+=_recurse_wrap(e)
                return ret
            elif level==2: # chapter
                # \label is just for PlasTeX which can then name the output file accordingly (the chapter has an $id)
                ret='\n'+ind+self._title('chapter',heading,hyper=toc_num)
                if toc_num: ret+='\n'+ind+'    \\label{'+toc_num+'}\n' # +ind+'    \\vismHypertarget{'+toc_num+'}\n'
                return ret+_recurse_wrap(e)
                # else: return '\n'+ind+_title('chapter',heading)+_recurse(e)
            elif level==3: ret='\n'+ind+self._title('section',heading)
            elif level==4: ret='\n'+ind+self._title('subsection',heading)
            elif level==5: ret='\n'+ind+self._title('subsubsection',heading)
            elif level==6: ret='\n'+ind+r'\par\noindent[\textsc{\textbf{'+self._recurse(heading)+'}}]'
            elif level==7: ret='\n'+ind+r'\par\noindent[\emph{\textbf{'+self._recurse(heading)+'}}]'
            elif level==8: ret='\n'+ind+r'\par\noindent[\emph{'+self._recurse(heading)+'}]'
            else: raise RuntimeError(f'Unknown {level=}')
            # levels 3+
            return ret+_recurse_wrap(e)
        elif e.tag=='pb':
            if e.attrib['ed'] in ('BPS2011','BPS1995'):
                # return r'\marginnote[\footnotesize\{'+e.text+'('+e.attrib['page_id']+r')\}]{}[-1ex]' # this is too complicated for PlasTeX
                if 'pdf_page' not in e.attrib: raise RuntimeError(f'pb[@pdf_page] missing, line {e.sourceline}')
                return r'\marginnote{\textcolor{teal}{\footnotesize\{'+e.attrib['pdf_page']+'|'+e.attrib['n']+r'\}}}{}'
            elif e.attrib['ed']=='PTS': return r'\textcolor{brown}{\textit{['+e.attrib['n']+']}}'
            assert False
        elif e.tag=='anchor':
            assert 'id' in e.attrib
            return '\\vismHypertarget{'+e.attrib['id']+'}\\label{'+e.attrib['id']+'}{}'
        elif e.tag=='ptr':
            if e.attrib['type'] in ('vism','vimm','internal'):
                txt=e.text.replace('[PAGE]',', page \\pageref{'+e.attrib['target']+'}')
                return r'\hyperlink{'+e.attrib['target']+r'}{'+txt+'}{}'
            elif e.attrib['type']=='bib':
                ret=r'\textbf{\cite{'+e.attrib['target']+'}'
                if loc:=e.get('loc',None):
                    if href:=e.get('href',None): ret+=' \\href{'+self._rep(href)+'}{'+loc+'}'
                    else: ret+=loc
                return ret+'}'
            else: raise ValueError('Unknown value of type in <ptr type="{e.attrib["type"]}">, line {e.sourceline}')
            # r'\fbox{'+e.text+'→'+e.attrib['target']+'}'
            assert False
        elif e.tag in ('index','glossary'):
            title,subtitle=self._rep(e.attrib['title']),self._rep(e.attrib.get('subtitle',None))
            ret='\\chapter['+title+']{'+title+'\\* {\\large '+subtitle+'}}'
            if ii:=e.findall('introductory'):
                assert len(ii)==1
                ret+=self._recurse(ii[0])
            ret+=r'\begin{multicols}{2}'+'\n'+r'\parskip=.2\baselineskip\RaggedRight\begin{vismHanging}'+'\n'+self._recurse(e)+r'\end{vismHanging}\end{multicols}'
            return ret
        elif e.tag=='introductory': return '' # already handled in index/glossary
        elif e.tag=='entry':
            assert e.getparent().tag in ('index','glossary')
            return r'\par\textbf{'+self._rep(e.attrib['title'])+'} '+self._recurse(e)+'\n'
        elif e.tag=='table':
            tbody='    '+'\\\\\n    '.join([' & '.join([self._recurse(td) for td in tr]).strip() for tr in e])+'\n'
            nRows,nCols=len(e),len(e[0])
            assert 'rend' in e.attrib,f'<table> without @rend at line {e.sourceline}'
            layout_type=e.attrib['rend']
            if layout_type=='ceylon':
                # env,lCols,xCols='l|l|l','X[2,l]|X[4,l]|X[3,l]'
                plastex='\\begin{tabular}{l|l|l}\n'+tbody+'\\end{tabular}'
                latex='\\begin{longtblr}{colspec={X[2,l]|X[4,l]|X[3,l]}}\n'+tbody+'\\end{longtblr}'
            elif layout_type=='commentaries':
                plastex='\\begin{tabular}{ll}\n'+tbody+'\\end{tabular}'
                latex='\\begin{tblr}{colspec={Q[15em]Q[15em]}}\n'+tbody+'\\end{tblr}'
            elif layout_type=='consciousness':
                plastex='\\begin{tabular}{rrl}\n'+tbody+'\\end{tabular}'
                latex='\\begin{longtblr}[theme=vismNaked,presep=\\smallskipamount,postsep=\\smallskipamount]{colspec={X[1,r]Q[4em,r]X[1,l]},rowsep=0pt}\n'+tbody+'\\end{longtblr}'
            else: raise InvalidValue(f'latex_theme must be one of: ceylon, commentaries, consciousness (not {latex_theme}, XML line {e.sourceline}).')
            return textwrap.indent(f'\n\n\\ifplastex\n{plastex}\n\\else\n{latex}\\fi\n\\noindent\n',ind)+ind
        elif e.tag=='list':
            if e.attrib['type']=='numbered':
                assert e.attrib['type']=='numbered'
                labelSpec='label='+{'1.':'\\arabic*.','I.':'\\Roman*.','i.':'\\roman*.','(i)':'(\\roman*)','(a)':'(\\alph*)','1)':'\\arabic*)','a.':'\\alpha*.'}[e.get('subtype','1.')]
                labelSpecShort=e.get('subtype','1.')
                start=e.get("start","1")
                ret='\n\\begin{enumerate}['+labelSpecShort+',nosep'+(f',start={start}' if start!="1" else '')+']'
                for li in e:
                    assert li.tag=='item'
                    ret+='\n    \\item '+self._recurse(li)
                ret+='\n\\end{enumerate}'
            elif e.attrib['type']=='bulleted':
                ret='\n\\begin{itemize}'
                for li in e:
                    ret+='\n    \\item '+self._recurse(li)
                ret+='\n\\end{itemize}'
            elif e.attrib['type']=='gloss':
                ret='\n\\begin{description}'
                assert len(e)%2==0
                for i in range(0,len(e)//2):
                    label,item=e[2*i],e[2*i+1]
                    ret+='\n   \item['+self._recurse(label)+'] '+self._recurse(item)
                ret+='\n\\end{description}'
            else: raise ValueError(f'Unhandled list type: {e.attrib["type"]}')
            return textwrap.indent(ret,ind)
        elif e.tag=='bibliography':
            ret='\n'+ind+'\\begin{thebibliography}{xxxxxxxxxxx}'
            for bi in e:
                if bi.tag=='bibentry':
                    abbr=bi.get('abbrev')
                    ret+='\n'+ind+f'  \\bibitem[{abbr}]{{{abbr}}}'+self._recurse(bi)
                elif bi.tag=='bibintertitle':
                    assert len(bi)==0 and bi.text
                    ret+='\n'+ind+'\\vismBibIntertitle{'+bi.text+'}'
                else: assert False
            return ret+'\n'+ind+'\\end{thebibliography}\n'
        elif e.tag=='IGNORE': return ''
        # elif e.tag=='raw':return open('latex/'+e.attrib['file']+'.tex','r').read()
        elif e.tag=='ref':
            return '\href{'+e.attrib['target'].replace('#','\\#')+'}{'+self._recurse(e)+'}'
        elif e.tag=='graphic':
            return '\\begin{center}\\includegraphics[width=\\vismWdPercent{80}]{'+e.attrib['url']+'}\\end{center}'
        raise RuntimeError(f'Unhandled tag <{e.tag}>, line {e.sourceline}')




from lxml import etree
import string



class SphinxWriter(object):
    def __init__(self,outdir,vimm=False,chapters_arabic=False):
        self.footnotes={}
        self.outdir=outdir
        self.chapter=0
        self.part=0
        self.matter=None
        self.editorial_titles=False
        self.vimm=vimm
        self.toctreeLevel=0
        self.rstExt='.rst'
        self.topFiles=[]
        self.chapters_arabic=chapters_arabic
    def _flush(self):
        if not self.footnotes: return ''
        ret='\n\n.. rubric:: Footnotes\n\n'
        for k,vv in self.footnotes.items(): ret+=f'\n\n.. _{self.chapter_anchor}.n{k}:\n\n.. [#{k}] '+'\n    '.join([v for v in vv.split('\n')])+'\n'
        self.footnotes={}
        return ret
    def _rep(self,t): return t.replace('*','∗')
    def recurse(self,e):
        if e.text is not None and len(e)==0: return self._rep(e.text)
        return ''.join([self.write(e2,ord=ord) for ord,e2 in enumerate(e)])
    #def indent_except_first(self,t):
    #    i='    '
    #    t2=textwrap.indent(t,i)
    #    assert len(t2.split('\n')[0])>len(i)
    #    return t2[len(i):]
    def indent_all(self,t):
        return textwrap.indent(t,4*' ')
    def title(self,e,level,anchor=None,prefix=None,prefixSep='. '):
        ret=''
        if anchor: ret+='\n\n.. _'+anchor+':'
        t=(e if isinstance(e,str) else self.recurse(e))
        if prefix: t=prefix+prefixSep+t
        return ret+'\n\n'+t+'\n'+(len(t)+4)*('#*=-^"\''[level])
    def enclose(self,t,c):
        if t.strip()=='': return ' '
        ret=t
        if ret.endswith(' '): ret=ret.rstrip()+c+' '
        else: ret=ret+c+'\\ '
        if ret.startswith(' '): ret=' '+c+ret.lstrip()
        else: ret=c+ret
        return ret
    def writeIndex(self,title):
        f=f'{self.outdir}/index.rst'
        print(f'→ {f}')
        idx=open(f,'w')
        idx.write(f'{title}\n{"="*len(title)}\n\n.. toctree::\n   :maxdepth: 6\n\n   ')
        idx.write('\n   '.join(self.topFiles)+'\n')
    def writeRst(self,*,e,fname,title,num=None,anchor=None,prefix=None,subTree=True):
        f2=f'{self.outdir}/{fname}'
        currOut=open(f2,'w')
        print('  '*self.toctreeLevel+f'→ {f2}')
        currOut.write(self.title(title,level=1,anchor=anchor,prefix=prefix)+'\n\n')
        if self.toctreeLevel==0: self.topFiles.append(fname)
        if subTree:
            self.toctreeLevel+=1
            currOut.write('.. toctree::\n   :maxdepth: 6\n\n')
            for sub in e:
                currOut.write('\n   '+(subF:=self.write(sub)))
            self.toctreeLevel-=1
        else:
            for sub in e:
                currOut.write(self.write(sub))
        currOut.write(self._flush())
        currOut.close()

    def write(self,e,ord=-1):
        def _nobraces(t):
            return t.replace('[','').replace(']','')
        if isinstance(e,etree._Comment): return''
        if e.tag=='TEI': return self.recurse(e)
        elif e.tag=='teiHeader': return ''
        elif e.tag=='text':
            for e2 in e: self.write(e2)
            return ''
        elif e.tag in ('front','main','back'):
            self.matter={'front':-1,'main':0,'back':1}[e.tag]
            self.chapter=0
            if e.tag in ('front',):
                self.writeRst(e=e,fname=e.tag+self.rstExt,title={'front':'Front'}[e.tag],subTree=True)
            else:
                for p in e: self.write(p)
            return None
        elif e.tag.startswith('head'): return ''
        elif e.tag.startswith('div'):
            level,tail=int((m:=re.match('(?P<tail>(?P<level>[0-9]+)-.*)',e.attrib['type'])).group('level')),m.group('tail')
            anchor=e.get('id',None)
            heading=e[0]
            assert heading.tag.startswith('head')
            toc_num=heading.attrib.get('n',None)
            if toc_num and anchor: raise RuntimeError('{e.sourceline}: both {e.attrib["id"]=} and {heading.attrib["n"]=} are defined.')
            if toc_num: anchor=toc_num
            assert 0<level<9
            import roman
            if level==1: # part
                self.part+=1
                R=roman.toRoman(self.part)
                self.writeRst(e=e,fname=f'part-{R}{self.rstExt}',title=self.recurse(heading),anchor=f'p{R}',num=self.part,prefix=f'Part {R}',subTree=True)
                return None
            elif level==2:
                self.chapter+=1
                if self.matter==-1:  f=f'front-{"_ABCDEFGHIJKLMN"[self.chapter]}'
                elif self.matter==0: f=f'ch-{self.chapter:02d}'
                elif self.matter==1: f=f'back-{"_ABCDEFGHI"[self.chapter]}'
                f+=self.rstExt
                if anchor is None:
                    anchor=((str(self.chapter) if self.chapters_arabic else roman.toRoman(self.chapter)) if self.matter==0 else None)
                    prefix=anchor
                else:
                    # this is to handle cases when chapter has an ID (e.g. in mctb2 a chapter in frontmatter), abut it should not be shown as prefix
                    prefix=None
                self.chapter_anchor=anchor
                self.writeRst(e=e,fname=f,title=self.recurse(heading),anchor=anchor,prefix=prefix,subTree=False)
                return f
            elif 3<=level<=6:
                return self.title(heading,prefix=e.attrib.get('n',None),prefixSep=' ',level=level)+'\n\n'+self.recurse(e)
            else:
                dd={7:'**',8:'*'}[level]
                return '\n\n'+dd+'['+self.recurse(heading)+']'+dd+'\\ '+'\n\n'+self.recurse(e)
        elif e.tag=='p':
            if not self.editorial_titles and e.get('type',None)=='editorial_title': return ''
            if anchor:=e.attrib.get('id',None):
                # <https://github.com/eudoxos/vism/issues/new?title=issue%20at%20{anchor}&body=({vismCommitTimestampQuery})>
                import roman
                pre=f'\n\n.. _{anchor}:\n\n:ref:`§{e.attrib["n"]} <{anchor}>` '
                return pre+self.recurse(e)
            else:
                pre=('\n\n' if ord>0 else '\n\n') ## ??
                tail=self.recurse(e)
                # fix what looks like start of enumeration but is not
                if len(e)>0 and e[0].tag=='span' and re.match('\([0-9]+\) |[0-9]+\. |[a-zA-Z]\. |\([a-zA-Z]\) ',tail): tail='\\'+tail
                return pre+tail
        elif e.tag=='em':
            assert len(e)==0
            if e.text is None: return ''
            return self.enclose(self._rep(e.text),'*')
        elif e.tag=='span':
            assert len(e)==0
            if e.text is None: return ''
            tx=self._rep(e.text)
            if (fam:=e.attrib.get('rend',None)) is None: return tx
            elif fam=='italic': return self.enclose(tx,'*')
            elif fam=='bold': return self.enclose(tx,'**')
            elif fam=='smallcaps': return self.enclose(tx,'``')
            elif fam=='bold-italic': return self.enclose(tx,'``')
            else: raise RuntimeError(f'Unrecognized family {fam}')
        elif e.tag=='note':
            if e.get('place',None)=='foot':
                anchor=e.attrib.get("id",str(len(self.footnotes)+1))
                if self.vimm:
                    if len(self.footnotes)==0: mark="1"
                    else: mark=str(int(list(self.footnotes.keys())[-1])+1)
                else:
                    mark=e.attrib['n']
                    if 'reference_existing_footnote' in e.attrib:
                        return f' [#{mark}]_'
                self.footnotes[mark]=self.recurse(e)
                return f' [#{mark}]_ '
            elif e.get('type',None)=='TODO':
                return f'**TODO: {e.text}**\ '
            raise RuntimeError(f'Unhandled <note>, line {e.sourceline}')
        elif e.tag=='lg':
            return '\n\n'+self.recurse(e)
        elif e.tag=='l':
            isLast=(e.getnext() is None)
            return ('\n\n' if ord==0 else '')+'\n| '+self.recurse(e)+('\n' if isLast else '')
        elif e.tag=='pb':
            if e.attrib['ed'] in ('BPS2011','BPS1995'): return f'*[{e.attrib["n"]}/{e.attrib["pdf_page"]}]* '
            elif e.attrib['ed']=='PTS': return f' ``{e.attrib["n"]}`` '
            assert False
        elif e.tag=='anchor':
            return f'\n\n.. _{e.get("id")}:\n\n'
        elif e.tag=='ptr':
            if e.attrib['type'] in ('vism','vimm','internal'):
                return f':ref:`{e.text.replace("[PAGE]","")} <{e.attrib["target"]}>`'
            elif e.attrib['type']=='bib':
                ret=f' [{e.attrib["target"].replace(".","").replace(" ","")}]_ '
                if loc:=e.get('loc',None):
                    if href:=e.get('href',None): ret+=f'`{loc.strip()} <{href}>`__'
                    else: ret+=self.enclose(loc,'*')
                #+(self.enclose(e.attrib["loc"],'*') if 'loc' in e.attrib else '')+' '
                return ret+' '
            assert False
        elif e.tag in ('index','glossary'):
            title,subtitle=e.attrib['title'],e.attrib['subtitle']
            if e.tag=='index':      out,ret='index_',self.title(e=f'{title} ({subtitle})',level=1,anchor='index')
            elif e.tag=='glossary': out,ret='glossary',self.title(e=f'{title} ({subtitle})',level=1,anchor='glossary')
            if ii:=e.findall('introductory'):
                assert len(ii)==1
                ret+='\n\n'+self.recurse(ii[0])
            ret+='\n\n.. glossary::'
            ret+=self.recurse(e)
            f0=f'{out}{self.rstExt}'
            self.topFiles.append(f0)
            f=f'{self.outdir}/{f0}'
            print(f'→ {f}')
            open(f,'w').write(ret)
            return
        elif e.tag=='introductory': return ''
        elif e.tag=='entry':
            title=e.attrib["title"].replace("*","\\*")
            return f'\n\n   {title}\n          '+self.recurse(e)
        elif e.tag=='IGNORE': return ''
        elif e.tag=='table':
            layout_type=e.attrib['rend']
            ret='\n\n.. list-table::\n'
            if layout_type=='commentaries': ret+='  :header-rows: 1\n\n'
            elif layout_type=='ceylon': ret+='  :header-rows: 1\n  :widths: 30 20 40\n\n'
            elif layout_type=='consciousness': ret+='  :width: 80%\n  :widths: 4 1 4\n\n'
            maxCol=max([len(tr) for tr in e])
            for irow,tr in enumerate(e):
                assert tr.tag=='row'
                for icol,td in enumerate(tr):
                    assert td.tag=='cell'
                    cont=self.recurse(td)
                    # escape (xiv) which would be turned into 'xiv.' (as enumeration start)
                    if icol==1 and len(cont)>0 and cont[0]=='(': cont='\\'+cont
                    ret+='\n  '+('*' if icol==0 else ' ')+' - '+cont.strip()
                for icol in range(len(tr),maxCol):
                    ret+='\n  '+('*' if icol==0 else ' ')+' - '
            return ret+'\n'
        elif e.tag=='list':
            if e.attrib['type']=='numbered':
                assert e.attrib['type']=='numbered'
                import roman
                iOff=int(e.get('start','1'))
                def _mkLabel(i):
                    return {
                        '1.':f'{i+iOff}.',
                        '1)':f'{i+iOff})',
                        'I.':f'{roman.toRoman(i+iOff)}.',
                        'i.':f'{roman.toRoman(i+iOff).lower()}.',
                        '(i)':f'({roman.toRoman(i+iOff).lower()})',
                        '(a)':f'({(string.ascii_lowercase+string.ascii_uppercase)[i+iOff-1]})',
                        'a.':f'{(string.ascii_lowercase+string.ascii_uppercase)[i+iOff-1]}.',
                    }[e.get('subtype','1.')]
                ret='\n'
                for i,li in enumerate(e):
                    label=_mkLabel(i)
                    ret+=f'\n\n{label} '+self.indent_all(self.recurse(li))
                ret+='\n\n'
                return ret
            elif e.attrib['type']=='bulleted':
                ret='\n'
                for i,li in enumerate(e):
                    ret+=f'\n\n* '+self.indent_all(self.recurse(li))
                ret+='\n\n'
                return ret
            elif e.attrib['type']=='gloss':
                ret='\n'
                for i in range(0,len(e)//2):
                    label,item=e[2*i],e[2*i+1]
                    ret+=f'\n{self.recurse(label)}\n    {self.indent_all(self.recurse(item))}'
                ret+='\n\n'
                return ret
            else: raise ValueError(f'Unhandled list type: {e.attrib["type"]}')
        elif e.tag=='bibliography':
            ret='\n\n'
            for bi in e:
                if bi.tag=='bibentry':
                    ret+=f'\n.. [{bi.get("abbrev").replace(".","").replace(" ","")}] '+self.recurse(bi).replace('\n','\n     ')
                else: assert False
            return ret
        elif e.tag=='ref':
            return f'`{self.recurse(e)} <{e.attrib["target"]}>`__'
        elif e.tag=='graphic':
            return f'\n\n .. image:: {e.attrib["url"]}\n    :width: 80%\n\n'
        raise RuntimeError(f'Unhandled tag <{e.tag}>')




class SphinxWriterMyST(object):
    def __init__(self,outdir,vimm=False,chapters_arabic=False):
        self.footnotes={}
        self.outdir=outdir
        self.chapter=0
        self.part=0
        self.matter=None
        self.editorial_titles=False
        self.vimm=vimm
        self.toctreeLevel=0
        self.rstExt='.md'
        self.topFiles=[]
        self.chapters_arabic=chapters_arabic
    def _flush(self):
        if not self.footnotes: return ''
        ret='\n\n:::{rubric} Footnotes\n\n:::\n\n'
        for k,vv in self.footnotes.items(): ret+=f'\n({self.chapter_anchor}.n{k})=\n\n[^{k}]:'+'\n    '.join([v for v in vv.split('\n')])+'\n'
        self.footnotes={}
        return ret
    def _rep(self,t): return t.replace('*','∗')
    def recurse(self,e):
        if e.text is not None and len(e)==0: return self._rep(e.text)
        return ''.join([self.write(e2,ord=ord) for ord,e2 in enumerate(e)])
    #def indent_except_first(self,t):
    #    i='    '
    #    t2=textwrap.indent(t,i)
    #    assert len(t2.split('\n')[0])>len(i)
    #    return t2[len(i):]
    def indent_all(self,t):
        return textwrap.indent(t,2*' ')
    def title(self,e,level,anchor=None,prefix=None,prefixSep='. '):
        ret='\n\n'
        if anchor: ret+=f'({anchor})=\n\n'
        t=(e if isinstance(e,str) else self.recurse(e))
        if prefix: t=prefix+prefixSep+t
        return f'{ret}{level*"#"} {t}'
    def enclose(self,t,c):
        if t.strip()=='': return ' '
        ret=t
        if ret.endswith(' '): ret=ret.rstrip()+c+' '
        else: ret=ret+c  # +'\\ '
        if ret.startswith(' '): ret=' '+c+ret.lstrip()
        else: ret=c+ret
        return ret
    def writeIndex(self,title):
        f=f'{self.outdir}/index.md'
        print(f'→ {f}')
        idx=open(f,'w')
        idx.write(f'# {title}\n\n:::{{toctree}}\n:maxdepth: 6\n\n')
        idx.write('\n'.join(self.topFiles)+'\n')
        idx.write(':::\n')
    def writeRst(self,*,e,fname,title,num=None,anchor=None,prefix=None,subTree=True):
        f2=f'{self.outdir}/{fname}'
        currOut=open(f2,'w')
        print('  '*self.toctreeLevel+f'→ {f2}')
        currOut.write(self.title(title,level=1,anchor=anchor,prefix=prefix)+'\n\n')
        if self.toctreeLevel==0: self.topFiles.append(fname)
        if subTree:
            self.toctreeLevel+=1
            currOut.write(':::{toctree}\n:maxdepth: 6\n\n')
            for sub in e:
                currOut.write('\n'+(subF:=self.write(sub)))
            currOut.write('\n:::\n')
            self.toctreeLevel-=1
        else:
            for sub in e:
                currOut.write(self.write(sub))
        currOut.write(self._flush())
        currOut.close()

    def write(self,e,ord=-1):
        def _nobraces(t):
            return t.replace('[','').replace(']','')
        if isinstance(e,etree._Comment): return''
        if e.tag=='TEI': return self.recurse(e)
        elif e.tag=='teiHeader': return ''
        elif e.tag=='text':
            for e2 in e: self.write(e2)
            return ''
        elif e.tag in ('front','main','back'):
            self.matter={'front':-1,'main':0,'back':1}[e.tag]
            self.chapter=0
            if e.tag in ('front',):
                self.writeRst(e=e,fname=e.tag+self.rstExt,title={'front':'Front'}[e.tag],subTree=True)
            else:
                for p in e: self.write(p)
            return None
        elif e.tag.startswith('head'): return ''
        elif e.tag.startswith('div'):
            level,tail=int((m:=re.match('(?P<tail>(?P<level>[0-9]+)-.*)',e.attrib['type'])).group('level')),m.group('tail')
            anchor=e.get('id',None)
            heading=e[0]
            assert heading.tag.startswith('head')
            toc_num=heading.attrib.get('n',None)
            if toc_num and anchor: raise RuntimeError('{e.sourceline}: both {e.attrib["id"]=} and {heading.attrib["n"]=} are defined.')
            if toc_num: anchor=toc_num
            assert 0<level<9
            import roman
            if level==1: # part
                self.part+=1
                R=roman.toRoman(self.part)
                self.writeRst(e=e,fname=f'part-{R}{self.rstExt}',title=self.recurse(heading),anchor=f'p{R}',num=self.part,prefix=f'Part {R}',subTree=True)
                return None
            elif level==2:
                self.chapter+=1
                if self.matter==-1:  f=f'front-{"_ABCDEFGHIJKLMN"[self.chapter]}'
                elif self.matter==0: f=f'ch-{self.chapter:02d}'
                elif self.matter==1: f=f'back-{"_ABCDEFGHI"[self.chapter]}'
                f+=self.rstExt
                if anchor is None:
                    anchor=((str(self.chapter) if self.chapters_arabic else roman.toRoman(self.chapter)) if self.matter==0 else None)
                    prefix=anchor
                else:
                    # this is to handle cases when chapter has an ID (e.g. in mctb2 a chapter in frontmatter), abut it should not be shown as prefix
                    prefix=None
                self.chapter_anchor=anchor
                self.writeRst(e=e,fname=f,title=self.recurse(heading),anchor=anchor,prefix=prefix,subTree=False)
                return f
            elif 3<=level<=6:
                return self.title(heading,prefix=e.attrib.get('n',None),prefixSep=' ',level=level-1)+'\n\n'+self.recurse(e)
            else:
                dd={7:'**',8:'*'}[level]
                return '\n\n'+dd+'['+self.recurse(heading)+']'+dd+'\n\n'+self.recurse(e)
        elif e.tag=='p':
            if not self.editorial_titles and e.get('type',None)=='editorial_title': return ''
            if anchor:=e.attrib.get('id',None):
                # <https://github.com/eudoxos/vism/issues/new?title=issue%20at%20{anchor}&body=({vismCommitTimestampQuery})>
                pre=f'\n\n({anchor})=\n\n{{ref}}`§{e.attrib["n"]} <{anchor}>` '
                return pre+self.recurse(e)
            else:
                pre=('\n\n' if ord>0 else '\n\n') ## ??
                tail=self.recurse(e)
                # fix what looks like start of enumeration but is not
                # if len(e)>0 and e[0].tag=='span' and re.match('\([0-9]+\) |[0-9]+\. |[a-zA-Z]\. |\([a-zA-Z]\) ',tail): tail='\\'+tail
                return pre+tail
        elif e.tag=='em':
            assert len(e)==0
            if e.text is None: return ''
            return self.enclose(self._rep(e.text),'*')
        elif e.tag=='span':
            assert len(e)==0
            if e.text is None: return ''
            tx=self._rep(e.text)
            if (fam:=e.attrib.get('rend',None)) is None: return tx
            elif fam=='italic': return self.enclose(tx,'*')
            elif fam=='bold': return self.enclose(tx,'**')
            elif fam=='smallcaps': return self.enclose(tx,'``')
            elif fam=='bold-italic': return self.enclose(tx,'``')
            else: raise RuntimeError(f'Unrecognized family {fam}')
        elif e.tag=='note':
            if e.get('place',None)=='foot':
                anchor=e.attrib.get("id",str(len(self.footnotes)+1))
                if self.vimm:
                    if len(self.footnotes)==0: mark="1"
                    else: mark=str(int(list(self.footnotes.keys())[-1])+1)
                else:
                    mark=e.attrib['n']
                    if 'reference_existing_footnote' in e.attrib:
                        return f' [^{mark}]'
                self.footnotes[mark]=self.recurse(e)
                return f' [^{mark}]'
            elif e.get('type',None)=='TODO':
                return f'**TODO: {e.text}**'
            raise RuntimeError(f'Unhandled <note>, line {e.sourceline}')
        elif e.tag=='lg':
            return '\n:::{line-block}\n'+self.recurse(e)+'\n:::\n'
        elif e.tag=='l':
            #isLast=(e.getnext() is None)
            #return ('\n\n' if ord==0 else '')+'\n| '+self.recurse(e)+('\n' if isLast else '')
            return '\n'+self.recurse(e)
        elif e.tag=='pb':
            assert e.attrib['ed'] in ('BPS2011','BPS1995','PTS')
            anchorName=f'page-{e.attrib["ed"]}-{e.attrib["n"]}'
            anchor=f'{{anchor}}`{anchorName}`'
            if e.attrib['ed'] in ('BPS2011','BPS1995'): return anchor+f' [{{ref}}`{e.attrib["n"]} <{anchorName}>`/{e.attrib["pdf_page"]}]{{.pb-tag-BPS}} '
            elif e.attrib['ed']=='PTS': return anchor+f' [{{ref}}`{e.attrib["n"]} <{anchorName}>`]{{.pb-tag-PTS}} '
            assert False
        elif e.tag=='anchor':
            return f'\n\n({e.get("id")})=\n\n'
        elif e.tag=='ptr':
            if e.attrib['type'] in ('vism','vimm','internal'):
                return f'{{ref}}`{e.text.replace("[PAGE]","")} <{e.attrib["target"]}>`'
            elif e.attrib['type']=='bib':
                ret=f'{{term}}`{e.attrib["target"]}`'
                if loc:=e.get('loc',None):
                    if href:=e.get('href',None): ret+=f'[{loc.strip()}]({href})'
                    else: ret+=' '+self.enclose(loc,'*')
                #+(self.enclose(e.attrib["loc"],'*') if 'loc' in e.attrib else '')+' '
                return ret
            assert False
        elif e.tag in ('index','glossary'):
            title,subtitle=e.attrib['title'],e.attrib['subtitle']
            if e.tag=='index':      out,ret='index_',self.title(e=f'{title} ({subtitle})',level=1,anchor='index')
            elif e.tag=='glossary': out,ret='glossary',self.title(e=f'{title} ({subtitle})',level=1,anchor='glossary')
            if ii:=e.findall('introductory'):
                assert len(ii)==1
                ret+='\n\n'+self.recurse(ii[0])
            ret+='\n\n{.glossary}\n'
            ret+=self.recurse(e)
            ret+='\n\n'
            f0=f'{out}{self.rstExt}'
            self.topFiles.append(f0)
            f=f'{self.outdir}/{f0}'
            print(f'→ {f}')
            open(f,'w').write(ret)
            return
        elif e.tag=='introductory': return ''
        elif e.tag=='entry':
            title=e.attrib["title"].replace("*","\\*")
            return f'\n{title}\n: '+self.recurse(e)
        elif e.tag=='IGNORE': return ''
        elif e.tag=='table':
            layout_type=e.attrib['rend']
            ret=f'\n\n:::{{list-table}}\n'
            if layout_type=='commentaries': ret+=':header-rows: 1\n\n'
            elif layout_type=='ceylon': ret+=':header-rows: 1\n:widths: 30 20 40\n\n'
            elif layout_type=='consciousness': ret+=':width: 80%\n:widths: 4 1 4\n\n'
            maxCol=max([len(tr) for tr in e])
            for irow,tr in enumerate(e):
                assert tr.tag=='row'
                for icol,td in enumerate(tr):
                    assert td.tag=='cell'
                    cont=self.recurse(td)
                    # escape (xiv) which would be turned into 'xiv.' (as enumeration start)
                    if icol==1 and len(cont)>0 and cont[0]=='(': cont='\\'+cont
                    ret+='\n'+('*' if icol==0 else ' ')+' - '+cont.strip()
                for icol in range(len(tr),maxCol):
                    ret+='\n'+('*' if icol==0 else ' ')+' - '
            return ret+'\n\n:::\n\n'
        elif e.tag=='list':
            if e.attrib['type']=='numbered':
                assert e.attrib['type']=='numbered'
                import roman
                iOff=int(e.get('start','1'))
                mystStyle={
                        '1.':'decimal',
                        '1)':'decimal',
                        'I.':'upper-roman',
                        'i.':'lower-roman',
                        '(i)':'lower-roman',
                        '(a)':'lower-alpha',
                        'a.':'lower-alpha',
                    }[e.get('subtype','1.')]
                ret=f'\n{{style={mystStyle}}}\n'
                for i,li in enumerate(e):
                    label=f'{i+iOff}.'
                    ret+=f'\n{label} '+self.indent_all(self.recurse(li))
                ret+='\n\n'
                return ret
            elif e.attrib['type']=='bulleted':
                ret='\n'
                for i,li in enumerate(e):
                    ret+=f'\n\n* '+self.indent_all(self.recurse(li))
                ret+='\n\n'
                return ret
            elif e.attrib['type']=='gloss':
                ret='\n'
                for i in range(0,len(e)//2):
                    label,item=e[2*i],e[2*i+1]
                    ret+=f'\n{self.recurse(label)}\n:  {self.indent_all(self.recurse(item))}'
                ret+='\n\n'
                return ret
            else: raise ValueError(f'Unhandled list type: {e.attrib["type"]}')
        elif e.tag=='bibliography':
            ret='\n\n{.glossary}'
            for bi in e:
                if bi.tag=='bibentry':
                    ret+=f'\n{bi.get("abbrev")}\n: '+self.recurse(bi).replace('\n','\n  ')+'\n'
                    # .. [{bi.get("abbrev").replace(".","").replace(" ","")}] '+self.recurse(bi).replace('\n','\n     ')
                else: assert False
            return ret
        elif e.tag=='ref':
            return f'[{self.recurse(e)}]({e.attrib["target"]})'
        elif e.tag=='graphic':
            return f'\n\n:::{{image}} {e.attrib["url"]}\n:width: 80%\n:::\n\n'
        raise RuntimeError(f'Unhandled tag <{e.tag}>')



## DocBook
from lxml import etree
import os
import copy

# bibDocbook=etree.parse('docbook/bib.xml',etree.XMLParser(remove_blank_text=True)).getroot()
global _docbook_frontmatter
_docbook_frontmatter=False

def _docb_writer(e,ord=0,parent=None,xslTNG=False):
    xlinkNs='http://www.w3.org/1999/xlink'
    xmlNs='http://www.w3.org/XML/1998/namespace'
    xmlPrefix='{'+xmlNs+'}'
    editorial_titles=False

    if xslTNG:
        xlinkPrefix='{'+xlinkNs+'}'
        nsmap={None:'http://docbook.org/ns/docbook','xlink':xlinkNs,'xml':xmlNs}
    else:
        #nsmap={None:'http://docbook.org/ns/docbook','xml':xmlNs}
        #xlinkPrefix=''
        nsmap,xlinkPrefix=None,''

    def _E(e,text=None,*,subs=[],xml_id=None,**kw):
        assert text is None or isinstance(text,str)
        ret=etree.Element(e,**kw,nsmap=nsmap) # ,'pub':pubNs})
        if xml_id is not None:
            # if xslTNG:
            ret.attrib[xlinkPrefix+'label']=xml_id
            ret.attrib[xmlPrefix+'id']=xml_id
        if 'linkend' in kw:
            if xslTNG:
                ret.attrib[xlinkPrefix+'to']=kw['linkend']
                kw.pop('linkend')
            pass
        ret.text=text
        for sub in subs:
            if sub is None: continue
            # print(sub)
            if sub.tag=='__FLATTEN__':
                for su in sub: ret.append(su)
            else: ret.append(sub)
        return ret

    def _curr_chapter(e):
        while (e:=e.getparent()) is not None:
            if e.tag=='div' and e.get('type',None)=='2-chapter':
                heading=e[0]
                assert heading.tag.startswith('head')
                return heading.attrib.get('n',None)


    def _recurse(e,dbg=False):
        if e.text is not None and len(e)==0:
            if dbg: print('=',e.text)
            return [_E('phrase',e.text)]
        if e.text is not None and e.text!='' and len(e)>0:
            print('$$$$',e.tag,e.sourceline) # ,len(e.text),e.text)
        ret=[_docb_writer(e2,ord=ord,parent=e) for ord,e2 in enumerate(e)]
        if dbg: print('|'.join([r.text for r in ret if r.text]))
        return ret
    if isinstance(e,etree._Comment): return None
    if e.tag=='TEI':
        # return _E('book',xmlns='http://docbook.org/ns/docbook',version="5.0",subs=_recurse(e))
        info=e[0]
        # print(info)
        assert info.tag=='info' # DocBook metadata, injected below
        b=_E('book',version="5.2",subs=[copy.copy(info)]+_recurse(e))
        global _docbook_frontmatter
        _docbook_frontmatter=True
        # b.append(bibDocbook)
        return b
        # b.attrib['xmlns:pub']="http://docbook.org/ns/docbook/publishers"
    elif e.tag=='info': return None
    elif e.tag=='teiHeader': return None
    elif e.tag in ('text','front','main','back'):
        return _E('__FLATTEN__',subs=_recurse(e))
    elif e.tag=='em':
        assert len(e)==0
        return _E('emphasis',e.text)
    elif e.tag=='span':
        assert len(e)==0
        if e.text is None: return None
        if (fam:=e.attrib.get('rend',None)) is None: return _E('phrase',e.text)
        elif fam=='italic': return _E('emphasis',e.text)
        elif fam=='bold': return _E('emphasis',e.text,role='bold')
        elif fam=='smallcaps': return _E('emphasis',e.text,role='smallcaps')
        elif fam=='bold-italic': return _E('emphasis',e.text,role='bold-italic')
        else: raise RuntimeError(f'Unrecognized family {fam}')
    elif e.tag=='p':
        if not editorial_titles and e.get('type',None)=='editorial_title': return None
        if 'id' in e.attrib:
            return _E('formalpara',xml_id=e.attrib['id'],subs=[_E('title','§'+e.attrib['n']),_E('para',subs=_recurse(e))])
        else: return _E('para',subs=_recurse(e))
    elif e.tag=='note':
        if e.get('place',None)=='foot':
            if (ch:=_curr_chapter(e)) is None:
                assert 'reference_existing_footnote' not in e.attrib
                return _E('footnote',subs=_recurse(e))
            else:
                label=f'{ch}.n{e.attrib["n"]}'
                if 'reference_existing_footnote' in e.attrib: return _E('footnoteref',linkend=label)
                return _E('footnote',subs=_recurse(e),xml_id=label)
        elif e.attrib['type']=='TODO': return _E('emphasis','[TODO: '+e.text+']',role='bold')
        raise RuntimeError('Unhandled note type, line {e.sourceline}')
    elif e.tag=='lg':
        for ich,ch in enumerate(e):
            if not ch.tag=='l':
                raise RuntimeError(f'<lg> may contain only <l> elements (<lg> at line {e.sourceline}; child #{ich} <{ch.tag}>, line {ch.sourceline})')
        return _E('linegroup',subs=[_E('speaker')]+_recurse(e))
        return _E('linegroup',subs=[_E('speaker')]+_recurse(e))
        # return _E('poetry',subs=[_E('linegroup',subs=_recurse(e))])
    elif e.tag=='l': return _E('line',subs=_recurse(e))
    elif e.tag=='div':
        level,tail=int((m:=re.match('(?P<tail>(?P<level>[0-9]+)-.*)',e.attrib['type'])).group('level')),m.group('tail')
        heading=e[0]
        assert heading.tag.startswith('head')
        toc_num=e.attrib.get('id',None)
        title=[_E('title',subs=_recurse(heading))]
        if level==1: # part
            # nonlocal _docbook_frontmatter
            _docbook_frontmatter=((name:=e.attrib['name'])=='(Front)')
            if _docbook_frontmatter: return _E('__FLATTEN__',subs=_recurse(e))
            kw=({'xml_id':'part-'+toc_num} if toc_num else {})
            return _E('part',subs=title+_recurse(e),**kw)
        elif level==2:
            # nonlocal _docbook_frontmatter
            if _docbook_frontmatter: return _E('preface',subs=title+_recurse(e))
            if sub:=heading.get('subtitle_pali',None): title+=[_E('subtitle',subs=[_E('phrase',subs=[_E('emphasis',text=sub)])])]
            return _E('chapter',subs=title+_recurse(e),xml_id=toc_num)
        else: return _E('section',subs=title+_recurse(e))
    elif e.tag.startswith('head'): return None
    # elif e.tag in ('struct-3-section','struct-4-subsection','struct-5-subsubsection','struct-6-subsubsubsection','struct-7-subsubsubsubsection','struct-8-subsubsubsubsubsection'): return _E('section',subs=_recurse(e))
    elif e.tag=='pb':
        # return None # XXXXX
        if e.attrib['ed'] in ('BPS2011','BPS1995'): return _E('literal',f'[{e.attrib["pdf_page"]}|{e.attrib["n"]}]')
        elif e.attrib['ed']=='PTS': return _E('varname',f'({e.attrib["n"]})')
    elif e.tag=='ptr':
        if e.attrib['type'] in ('vism','vimm','internal'): return _E('link',e.text.replace("[PAGE]",""),linkend=e.attrib['target'])
        elif e.attrib['type']=='bib':
            if 'loc' in e.attrib: return _E('phrase',subs=[_E('citation',e.attrib['target']),_E('phrase',' '+e.attrib['loc'])])
            return _E('citation',e.attrib['target'])
        assert False
    elif e.tag=='anchor':
        return _E('anchor',xml_id=e.attrib['id'])
    elif e.tag=='index': return _E('index',subs=[_E('title',e.attrib['title']),_E('subtitle',e.attrib['subtitle'])]+_recurse(e))
    elif e.tag=='glossary':  return _E('glossary',subs=[_E('title',e.attrib['title']),_E('subtitle',e.attrib['subtitle'])]+_recurse(e))
    elif e.tag=='introductory': return _E('para',subs=_recurse(e))
    elif e.tag=='entry':
        if parent.tag=='index': return _E('primaryie',subs=[_E('emphasis',text=e.attrib['title'],role='bold')]+_recurse(e))
        elif parent.tag=='glossary': return _E('glossentry',subs=[_E('glossterm',text=e.attrib['title'])]+[_E('glossdef',subs=_recurse(e))])
        print(parent.tag)
        assert False
    elif e.tag=='table':
        hasHead=(e.attrib['rend']!='consciousness')
        tab=_E('informaltable',subs=([_E('thead')] if hasHead else [])+[_E('tbody')])
        for irow,tr in enumerate(e):
            assert tr.tag=='row' and set([td.tag for td in tr])=={'cell'}
            row=_E('tr',subs=[_E('td',subs=(_recurse(td) if len(td)>0 else []),valign='top') for td in tr])
            tab[min(irow,1) if hasHead else 0].append(row)
        return tab
    elif e.tag=='list':
        assert e.attrib['type']=='numbered'
        enum=_E('orderedlist',numeration={'1.':'arabic','I.':'upperroman','i.':'lowerroman','(i)':'lowerroman','(a)':'loweralpha'}[e.get('subtype','1.')])
        if 'start' in e.attrib: enum.attrib['startingnumber']=e.attrib['start']
        for li in e:
            enum.append(_E('listitem',subs=_recurse(li)))
            # if 'label' in e.attrib: print('Ignoring custom label "{e.attrib["label"]}" (line {li.sourceline})')
        return enum
    elif e.tag=='bibliography':
        bib0=_E('bibliography',subs=[bib:=_E('bibliodiv')])
        for bi in e:
            if bi.tag=='bibentry': bib.append(_E('biblioentry',subs=[_E('abbrev',bi.attrib['abbrev']),_E('title',subs=_recurse(bi))]))
            elif bi.tag=='bibintertitle': bib0.append(bib:=_E('bibliodiv',subs=[_E('title',bi.text)]))
            else: raise ValueError(f'Unhandled tag in bibliography: {bi.tag} {bi.sourceline}')
            # else: assert False
        return bib0
    elif e.tag=='raw':
        return etree.parse('docbook/'+e.attrib['file']+'.xml',etree.XMLParser(remove_blank_text=True)).getroot()
    #elif e.tag=='TODO':
    #    return _E('emphasis','[TODO: '+e.text+']',role='bold')
    elif e.tag=='IGNORE': return None
    raise RuntimeError(f'Unhandled tag <{e.tag}>')

def _docbook_fix_formalpara(book):
    for fp in book.findall('.//formalpara'):
        subs=[]
        p=fp
        while ((p:=p.getnext()) is not None) and (p.tag in ('para','linegroup')):
            subs.append(p)
        for p in subs: fp.append(p)
    return book



##### HTML5
from lxml import etree
import os
import re

_html5_frontmatter=False

class InFootnote(object):
    def __init__(self,writer): self.writer=writer
    def __enter__(self): self.writer.inFootnote=True
    def __exit__(self,*args): self.writer.inFootnote=False

class Html5Writer():
    def __init__(self,editorial_titles=False):
        self.inFootnote=False
        self.editorial_titles=editorial_titles
    def write(self,e,ord=0,parent=None):

    #def _html5_writer(e,ord=0,parent=None):
    #    editorial_titles=False

        def _E(e,text=None,*,subs=[],xml_id=None,**kw):
            assert text is None or isinstance(text,str)
            if 'class_' in kw: kw['class']=kw.pop('class_')
            ret=etree.Element(e,**kw) #,nsmap=nsmap) # ,'pub':pubNs})
            if xml_id is not None: ret.attrib['id']=xml_id
            ret.text=text
            assert not isinstance(subs,etree._Element)
            assert isinstance(subs,list)
            for sub in subs:
                if sub is None: continue
                if sub.tag=='__FLATTEN__':
                    for su in sub: ret.append(su)
                else: ret.append(sub)
            return ret

        def _curr_chapter(e):
            while (e:=e.getparent()) is not None:
                if e.tag=='div' and e.get('type',None)=='2-chapter':
                    assert e[0].tag.startswith('head')
                    return e[0].get('n',None)

        def _recurse(e,dbg=False):
            if e.text is not None and len(e)==0:
                if dbg: print('=',e.text)
                return [_E('span',e.text)]
            if e.text is not None and e.text!='' and len(e)>0:
                print('$$$$',e.tag,e.sourceline) # ,len(e.text),e.text)
                assert False
            ret=[self.write(e2,ord=ord,parent=e) for ord,e2 in enumerate(e)]
            if dbg: print('|'.join([r.text for r in ret if r.text]))
            return ret
        if isinstance(e,etree._Comment): return None
        if e.tag=='TEI':
            # _E('head',subs=[_E('link',rel='stylesheet',href='style.A4.css')]),
            return _E('html',subs=[_E('body',subs=_recurse(e))],lang='en')
        elif e.tag=='teiHeader': return None
        elif e.tag in ('text','front','main','back'):
            return _E('__FLATTEN__',subs=_recurse(e))
        elif e.tag=='em':
            assert len(e)==0
            return _E('em',e.text)
        elif e.tag=='span':
            assert len(e)==0
            if e.text is None: return None
            if (fam:=e.attrib.get('rend',None)) is None: return _E('span',e.text)
            elif fam=='italic': return _E('em',e.text)
            elif fam=='bold': return _E('strong',e.text)
            elif fam=='smallcaps': return _E('span',e.text,style='font-variant: small-caps;')
            elif fam=='bold-italic': return _E('strong',e.text)
            else: raise RuntimeError(f'Unrecognized family {fam}')
        elif e.tag=='p':
            if not self.editorial_titles and e.get('type',None)=='editorial_title': return None
            elem='p'
            if anchor:=e.get('id',None):
                kw=dict(id=anchor,class_='vism-para')
                pre=[_E('strong','§'+e.attrib['n']+'. ')]
            else: kw,pre={},[]
            # workardoun for paragraphs inside footnotes:
            # https://github.com/zopyx/print-css-rocks/pull/28#issuecomment-1603734259
            if self.inFootnote:
                elem='span'
                kw|={'class_':'p'}
            return _E(elem,subs=pre+_recurse(e),**kw)
        elif e.tag=='note':
            if e.get('place',None)=='foot':
                with InFootnote(self):
                    if (ch:=_curr_chapter(e)) is None:
                        assert 'reference_existing_footnote' not in e.attrib
                        return _E('span',subs=_recurse(e),class_='footnote')
                    else:
                        label=f'{ch}.n{e.attrib["n"]}'
                        if 'reference_existing_footnote' in e.attrib:
                            return _E('span',f'FIXME: see the other footnote {label}.',class_='footnote')
                        return _E('span',subs=_recurse(e),id=label,class_='footnote')
            elif e.get('type',None)=='TODO':
                 return _E('strong','[TODO: '+e.text+']',class_='vism-todo')
            else: raise RuntimeError(f'Unhandled note at {e.sourceline}')
        elif e.tag=='lg':
            for ich,ch in enumerate(e):
                if not ch.tag=='l':
                    raise RuntimeError(f'<lg> may contain only <l> elements (<lg> at line {e.sourceline}; child #{ich} <{ch.tag}>, line {ch.sourceline})')
            return _E('div',subs=_recurse(e),class_='vism-verse')
            # return _E('poetry',subs=[_E('linegroup',subs=_recurse(e))])
        elif e.tag=='l': return _E('div',subs=_recurse(e))
        elif e.tag=='div':
            level,tail=int((m:=re.match('(?P<tail>(?P<level>[0-9]+)-.*)',e.attrib['type'])).group('level')),m.group('tail')
            heading=e[0]
            assert heading.tag.startswith('head')
            toc_num=heading.attrib.get('n',None)
            title=[_E('h1',subs=_recurse(heading))]
            if level==1: # part
                global _html5_frontmatter
                _html5_frontmatter=((name:=e.attrib['name'])=='(Front)')
                if _html5_frontmatter: return _E('__FLATTEN__',subs=_recurse(e))
                kw=({'xml_id':'part-'+toc_num} if toc_num else {})
                return _E('section',subs=title+_recurse(e),class_='sect-dp1',**kw)
            elif level==2:
                if _html5_frontmatter: return _E('section',subs=title+_recurse(e),class_='sect-dp2')
                if sub:=heading.get('subtitle_pali',None): title+=[_E('div',role='doc-subtitle',subs=[_E('span',subs=[_E('emphasis',text=sub)])])]
                return _E('section',subs=title+_recurse(e),xml_id=toc_num,class_='sect-dp2')
            else: return _E('section',subs=title+_recurse(e),class_=f'sect-dp{level}')
        elif e.tag.startswith('head'): return None
        elif e.tag=='pb':
            if e.attrib['ed'] in ('BPS2011','BPS1995'): return _E('span',f'[{e.attrib["pdf_page"]}|{e.attrib["n"]}]',class_='vism-page-bps')
            elif e.attrib['ed']=='PTS': return _E('span',f'({e.attrib["n"]})',class_='vism-page-pts')
        elif e.tag=='ptr':
            target=e.attrib['target']
            if e.attrib['type'] in ('vism','vimm','internal'): return _E('a',e.text.replace("[PAGE]",""),href='#'+target)
            elif e.attrib['type']=='bib':
                ret=_E('span',class_='vism-bibref',subs=[_E('a',text=target,href='#bib:'+target)])
                if loc:=e.get('loc',None):
                    if href:=e.get('href',None): ret.append(_E('a',text=' '+loc,href=href))
                    else: ret.append(_E('span',' '+loc))
                return ret
            assert False
        elif e.tag=='anchor':
            return _E('a',id=e.get('id'))
        elif e.tag in ('index','glossary'):
            return _E('section',class_='sect-dp2',subs=[_E('h1',e.attrib['title']),_E('h2',e.attrib['subtitle']),_E('dl',class_='cols-2',subs=_recurse(e))])
        elif e.tag=='introductory': return _E('p',subs=_recurse(e))
        elif e.tag=='entry':
            return _E('__FLATTEN__',subs=[_E('dt',text=e.attrib['title']),_E('dd',subs=_recurse(e))])
        elif e.tag=='table':
            tab=_E('table',subs=[_E('thead'),_E('tbody')])
            for irow,tr in enumerate(e):
                assert tr.tag=='row' and set([td.tag for td in tr])=={'cell'}
                row=_E('tr',subs=[_E('td',subs=_recurse(td),valign='top') for td in tr])
                tab[min(irow,1)].append(row)
            return tab
        elif e.tag=='list':
            assert e.attrib['type']=='numbered'
            enum=_E('ol',
                style='list-style-type: '+{'1.':'decimal','I.':'upper-roman','i.':'lower-roman','(i)':'lower-roman','(a)':'lower-alpha'}[e.get('subtype','1')]
            )
            if 'start' in e.attrib: enum.attrib['start']=e.attrib['start']
            for li in e:
                enum.append(_E('li',subs=_recurse(li)))
            return enum
        elif e.tag=='bibliography':
            bib0=_E('__FLATTEN__',subs=[bib:=_E('dl',class_='bibliography')])
            for bi in e:
                if bi.tag=='bibentry':
                    bib.append(_E('dt',text=bi.attrib["abbrev"],id=f'bib:{bi.attrib["abbrev"]}'))
                    bib.append(_E('dd',subs=_recurse(bi)))
                elif bi.tag=='bibintertitle':
                    bib0.append(_E('section',subs=[_E('h1',bi.text),bib:=_E('dl',class_='bibliography')]))
                else: assert False
            return bib0
        elif e.tag=='raw':
            return etree.parse('html5/'+e.attrib['file']+'.xml',etree.XMLParser(remove_blank_text=True)).getroot()
        elif e.tag=='IGNORE': return None
        raise RuntimeError(f'Unhandled tag <{e.tag}> (line {e.sourceline})')





