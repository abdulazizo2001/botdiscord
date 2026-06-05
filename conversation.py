# conversation.py
# Arbre de discussion: thèmes libres, ici un exemple simple.

from data_structures import TreeNode

def build_conversation_tree():
    # Racine
    root = TreeNode("root", prompt="Tu veux parler de programmation ou de sport ?")

    prog = TreeNode("prog", prompt="Python ou Java ?")
    sport = TreeNode("sport", prompt="Football ou Basket ?")

    root.add_option("programmation", prog)
    root.add_option("sport", sport)

    py = TreeNode("py", conclusion="Tu es team Python, excellent choix !")
    ja = TreeNode("ja", conclusion="Java, robuste et verbeux !")
    fb = TreeNode("fb", conclusion="Le football, esprit d'équipe !")
    bb = TreeNode("bb", conclusion="Le basket, rythme et précision !")

    prog.add_option("python", py)
    prog.add_option("java", ja)

    sport.add_option("football", fb)
    sport.add_option("basket", bb)

    # Index des nœuds pour accès rapide
    nodes = {
        n.id: n for n in [root, prog, sport, py, ja, fb, bb]
    }

    return root, nodes


def search_topic(root, topic):
    """Parcours DFS manuel du contenu des prompts et des clés d'options."""
    topic = topic.strip().lower()
    stack = [root]
    while stack:
        cur = stack.pop()
        if cur.prompt and topic in cur.prompt.lower():
            return True
        for key, child in cur.options.items():
            if topic in key.lower():
                return True
            stack.append(child)
    return False
