from .chess_rules import KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN
DEFAULT_VALUES = {'mate': 10000, QUEEN: 9.5, ROOK: 5, BISHOP:3.5, 
        KNIGHT: 3, PAWN: 1, 'draw': 0}

class Tree(object):
    def __init__(self, init_pos, evaluator, history=None):
        self.root = Node(move=None, value=evaluator.eval0(init_pos), parent=None, init_pos=init_pos)
        if history is None:
            history = {}
        self.history = set(history)
        self.evaluator = evaluator
        self.evaluated = dict()
        self.evaluated[init_pos] = self.root
        self.frontier = [self.root]

    def candidates(self, max_number):
        result = self.root.children
        variant = {self.root}
        def _get_value(c):
            return c[0]._get_value(variant, self.history)[0]
        result.sort(key=_get_value, reverse=self.root.position.white_moves)
        return result[: max_number]

    def best_variant(self, candidate=None):
        if not candidate:
            prepend = True
            candidate, candidate_move = self.candidates(1)[0]
        else:
            prepend = False
        variant = {self.root}
        (best_value, best_var) = candidate._get_value(variant, self.history)
        if prepend:
            best_var = [candidate_move] + best_var if best_var else [candidate_move]
        return best_var, best_value

    def _best_node(self, candidate=None):
        if not candidate:
            candidate = self.root
        considered = set()
        best_node = candidate
        while best_node.best:
            best_node = best_node.best[0]
            if best_node in considered:
                return None
            considered.add(best_node)
        return best_node

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
        if abs(self.root.value) < 1000:
            candidates = self.candidates(3)
            for c in candidates:
                if abs(c[0].value) < 1000:
                    node = self._best_node(c[0])
                    if node:
                        new_nodes = node.explore_children(self.evaluator, self.evaluated)
                        self.frontier.extend(new_nodes)

    def __repr__(self):
        result = repr(self.root.position)
        result += self.root.pretty_print_children(1)
        return result




class Node(object):
    id_gen = 0

    def __init__(self, move, value, parent, init_pos=None):
        self.id = Node.id_gen
        Node.id_gen += 1
        self.extra = 0
        if not move:
            self.position = init_pos
            self.is_root = True
        else:
            self.position = move.to_position
            self.is_root = False
            if move.is_capture:
                self.extra = DEFAULT_VALUES[move.captured]
            if self.position.is_check():
                self.extra += 2

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
                rank += abs(node_value - pre_value) + depth * 0.3
            except Exception, e:
                print node_value, pre_value
                print node
                raise e
        rank -= 1.5 * self.extra
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
            if best_value != self.value:
                self.value = best_value
                changed = True
            else:
                changed = False
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
        
    def _get_value(self, variant, history):
        if self in variant or self.position in history:
            return (0, None)
        if not self.children:
            return (self.value, None)
        next_variant = set(variant)
        next_variant.add(self)
        child_values = map(lambda ch: (ch[0]._get_value(next_variant, history), ch[1]), 
                self.children)
        if self.position.white_moves:
            best_var = max(child_values, key=lambda x: x[0][0]) 
        else:
            best_var = min(child_values, key=lambda x: x[0][0]) 
        result = (best_var[0][0], 
            [best_var[1]] + best_var[0][1] if best_var[0][1] else [best_var[1]])
        return result



from .chess_play import Engine

class TreeEngine(Engine):

    def __init__(self, evaluator, steps=3, max_cycles=180, min_cycles=100, min_best_depth=8):
        self.evaluator = evaluator
        self.steps = steps
        self.max_cycles = max_cycles
        self.min_cycles = min_cycles
        self.min_best_depth = min_best_depth

    def set_game(self, game):
        self.game = game

    def start(self, pipe):
        pos = self.game._current_position()
        tree = Tree(pos, self.evaluator, self.game._history())
        tree.analyse_step(self.steps)
        i = 0
        while True:
            if pipe.poll() or abs(tree.root.value) > 999:
                break
            if i > self.max_cycles:
                break
            if i > self.min_cycles:
                best_node = tree._best_node()
                if best_node:
                    if best_node.extra:
                        if len(tree.best_variant()[0]) >= 2 * self.min_best_depth:
                            break
                    else:
                        if len(tree.best_variant()[0]) >= self.min_best_depth:
                            break
            tree.analyse_step(self.steps)
            i += 1
        candidates = tree.candidates(3)
        for c in candidates:
            print c[1], tree.best_variant(c[0])
            
        pipe.send(tree.best_variant())

    def move(self):
        pos = self.game._current_position()
        tree = Tree(pos, self.evaluator, self.game._history())
        tree.analyse_step(self.steps)
        for i in xrange(self.max_cycles):
            if abs(tree.root.value) > 999:
                break
            tree.analyse_step(self.steps)
        best_variant = tree.best_variant()
        move =  best_variant[0][0]

        return move
