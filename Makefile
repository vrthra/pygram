debug=-m pudb
ENV=$(debug)

trace.g: trace.p
	python3 $(ENV) ./infer.py

trace.p:
	./extract.py

clean:
	rm trace.p
