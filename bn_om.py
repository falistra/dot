import functools,operator,itertools
from orderedSet import OrderedSet
import parser
import efprob_dc as efp

# Bayesian NETWORK OBJECT MODEL

class Node():
    nodesList = {}

    def __new__(cls,name):
        if name in Node.nodesList:
            return Node.nodesList[name]
        else:
            obj = Node.nodesList[name] = super(Node, cls).__new__(cls)
            return obj

    def __init__(self,name,*args):
        self.name = name
        self.parents = [] # set()
        self.children = [] # set()
        self.indegree = 0
        self.visited = False
        self.adjs = []

    def __repr__(self):
        # return "Node({}-{})".format(self.name,id(self))
        return "Node({})".format(self.name)

    def addToNet(self,net):
        net.nodes.add(self)
        if type(self) is InitialNode:   net.initialNodes.add(self)

    def setChannel(self,cpt):
        codomainElements = OrderedSet([names[-1] for (names,_) in cpt])
        NumCodElems = len(codomainElements)
        codomain = efp.Dom([self.name+"_"+elem for elem in codomainElements],names = efp.Name(self.name))
        doms = []
        steps = 1
        for (i,pn) in enumerate(self.parents):
            domainElements = OrderedSet([names[i] for (names,_) in cpt])
            doms.append(efp.Dom([pn.name+"_"+elem for elem in domainElements],names = efp.Name(pn.name)))
            steps *= len(domainElements)
        dom = functools.reduce(lambda d1, d2: d1 + d2, doms)
        pvalues = [row for (_,row) in cpt]
        matrix = [pvalues[n:n+NumCodElems] for n in range(0,len(pvalues),NumCodElems)]
        states = [efp.State(matrix[j], codomain) for j in range(steps)]
        self.channel = efp.chan_from_states(states, dom)
        self.node_size = len(self.channel.cod[0])


class InitialNode(Node):
    def __new__(cls,name,**kwargs):
        return super(InitialNode, cls).__new__(cls,name)

    def __init__(self,name,**kwargs):
        super(InitialNode, self).__init__(name)
        if "distribution" in kwargs:
            distribution = kwargs["distribution"]
            self.setChannel(distribution)

    def setChannel(self,distribution):
        cases = []
        pvalues = []
        for (names,pvalue) in distribution:
            cases.append(self.name+"_"+names[0])
            pvalues.append(pvalue)
        domain = efp.Dom(cases,names = efp.Name(self.name))
        self.channel = efp.State(pvalues,domain).as_chan()
        self.node_size = len(self.channel.cod[0])

    def __repr__(self):
        # return "InitialNode({}-{})".format(self.name,id(self))
        return "InitialNode({})".format(self.name)


class Edge():
    def __init__(self,From,to,cpt):
        self.From = From # list of nodes
        self.to = to # single node
        self.cpt = cpt

    def __repr__(self):
        return "Edge({}--{}-->{})".format(self.From,self.cpt,self.to)

    def addToNet(self,net):
        for node_from in self.From:
            if node_from not in net.nodes:
                node_from.addToNet(net)
            if self.to not in net.nodes:
                self.to.addToNet(net)
            node_from.children.append(self.to)
            self.to.parents.append(node_from)
        self.to.setChannel(self.cpt)
        net.edges.add(self)

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
        self.nodes = set()
        self.edges = set()
        self.initialNodes = set()
        self.bestValue = float("inf") # max value in Python
        self.bestPath = None
        self.numberOfPath = 0

    def __add__(self,element):
        element.addToNet(self)
        return self

    def __repr__(self):
        return \
            "Nodes\n" + \
            "\n".join([repr(node) for node in self.nodes]) + \
            "\n\nEdges\n" + \
            "\n".join([repr(edge) for edge in self.edges]) \
            + "\n\nParents\n" + \
            "\n".join(["{} : {}".format(repr(node),repr(node.parents)) for node in self.nodes])  \
            + "\n\nChildren\n" + \
            "\n".join(["{} : {}".format(repr(node),repr(node.children)) for node in self.nodes])


    def allTopologicalSortRecursive(self,currentPath):
        if self.stopRecursion:
            return
        flag = False
        for node in self.nodesSorted:
            # if type(i) is InitialNode:  continue

            #  If indegree is 0 and not yet visited then
            #  only choose that vertex
            if (node.indegree == 0 and not node.visited):

                for node_adj in node.adjs:
                    node_adj.indegree -= 1
                currentPath.append(node)
                node.visited = True

                self.allTopologicalSortRecursive(currentPath)

                node.visited = False
                currentPath.pop()
                for node_adj in node.adjs:
                    node_adj.indegree += 1
                flag = True

        if (not flag):
            self.numberOfPath += 1
            if (self.numberOfPath > 1000000):
                self.stopRecursion = True
            currentMaxWidth =  self.functionToMinimize(currentPath)
            if currentMaxWidth < self.bestValue:
                print("====== ",self.numberOfPath," ======")
                print(currentPath,currentMaxWidth)
                self.bestValue = currentMaxWidth
                self.bestPath = currentPath.copy()


    def findBestPath(self):

        def functionToMinimize(path):
            availableNodes = set(self.initialNodes)
            nodeCopies = self.nodeCopies.copy()
            maxWidth = 0
            for node in path:
                for parent in node.parents:
                    nodeCopies[parent] -= 1
                    if nodeCopies[parent] == 0:
                        availableNodes.remove(parent)
                availableNodes.add(node)
                currentWidth = functools.reduce(operator.mul, [node.node_size for node in availableNodes], 1)
                if maxWidth < currentWidth:
                    maxWidth = currentWidth
            return maxWidth

        for edge in self.edges:
            for node_from in edge.From:
                node_from.adjs.append(edge.to)
        for n in self.nodes:
            for m in n.adjs:
                m.indegree += 1

        self.nodesSorted = sorted(self.nodes,key = lambda n : -n.indegree) # -len(n.parents))
        self.nodeCopies = {node:len(node.children) for node in self.nodes}
        self.functionToMinimize = functionToMinimize
        self.stopRecursion = False

        self.allTopologicalSortRecursive(currentPath=[])
        return self.bestPath


    def categorize(self):
        bestPath = self.findBestPath()
        print(bestPath)
        # self.buildChannelList(bestPath)
        raise NotImplementedError("categorize To be implemented")

    def inference(self,observationNode,evidences):
        raise NotImplementedError("inference To be implemented")
