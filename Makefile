debug=-m pudb
ENV=$(debug)

traces.g: traces.p
	python3 $(ENV) ./infer.py

traces.p: extract.py
	./extract.py

show:
	@ ./showtrace.py

showjs:
	@ ./showtrace.py | jq .

clean:
	rm traces.p
