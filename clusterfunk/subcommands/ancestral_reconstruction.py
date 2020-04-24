from clusterfunk.annotate_tree import TreeAnnotator
from clusterfunk.utils import check_str_for_bool, prepare_tree


def run(options):
    tree = prepare_tree(options, options.input)

    annotator = TreeAnnotator(tree)

    acctran = True if options.acctran else False

    if len(options.traits) > 0:
        i = 0
        for trait in options.traits:
            ancestral_state = check_str_for_bool(options.ancestral_state[i]) if len(
                    options.ancestral_state) > i else None

            annotator.annotate_nodes_from_tips(trait, acctran, ancestral_state)
            i += 1

    tree.write(path=options.output, schema="nexus")