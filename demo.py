from bn_om import BayesianNet
from bn_om import Predicate

#example = open("asia.dot").read()
example = open("child.dot").read()

bn = BayesianNet.define(example)
# print(bn)

def run():
    try:
        bn.categorize()
        pass
    except NotImplementedError as e:
        print(e)

    try:
        asiaPositive = Predicate("asia",[("t",1.0),("f",0.0)])
        xrayNegative = Predicate("xray",[("t",0.0),("f",1.0)])
        evidences = [asiaPositive,xrayNegative]
        bn.inference(observationNode="dysp",evidences=evidences)
    except NotImplementedError as e:
        print(e)

if __name__ == '__main__':
    import timeit
    print(timeit.timeit(stmt = run,number = 1))
