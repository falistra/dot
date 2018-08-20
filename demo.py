from bn_om import BayesianNet
from bn_om import Predicate

example = """
smoke [t=0.5]
asia  [t=0.5]
smoke -> lung [t=0.1; f=0.01]
asia -> tub[t=0.05; f=0.01]
lung,tub -> either[t,f=1; f,t=1; t,t=1; f,f=0]
smoke -> bronc[t=0.6; f=0.3]
bronc,either -> dysp[t,f=0.9; f,t= 0.9; t,t= 0.8; f,f=0.1]
either -> xray[t=0.98;f=0.05]
"""

bn = BayesianNet.define(example)
print(bn)

try:
    bn.categorize()
except NotImplementedError as e:
    print(e)

try:
    asiaPositive = Predicate("asia",[("t",1.0),("f",0.0)])
    xrayNegative = Predicate("xray",[("t",0.0),("f",1.0)])
    evidences = [asiaPositive,xrayNegative]
    bn.inference(observationNode="dysp",evidences=evidences)
except NotImplementedError as e:
    print(e)
