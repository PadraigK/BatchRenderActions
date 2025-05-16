# Batch Render Actions

Batch Render Actions is a Blender add-on that lets you render each animation action in your scene to its own folder, using a customizable filename template and output directory.

## Features

- Render all actions in the current Blender file as separate animations.
- Each action is rendered to its own subfolder.
- Customizable filename template for output frames.
- Simple UI panel in the 3D Viewport sidebar.

## Installation

1. (Optional) Build the add-on for packaging:

   ```sh
   make build
   ```

   This creates a ZIP file in the `build` directory.

2. In Blender, go to **Edit > Preferences > Add-ons > Install** and select the ZIP file, or add the source folder directly.

3. Enable the "Batch Render Actions" add-on.

## Usage

1. Select the object whose actions you want to render.
2. Open the **3D Viewport** and go to the **Render Actions** tab in the sidebar.
3. Set the **Filename Template** and **Output Directory** as desired.
4. Click **Render All Actions**. Each action will be rendered as a separate animation in its own folder.

## Development

- Source code: `__init__.py`
- Build system: `Makefile`

### Building

To build the add-on for distribution:

```sh
make build
```

To clean build artifacts:

```sh
make clean
```

## Requirements

- Blender 4.2.0 or newer

## License

SPDX:GPL-3.0-or-later

---

Maintainer: Pádraig Ó Cinnéide