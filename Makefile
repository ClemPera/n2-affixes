PY := .venv/bin/python

.PHONY: deck qa release

deck:
	$(PY) scripts/build_deck.py
	$(PY) scripts/qa_deck.py

qa:
	$(PY) scripts/qa_deck.py

release:
	@test -n "$(VERSION)" || (echo "Usage: make release VERSION=1.1.0 NOTE='what changed'" && exit 1)
	$(PY) scripts/release.py "$(VERSION)" --note "$(NOTE)"
