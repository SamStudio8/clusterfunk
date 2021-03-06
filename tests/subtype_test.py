import os
import unittest

import dendropy

from clusterfunk.utilities.subtyper import Subtyper
from clusterfunk.utilities.utils import collapse_nodes

this_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(this_dir, "tests", 'data', 'subtype')


class MyTestCase(unittest.TestCase):
    def test_sibling(self):
        tree = dendropy.Tree.get(path="%s/representative_sequences.aln.fasta.nexus.tree" % data_dir, schema="nexus",
                                 preserve_underscores=True)
        subtyper = Subtyper(tree, 2, "|")

        self.assertEqual(subtyper.get_subtype("Iceland/222/2020|EPI_ISL_417837|B.1.8|Iceland|||2020-03-16"), "B.1.8")

    def test_nested_no_sibling(self):
        tree = dendropy.Tree.get(path="%s/representative_sequences.aln.fasta.nexus.tree" % data_dir, schema="nexus",
                                 preserve_underscores=True)
        subtyper = Subtyper(tree, 2, "|")

        self.assertEqual(subtyper.get_subtype("France/IDF2256/2020|EPI_ISL_416498|B.1.4|France|||2020-03-11"), "B.1.4")

    def test_between_clades_fall_back(self):
        tree = dendropy.Tree.get(path="%s/representative_sequences.aln.fasta.nexus.tree" % data_dir, schema="nexus",
                                 preserve_underscores=True)
        subtyper = Subtyper(tree, 2, "|")

        self.assertEqual(subtyper.get_subtype("USA/CZB-RR057-013/2020|EPI_ISL_417937|B.1.3|USA|||2020-03-18"), "B.1")

    def test_doesnt_find_tip(self):
        tree = dendropy.Tree.get(path="%s/EPI_ISL_667.aln.fasta.tree" % data_dir, schema="newick",
                                 preserve_underscores=True)
        subtyper = Subtyper(tree, 2, "|")

        self.assertEqual(subtyper.get_subtype("Testland___TLD32___2020|EPI_ISL_667||Testland|||2020-03-11"), "B")

    def test_empty_subtype(self):
        tree = dendropy.Tree.get(path="%s/EPI_ISL_413581X.aln.fasta.nexus.tree" % data_dir, schema="nexus",
                                 preserve_underscores=True)

        collapse_nodes(tree, lambda x: x.edge.length == 0)
        subtyper = Subtyper(tree, 2, "|")

        self.assertEqual(subtyper.get_subtype("Netherlands___Oss_1363500___2020|EPI_ISL_413581X|2020-02-29"), "B")

    def test_polytomy_no_tip_Siblings(self):
        tree = dendropy.Tree.get(path="%s/EPI_ISL_416626.aln.fasta.nexus.tree" % data_dir, schema="nexus",
                                 preserve_underscores=True)
        collapse_nodes(tree, lambda x: x.edge.length == 0)
        subtyper = Subtyper(tree, 2, "|")
        self.assertEqual(subtyper.get_subtype("EPI_ISL_416626||"), "B")

    def test_for_good_measure(self):
        tree = dendropy.Tree.get(path="%s/EPI_ISL_418192.aln.fasta.nexus.tree" % data_dir, schema="nexus",
                                 preserve_underscores=True)
        collapse_nodes(tree, lambda x: x.edge.length == 0)
        subtyper = Subtyper(tree, 2, "|")
        self.assertEqual(subtyper.get_subtype("EPI_ISL_418192||"), "B.1")


if __name__ == '__main__':
    unittest.main()
