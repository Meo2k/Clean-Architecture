PORT=8000
HOST=127.0.0.1

ifdef public
	HOST=0.0.0.0
endif

.PHONY: all run

all: run

run:
	@echo "Starting server on http://$(HOST):$(PORT)"
	@uv run uvicorn main:app --reload --host $(HOST) --port $(PORT)