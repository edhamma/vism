XML tags
=========

* `span`: optionanly defines `size` (in px) and `family` (`normal`, `italic`, `bold`, `smallcaps`, `bold-italic`); this is the only element which contains text
* `em`: shorthand for `<span family="italic">`
* `p`: paragraph, most paragraphs define `page_id` (1-based) and `page_no` (human-readable) for pages in the BPS edition
   
   * if `p` defines `num` and `anchor`, it is Visuddhimagga paragraph number, being marked as such (e.g. §69). Anchor has the format XV.15 (chapter in roman, dot, decimal paragraph)

* `footnote`: footnote (defines `page_id` and `mark`); footnotes contain paragraphs

   * might define (one instance) `reference_existing_footnote`, in which case it refers to the immediately preceding footnote (LaTeX actually checks that the footnote mark matches)
   
* structure: `struct-1-part`, `struct-2-chapter`, `struct-3-section`, `struct-4-subsection`: nested elements for the book structure
* headings: `heading-1-part`, `heading-2-chapter`, `heading-3-section`, `heading-4-subsection` (these are just the headings, and should come at the beginning of the respective structure part)
* `verse` & `line`: block for verse, contains `line` elements (stanzas not yet done)
* `printed_page`: denotes pagebreak in either the BPS2011 edition, or in the old Pali Text Society edition (attribute `edition`, which is `BPS2011` or `PTS`)
* `entry`: entry in index or glossary; has the `title` attribute, and its children is the contents;
* `ref`: hyperlink to something, depending on `type` attribute:

   * `vism` is internal link to Visuddhimagga chapter or paragraph, `target` being the standard label (`XII` for chapter, `XII.23` for chapter and paragraph)
   * `bib` is bibliography link (citation), `target` attribute being the bibliography key (such as `M`) and `loc` the rest of the citation (e.g. ` I 54`), for `M I 54`

* `book`: top-level tag for the main text
* `list`: top-level tag for index or glossary

