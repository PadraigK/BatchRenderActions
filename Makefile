.PHONY: build clean

BLENDER ?= /Applications/Blender.app/Contents/MacOS/Blender
SOURCE_DIR := src
OUTPUT_DIR := build

build: ensure-build-dir
	$(BLENDER) --command extension build --source-dir $(SOURCE_DIR) --output-dir $(OUTPUT_DIR)

ensure-build-dir:
	mkdir -p $(OUTPUT_DIR)

clean:
	rm -rf $(OUTPUT_DIR)
