# DocBook Syntax

Our DocBook document is perhaps in some ways non-conforming (lack of documentation and examples), though it produces mostly correct results with older XSLTs (but not with newer, such as xslTNG). These are the points:

* `<formalpara>` is a structuring element which should contain `<title>` and then `<p>` (or `<linegroup>` perhaps), instead of inline material itself (`<phrase` etc). `<formalpara>` should span over its containing paragraphs until the next `<formalpara>`, or the end of the section.
* `<citation>` and `<phrase>` (e.g. "[MN] I, 234") should be replaced by `<biblioref>` and friends, but there is lack of documentation on that: [StackOverflow question](https://stackoverflow.com/q/75499126)

# Output improvements

* [TOC control](http://www.sagehill.net/docbookxsl/TOCcontrol.html) documents (for docbook 4.x, though) how to control where TOCs are, and to what depth. Try that so that we have TOCs in chapters (not parts) in the XHTML output.
* Stylesheet for XHTML?
* EPub output: produces empty files, or broken EPubs which readers refuse to open (Sphinx's epub's are OK)
