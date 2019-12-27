from gl.transform import Transform

class NodeObject:
    def __init__(self, name="emitter"):
        self.gl_node_manual_init(name)

    def gl_node_manual_init(self, name="emitter"):
        self.gl_node_root = None
        self.idle_callback = None
        self.gl_node_name = name

    def gl_node_init(self, name=None):
        self.gl_node_root = Transform(name=self.gl_node_name)
        pass

    def gl_node_add_child(self, child):
        self.gl_node_root.add_child(child)

    def gl_node(self):
        if self.gl_node_root is None:
            self.gl_node_init()
        return self.gl_node_root

    def gl_node_set_idle_callback(self, cb, min_delay=None):
        self.idle_callback = (cb, min_delay)
