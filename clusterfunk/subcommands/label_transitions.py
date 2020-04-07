import os
from clusterfunk.label_transitions import *
from clusterfunk.utils import check_str_for_bool, prepare_tree


def run(options):
    tree = prepare_tree(options)
    annotator = TransitionAnnotator(options.trait, options.include_parent, options.transition_name)

    if options.exploded_trees:
        trees = annotator.split_at_transitions(tree, check_str_for_bool(options.parent_state),
                                               check_str_for_bool(options.child_state))
        print(len(trees))
        if not os.path.exists(options.output):
            os.makedirs(options.output)
        i = 1
        for tree in trees:
            tree["tree"].write(path=options.output + "/" + tree["id"] + '.tree', schema="nexus")
            i += 1

    else:
        count = annotator.annotate_transitions(tree, check_str_for_bool(options.parent_state),
                                               check_str_for_bool(options.child_state))
        print(count)
        tree.write(path=options.output, schema="nexus")
