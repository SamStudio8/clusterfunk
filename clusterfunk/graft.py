class RootStock:
    def __init__(self, tree):
        self.tree = tree
        self.incoming_tree = None
        self.added_taxa = []

    def graft(self, incoming_tree):
        self.tree.taxon_namespace.add_taxa(incoming_tree.taxon_namespace)
        self.added_taxa.extend([taxon for taxon in incoming_tree.taxon_namespace])
        tips = [tip.taxon for tip in self.tree.leaf_node_iter()]

        incoming_tree_tips = [tip.taxon for tip in incoming_tree.leaf_node_iter()]
        incoming_tree_tips_labels = [tip.label for tip in incoming_tree_tips]

        shared_taxa = [tip for tip in tips if tip.label in incoming_tree_tips_labels]
        expectant_parent = self.tree.mrca(taxa=shared_taxa)
        added_node = expectant_parent.add_child(incoming_tree.seed_node)
        added_node.edge.collapse(adjust_collapsed_head_children_edge_lengths=True)

        self.tree.prune_taxa(shared_taxa)
        self.tree.purge_taxon_namespace()

    def remove_left_over_tips(self):
        self.tree.prune_taxa([taxon for taxon in self.tree.taxon_namespace if taxon not in self.added_taxa])
        self.tree.purge_taxon_namespace()
