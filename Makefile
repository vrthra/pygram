trace.g: trace.p
	./infer.py

trace.p:
	./extract.py

clean:
	rm trace.p
