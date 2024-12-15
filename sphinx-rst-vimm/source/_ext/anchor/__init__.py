from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective, SphinxRole
from sphinx.roles import XRefRole
from sphinx.util.typing import ExtensionMetadata
from sphinx.environment import BuildEnvironment
from docutils.nodes import Element, Node, system_message

class AnchorRole(XRefRole):
    def result_nodes(self, document: nodes.document, env: BuildEnvironment, node: Element,
                     is_ref: bool) -> tuple[list[Node], list[system_message]]:
        targetnode = nodes.target('', '', names=[self.text.lower()], ids=[self.text.lower()])
        document.note_explicit_target(targetnode)
        return [targetnode], []


def setup(app):
    app.add_role('anchor',AnchorRole())
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True
    }
