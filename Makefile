deps:
	pip install -r requirements.txt

reqs:
	pip freeze > requirements.txt

coverage:
	python coverage_test.py
