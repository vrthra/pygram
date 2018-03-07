#!/usr/bin/env python3
import pickle
import jsonpickle
traces = pickle.load(open( "traces.p", "rb" ))
frozen = jsonpickle.encode(traces)
print(frozen)
