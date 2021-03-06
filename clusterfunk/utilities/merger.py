from clusterfunk.utilities.utils import NodeTraitMap, SafeNodeAnnotator

nodeAnnotator = SafeNodeAnnotator()


class Merger:
    def __init__(self, trait_to_merge, trait_name, prefix="", max_merge=1, merge_identical_samples=False,
                 merge_siblings=False):
        self.trait_to_merge = trait_to_merge
        self.trait_name = trait_name
        self.max_merge = max_merge
        self.merge_counts = None
        self.count = 1
        self.prefix = prefix
        self.only_merge_sibling_singletons = merge_identical_samples
        self.merge_siblings = merge_siblings

    def merge(self, tree):
        self.count = 1

        if self.only_merge_sibling_singletons:
            self.merge_sibling_singletons(tree.seed_node)
        elif self.merge_siblings:
            self.merge_siblings_routine(tree.seed_node)
        else:

            self.merge_counts = NodeTraitMap()
            for node in tree.postorder_node_iter():
                self.merge_counts.set([node, 0])

            values = list(set([tip.annotations.get_value(self.trait_to_merge) for tip in tree.leaf_node_iter() if
                               tip.annotations.get_value(self.trait_to_merge) is not None]))

            mrcas = []
            for value in values:
                taxa = [n.taxon for n in
                        tree.leaf_node_iter(lambda n: n.annotations.get_value(self.trait_to_merge) == value)]
                mrca = tree.mrca(taxa=taxa)
                mrcas.append(mrca)
            level_order_mrcas = [node for node in tree.levelorder_node_iter() if node in mrcas]

            while len(level_order_mrcas) > 0:
                current_node = level_order_mrcas.pop()
                parent = current_node.parent_node
                siblings = [node for node in level_order_mrcas if node.parent_node == parent]

                # combine
                if self.merge_counts.get(parent) < self.max_merge and len(siblings) > 0:
                    level_order_mrcas = [node for node in level_order_mrcas if node not in siblings]
                    self.increment_to_root(parent)
                    self.name_merger(parent)
                # name them
                else:
                    self.name_merger(current_node)
                self.count += 1

    def merge_sibling_singletons(self, internal_node):
        annotation_value = internal_node.annotations.get_value(self.trait_to_merge)
        if annotation_value is not None:
            nodeAnnotator.annotate(internal_node, self.trait_name, annotation_value)

        if internal_node.num_child_nodes() > 2:
            values = []
            for leaf in internal_node.child_node_iter(
                    lambda node: node.is_leaf() and node.annotations.get_value(self.trait_to_merge) is not None):
                annotation_value = leaf.annotations.get_value(self.trait_to_merge)
                values.append(annotation_value)
                nodeAnnotator.annotate(leaf, self.trait_name, values[0])
        else:
            for leaf in internal_node.child_node_iter(
                    lambda node: node.is_leaf() and node.annotations.get_value(self.trait_to_merge) is not None):
                annotation_value = leaf.annotations.get_value(self.trait_to_merge)
                nodeAnnotator.annotate(leaf, self.trait_name, annotation_value)

        for child in internal_node.child_node_iter(lambda node: not node.is_leaf()):
            self.merge_sibling_singletons(child)

    def merge_siblings_routine(self, internal_node):

        annotation_value = internal_node.annotations.get_value(self.trait_name)
        # not getting to C in the test. need to get to all the tips!
        if annotation_value is not None:
            # nodeAnnotator.annotate(internal_node, self.trait_name, annotation_value)
            for annotatated_child in internal_node.child_node_iter(
                    lambda n: n.annotations.get_value(self.trait_to_merge) is not None):
                nodeAnnotator.annotate(annotatated_child, self.trait_name, annotation_value)
        elif internal_node.num_child_nodes() > 2:
            value = None
            for imported_child in internal_node.child_node_iter(lambda child:
                                                                child.annotations.get_value(
                                                                        self.trait_to_merge) is not None):
                annotation_value = imported_child.annotations.get_value(self.trait_to_merge)
                if value is None:
                    value = annotation_value
                nodeAnnotator.annotate(imported_child, self.trait_name, value)
        else:
            for only_annotated_child in internal_node.child_node_iter(
                    lambda n: n.annotations.get_value(self.trait_to_merge) is not None):
                child_annotation = only_annotated_child.annotations.get_value(self.trait_to_merge)
                nodeAnnotator.annotate(only_annotated_child, self.trait_name, child_annotation)

        for child in internal_node.child_node_iter(lambda n: not n.is_leaf()):
            self.merge_siblings_routine(child)

    def name_merger(self, node, annotation=None, leafs_only=False):
        if annotation is None:
            annotation = self.prefix + str(self.count)
        if leafs_only:
            if node.is_leaf():
                nodeAnnotator.annotate(node, self.trait_name, annotation)
        else:
            nodeAnnotator.annotate(node, self.trait_name, annotation)

        for child in node.child_node_iter():
            if child.annotations.get_value(self.trait_to_merge) is not None:
                if leafs_only and child.is_leaf():
                    self.name_merger(child, annotation, leafs_only)
                else:
                    self.name_merger(child, annotation)

    def increment_to_root(self, node):
        new_count = self.merge_counts.get(node) + 1
        self.merge_counts.set([node, new_count])
        if node.parent_node is not None:
            self.increment_to_root(node.parent_node)
