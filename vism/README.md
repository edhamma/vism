XML tags
=========

The markup follows (mostly) TEI (Text Encoding Initiative), wich some exceptions which will be noted below. We don't currently use XML namespaces, so the document will not validate against TEI at the moment (it might be added in the future).

* `span`: optionanly defines `rend` (`normal`, `italic`, `bold`, `smallcaps`, `bold-italic`); this and `<em>` are the only leaf elements (containing text)
* `em`: shorthand for `<span family="italic">`
* `p`: paragraph, most paragraphs define `page_id` (1-based) and `page_no` (human-readable) for pages in the BPS edition
   
   * if `p` defines `n` and `id`, it is Visuddhimagga paragraph number, being marked as such (e.g. §69). Anchor has the format XV.15 (chapter in roman, dot, decimal paragraph)

* `footnote`: footnote (defines `page_id` and `n`); footnotes contain paragraphs

   * might define (one instance) `reference_existing_footnote`, in which case it refers to the immediately preceding footnote (LaTeX actually checks that the footnote mark matches)
   
* structure: `div` of type `1-part`, `2-chapter`, `3-section`, `4-subsection` etc: nested elements for the book structure
* headings: `head` (these are just the headings, and should come at the beginning of the respective structure part)
* `lg` & `l` (line group and lines): block for verse, contains `l` elements; stanzas are expressed as contiguous `<lg>` blocks 
* `pb`: page beginning, either with `ed` BPS2011, BPS1995, PTS, `pdf_page` attribute (for `BPS*` editions; absolute page number in the PDF source) and `n` (page number shown on the page).
* `entry`: entry in index or glossary; has the `title` attribute, and its children is the contents;
* `ptr`: hyperlink to something, depending on `type` attribute:

   * `vism` is internal link to Visuddhimagga chapter or paragraph, `target` being the standard label (`XII` for chapter, `XII.23` for chapter and paragraph)
   * `bib` is bibliography link (citation), `target` attribute being the bibliography key (such as `M`) and `loc` the rest of the citation (e.g. ` I 54`), for `M I 54`

* `TEI`: top-level tag for the main text
* `enum`: top-level tag for index or glossary (`type` is `numbered`, `subtype` is e.g. `1.` for numbering style)

