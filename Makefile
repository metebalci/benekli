
test:
	black --check benekli
	pylint benekli

upload:
	rm -rf build
	rm -rf dist
	python -m build
	python -m twine upload dist/*
