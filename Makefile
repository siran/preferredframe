.PHONY: serve clean


rm:
	@echo "removing site/"
	rm -r site || true

buildb:
	@echo "building ..."
	.scripts/build_site/build_site.py
buildn:
	@echo "building no books ..."
	.scripts/build_site/build_site.py --skip-books

serve: clean buildn
	@echo "serving NO books ..."
	python3 -m http.server -d site 8000
serveb: clean buildb
	@echo "serving WITH books..."
	python3 -m http.server -d site 8000
clean:
	rm -rf site
