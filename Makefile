
test:
	black --check benekli
	pylint benekli

reuse:
	reuse annotate --style python --merge-copyrights --license=GPL-3.0-or-later --copyright="Mete Balci" --year 2025 -r benekli

upload:
	rm -rf build
	rm -rf dist
	python -m build
	python -m twine upload dist/*
