
class Tree(object):
    def __init__(self, init_pos, evaluator):
        self.root = Node(move=None, value=evaluator.eval0(init_pos), parent=None, init_pos=init_pos)
        self.evaluator = evaluator
        self.evaluated = dict()
        self.evaluated[init_pos] = self.root
        self.frontier = [self.root]

    def best_variant(self):
        variant = []
        best_move = self.root.best
        while best_move:
            variant.append(best_move[1])
            best_move = best_move[0].best
        return variant, self.root.value

    def analyse_step(self, steps=10):
        #print ''
        #print ''
        #print ''
        #print 'TREE', self
        #print 'FRONTIER', self.frontier
        self.frontier.sort(key=Node.explore_rank, reverse=True)
        i = 0
        while i < steps and self.frontier:
            node = self.frontier.pop()
            new_nodes = node.explore_children(self.evaluator, self.evaluated)
            self.frontier.extend(new_nodes)
            i += 1

    def __repr__(self):
        result = repr(self.root.position)
        result += self.root.pretty_print_children(1)
        return result




class Node(object):
    id_gen = 0

    def __init__(self, move, value, parent, init_pos=None):
        self.id = Node.id_gen
        Node.id_gen += 1
        if not move:
            self.position = init_pos
            self.is_root = True
        else:
            self.position = move.to_position
            self.is_root = False
        assert value is not None
        if value is None:
            raise Exception('None value')
        self.value = value
        if parent:
            self.min_depth = parent.min_depth + 1
            notation = move.notation()
            self.parents = [(parent, notation)]
            self.best_parent = (parent, notation)
        else:
            self.min_depth = 0
            self.parents = []
            self.best_parent = None
        self.children = []
        self.best = None

    def __repr__(self):
        return 'Node(' + repr(self.id) + '): ' + repr(self.position) + '. VALUE: ' + repr(self.value) + (
                ('. BEST: ' + self.best[1]) if self.best else '')

    def pretty_print_children(self, indent, already_printed=None):
        if already_printed is None:
            already_printed = set()
        from os import linesep
        indent_space = linesep + '    ' * indent
        result = ''
        for n, notation in self.children:
            result += indent_space + str(notation) + ', ' + str(n.value) + ' (' + str(n.id) + ')'
            if n in already_printed:
                result += '*'
            else:
                already_printed.add(n)
                result += n.pretty_print_children(indent + 1, already_printed)
        return result

    def is_better(self, new, current):
        if current is None:
            return True
        if self.position.white_moves:
            return new > current
        return new < current

    def expand_min_depth(self, min_depth):
        if min_depth < self.min_depth:
            self.min_depth = min_depth
            for n, _ in self.children:
                n.expand_min_depth(min_depth + 1)

    def explore_children(self, evaluator, evaluated):
        #print 'EXPLORING', self
        children = list()
        new_nodes = list()

        best = None
        best_value = None
        existent_children = []
        has_moves = False
        for m in self.position.all_moves():
            has_moves = True
            notation = m.notation()
            try:
                node = evaluated[m.to_position]
                node.parents.append((self, notation))
                existent_children.append((node, notation))
                m_val = node.value
                node.expand_min_depth(self.min_depth + 1)
            except KeyError:
                m_val = evaluator.eval(self.position, self.value, m)
                node = Node(m, m_val, self)
                if not m.is_mate() and not m.is_stalemate():
                    new_nodes.append(node)
                evaluated[m.to_position] = node
                #if m.is_mate():
                    #print 'mate found ', node
            assert m_val is not None
            if self.is_better(m_val, best_value):
                best = node, notation
                best_value = m_val
            if m.is_mate():
                try:
                    assert abs(best[0].value) > 999, 'No mate!'
                except AssertionError, e:
                    print self
                    print m
                    print best
                    best[0].pretty_print_children(1)
                    for n in self.position.all_moves():
                        print n
                    raise e
                #print best[0].position.is_mate(), best[1]
            children.append((node, notation))
        try:
            assert has_moves, 'No move!'
        except AssertionError, e:
            print self
            raise e

        self.children = children
        #print 'NEW CHILDREN', children
        self.best = best
        #if self.best and self.best[0].position.is_mate():
            #print 'UPDATING MATE', self.value

        assert best_value is not None
        self.value = best_value
        for parent, notation in self.parents:
            parent.update_value((self, notation))
            #print parent.value
        #for (ch, notation) in existent_children:
            #if not ch.best_parent or self.is_better(best_value, ch.best_parent[0].value):
                #ch.best_parent = (self, notation)
                
        return new_nodes

    def explore_rank(self):
        node = self
        best_path = [node]
        while not node.is_root:
            candidate_diff = None
            node_value = node.value
            candidate_depth = node.min_depth - 1
            for (p, p_not) in node.parents:
                if candidate_depth == p.min_depth:
                    parent_diff = abs(node_value - p.value)
                    if candidate_diff is None or candidate_diff < parent_diff:
                        candidate = p
                        candidate_diff = parent_diff
            node = candidate
            assert not node in best_path
            best_path.append(node)
        node = best_path.pop()
        pre_value = node.value
        rank = 0
        depth = 0
        while best_path:
            node = best_path.pop()
            node_value = node.value
            depth += 1
            try:
                rank += abs(node_value - pre_value) + depth * 0.5
            except Exception, e:
                print node_value, pre_value
                print node
                raise e
        return rank

    def update_value(self, node_notation):
        node, notation = node_notation
        if self.best == node_notation:
            best_value = node.value
            best = node, notation
            for n, n_notation in self.children:
                if self.is_better(n.value, best_value):
                    best = n, n_notation
                    best_value = n.value
            self.best = best
            self.value = best_value
            changed = True
        else:
            if self.is_better(node.value, self.value):
                self.value = node.value
                self.best = node, notation
                changed = True
            else:
                changed = False
        if changed:
            for parent, notation in self.parents:
                parent.update_value((self, notation))
        
    def get_value(self):
        return self.value

from .chess_play import Engine

class TreeEngine(Engine):

    def __init__(self, evaluator, steps=5, max_cycles=200):
        self.evaluator = evaluator
        self.steps = steps
        self.max_cycles = max_cycles

    def set_game(self, game):
        self.game = game

    def start(self, pipe):
        pos = self.game._current_position()
        tree = Tree(pos, self.evaluator)
        tree.analyse_step(self.steps)
        for i in xrange(self.max_cycles):
            if pipe.poll() or abs(tree.root.value) > 999:
                break
            tree.analyse_step(self.steps)
        pipe.send(tree.best_variant())

    def move(self):
        pos = self.game._current_position()
        tree = Tree(pos, self.evaluator)
        tree.analyse_step(self.steps)
        for i in xrange(self.max_cycles):
            if abs(tree.root.value) > 999:
                break
            tree.analyse_step(self.steps)
        best_variant = tree.best_variant()
        move =  best_variant[0][0]

        return move