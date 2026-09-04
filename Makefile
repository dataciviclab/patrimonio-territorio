# Patrimonio Territorio — Makefile
TOOLKIT = toolkit

DATASETS := $(shell find datasets -name dataset.yml 2>/dev/null | sort)

.PHONY: run run-all check dashboard clean registry help

# --- Run pipeline -----------------------------------------------------------
run:
	@for f in $(DATASETS); do \
		echo "=== $$f ==="; \
		$(TOOLKIT) run --config "$$f" || exit 1; \
	done

run-all: run

# --- Validazione config -----------------------------------------------------
check:
	@for f in $(DATASETS); do \
		echo "→ $$f"; \
		$(TOOLKIT) run preflight --config "$$f" > /dev/null 2>&1 || exit 1; \
	done
	@echo "✅ All configs valid"

# --- Dashboard --------------------------------------------------------------
dashboard:
	cd dashboard && streamlit run app.py

# --- Pulizia ----------------------------------------------------------------
clean:
	rm -rf out/data/_runs out/data/probe out/data/raw out/data/clean out/data/mart

# --- Registry ---------------------------------------------------------------
registry:
	$(TOOLKIT) registry build --prefix patrimonio_territorio

registry-write:
	$(TOOLKIT) registry build --prefix patrimonio_territorio --write

# --- Help -------------------------------------------------------------------
help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sort
