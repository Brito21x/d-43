# Makefile

install:
	pip install -r requirements.txt

run:
	shiny run src/app.py

clean:
	rm -rf src/__pycache__
