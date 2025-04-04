
.PHONY: test reuse test-proof test-unit upload

test:
	black --check benekli
	pylint benekli

test-unit:
	python -m unittest discover tests

reuse:
	reuse annotate --style python --merge-copyrights --license=GPL-3.0-or-later --copyright="Mete Balci" --year 2025 -r benekli

test-proof: FourteenBalls.tif
	benekli -s SC-P800\ Series\ Epson\ Archival\ Matte.icc -d display.icc -i $< -r p -o $(basename $<).p.bpc$(suffix $<) --bpc
	benekli -s SC-P800\ Series\ Epson\ Archival\ Matte.icc -d display.icc -i $< -r p -o $(basename $<).p.nobpc$(suffix $<)
	benekli -s SC-P800\ Series\ Epson\ Archival\ Matte.icc -d display.icc -i $< -r r -o $(basename $<).r.bpc$(suffix $<) --bpc
	benekli -s SC-P800\ Series\ Epson\ Archival\ Matte.icc -d display.icc -i $< -r r -o $(basename $<).r.nobpc$(suffix $<)
	benekli -s SC-P800\ Series\ Epson\ Archival\ Matte.icc -d display.icc -i $< -r a -o $(basename $<).a$(suffix $<)

upload:
	rm -rf build
	rm -rf dist
	python -m build
	python -m twine upload dist/*
