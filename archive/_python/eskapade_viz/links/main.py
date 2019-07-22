ds = unpickle_datastore()

read_key='data' # template from link?

doc = curdoc()

DfSummaryBokeh(read_key=read_key)._doc_factory(doc)

