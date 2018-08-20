import parser

# Bayesian NETWORK OBJECT MODEL

class Node():
    nodesList = {}

    def __new__(cls,name):
        if name in Node.nodesList:
            return Node.nodesList[name]
        else:
            obj = Node.nodesList[name] = super(Node, cls).__new__(cls)
            return obj

    def __init__(self,name):
        self.name = name

    def __repr__(self):
        return "Node({}-{})".format(self.name,id(self))
        # return "Node({})".format(self.name)

    def addToNet(self,net):
        net.nodes.append(self)


class InitialNode(Node):
    def __new__(cls,name):
        return super(InitialNode, cls).__new__(cls,name)

    def __init__(self,name):
        super(InitialNode, self).__init__(name)

    def __repr__(self):
        return "InitialNode({}-{})".format(self.name,id(self))
        # return "InitialNode({})".format(self.name)

class Edge():
    def __init__(self,From,to,cpt):
        self.From = From
        self.to = to
        self.cpt = cpt

    def __repr__(self):
        return "Edge({}--{}-->{})".format(self.From,self.cpt,self.to)

    def addToNet(self,net):
        net.edges.append(self)

class valuesList():
    def __init__(self):
        self.values = []

    def __add__(self,value):
        self.values.append(value)
        return self

    def __hash__(self):
        return hash(str(self.values))

    def __eq__(self,other):
        return str(self.values) == str(other.values)

    def __repr__(self):
        return (",").join(self.values)

class Predicate():

    def __init__(self,name,distribution):
        self.name = name
        self.distribution = distribution

    def __repr__(self):
        return "Predicate({}-{})".format(self.name,id(self))


class BayesianNet():

    @staticmethod
    def define(dotCode):
        return parser.parse(dotCode)

    def __init__(self):
        self.nodes = []
        self.edges = []

    def __add__(self,element):
        element.addToNet(self)
        return self

    def __repr__(self):
        return \
            "Nodes\n" + \
            "\n".join([repr(node) for node in self.nodes]) + \
            "\nEdges\n" + \
            "\n".join([repr(edge) for edge in self.edges])

    def categorize(self):
        raise NotImplementedError("categorize To be implemented")

    def inference(self,observationNode,evidences):
        raise NotImplementedError("inference To be implemented")
