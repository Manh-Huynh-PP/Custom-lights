# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.5] - 2026-07-11

### Added
- **Interactive Check Visibility Dialog**: Rebuilt the "Check Visibility" popup as an interactive dialog (`invoke_props_dialog`). Toggling the Viewport or Render status inside the dialog now applies the changes in real-time without closing the popup.
- **Outliner Eye & Viewport Syncing**: Toggling viewport visibility in the panel or dialog now automatically syncs both `hide_viewport` (Monitor icon) and `hide_set()` (Outliner Eye icon), solving desynchronization issues.
- **Dynamic State Icons**: Toggles inside the mismatch dialog now render dynamic icons (`HIDE_ON`/`HIDE_OFF`, `RESTRICT_RENDER_ON`/`RESTRICT_RENDER_OFF`) to reflect current Outliner states.

### Fixed
- **Fixed Manage Lights Panel Typos**: Resolved a crash where the N-panel failed to draw due to a typo `CHECKBOX_DECT` (corrected to `CHECKBOX_DEHLT`).
- **Fixed Submodule Reloading**: Added recursive submodule reloading (`importlib.reload(ui_ops)`) to `__init__.py` to ensure that F3 -> Reload Scripts properly loads all submodule changes.

---

## [2.1.4] - 2026-06-17

### Added
- **Enhanced Hotkey Customization UI**: Replaced the default `rna_keymap_ui.draw_kmi` keymap widget with a custom layout row. This hides the internal operator name/identifier to prevent confusion, and exposes modifier keys (`Shift`, `Ctrl`, `Alt`, `OS`) directly as clean toggle buttons (using `*_ui` boolean properties).
- **Addon Website URL**: Uncommented and configured the repository URL (`https://github.com/Manh-Huynh-PP/Custom-lights`) in both `blender_manifest.toml` and legacy `bl_info` metadata.

### Fixed
- **Fixed Preferences Panel Crash**: Resolved a Blender startup/preference crash caused by using the invalid icon `KEYBOARD_KEY`. Changed the icon to `PREFERENCES`.
- **Fixed Visibility Setting Resets**: Resolved a bug where opening the Quick Adjust menu (`L` key) on a mesh light or standard light would reset its Cycles ray visibility settings to defaults. Implemented an `is_initializing` flag to suppress property update callbacks during initialization.

---

## [2.1.3] - 2026-06-15

### Added
- **UI Feasibility Checks for Gradients**: The "Flip Gradient" and "Rotate Gradient" options in the Quick Adjust Menu (`L` key popup) are now displayed conditionally.
  - "Flip Gradient" is shown only if the active light has a valid ColorRamp node with at least 2 color stops.
  - "Rotate Gradient" is shown only if the active light's shader tree has both a "Separate XYZ" and a "Gradient Texture" node.
  - The entire layout row and separator are hidden if neither option is feasible.

### Fixed
- **Blender Crash Prevention (Popup Operator Execution)**: Resolved a Blender C-level crash (access violation in `MSVCP140.dll` / `wm_block_redo_cb`) that occurred when executing the Flip or Rotate operators from inside the transient popup menu. These operators are now registered as `INTERNAL`, and their undo states are pushed manually using Python's `undo_push()`.
- **Solo Light Behavior Fix**: Resolved a selection-change logic bug. Selecting another light after explicitly turning off Solo Light for the active light via the popup no longer automatically re-activates Solo Mode. Solo Mode now strictly honors the active/inactive state of `scene.custom_light_solo_active`.

---

## [2.1.2] - 2026-06-15

### Added
- **Multi-Light Quick Adjust (Relative/Absolute)**: Pressing `L` when multiple managed lights are selected now opens a multi-light parameter adjustment popup with a **Relative Offset Mode** toggle (default: ON). This allows you to adjust values (energy, size, spot settings, point radius) relatively, preserving their ratios, or absolutely.
- **Clean Empty Collections Button**: Added a utility button "Clean Empty Collections" in the Manage Lights panel to recursively find and delete empty collections (containing no objects and no children).
- **Check Visibility Mismatch Button**: Added a utility button "Check Visibility" in the Manage Lights panel that scans all managed lights, detects mismatched viewport/render states (e.g. visible in viewport but hidden in renders, or vice versa), selects them in the 3D Viewport, and displays them in a dialog popup.
- **Dynamic Property Grouping**: The multi-light adjustment menu dynamically detects light types in the selection (e.g. Area, Spot, Point) and only displays fields relevant to the selected types.
- **Realtime Synchronization**: Adjusting sliders/parameters updates all selected lights of the corresponding type in realtime.

### Fixed
- **Duplicate Collections Fix**: Refactored `create_or_get_collection` to check global `bpy.data.collections` first. If a collection already exists but is not linked to the current parent, it is linked instead of creating duplicate collections with numbered suffixes (like `Base Lights.001`).

---

## [2.1.1] - 2026-06-15

### Added
- **Target Parent Collection Customization**: Added option in N-panel to route new lights either to a newly typed parent collection name or to an existing collection selected from a dropdown.
- **Smart Shortcut Dispatcher (`L` key)**: Pressing `L` now automatically decides what to open:
  - If a light or mesh light is active, opens the parameters Quick Adjust popup.
  - Otherwise, opens the Viewport Pie Menu.
- **Auto View Layer Activation**: Adding a light automatically includes and activates both its parent and sub-collection in the View Layer if they were excluded or hidden, avoiding errors and showing the new light immediately.
- **Tracker Light Default Count**: Set the default number of lights to 3 (previously 1) when creating Tracker Lights.

### Fixed
- **AttributeError Fix**: Resolved `AttributeError: 'LIGHTING_OT_select_collection_all' object has no attribute 'enabled'` which caused the entire "Manage Lights" panel to go blank.
- **Removed keymap `Shift + Alt + L`** in favor of the new smart dispatcher.

---

## [2.1.0] - 2026-06-15

### Added
- **Viewport Pie Menu**: Added an 8-directional pie menu for rapid viewport lighting workflows:
  - Add standard lights (Point, Area, Spot, Sun) or a Tracker Light.
  - Track to Selected.
  - Toggle Solo mode for the active light.
  - Call the Quick Adjust popup menu.
- **World HDRI Z-Rotation Control**: Added a Z-rotation slider under World controls to rotate the environment map around the Z axis. Automatically configures and links Texture Coordinate and Mapping nodes to the Environment Texture if missing.
- **Real-time Gobo Parameter Panel**: Added a dynamic sub-panel that displays when a Gobo light or Gobo mesh is selected, allowing direct control of Noise, Voronoi, Wave, Image, Mapping, and ColorRamp nodes from the sidebar without opening the Shader Editor. Exposes the ColorRamp directly inside the N-panel using a native color ramp UI template.
- **Light Solo / Isolate Mode**: Added a dedicated Solo button next to each light in the Manage Lights list to temporarily hide all other light sources and isolate the active light. Restores the previous visibility states of all lights on toggle.
- **Excluded Collection Handling**: Added an Include/Exclude checkbox directly inside the Manage Lights list next to each collection. Excluded collections are grayed out, showing an `[EXCLUDED]` tag. Safeguards selection operations from executing on excluded lights, preventing Blender RuntimeErrors.
- **Quick Deletion**: Added a trash icon button next to each light inside the Manage Lights list to delete lights instantly.
- **Filter Tabs**: Added tabs at the top of the Manage Lights panel to filter listed objects by type: All, Base Lights, Mesh Lights, or Gobos.

### Changed
- **Consolidated Auto-Collection Logic**: Reduced Outliner clutter by grouping all 12+ light types into 4 core sub-collections under `"Custom Lights"`:
  - `"Base Lights"`: Point, Sun, Spot, Area, and Tracker lights.
  - `"Gobo Lights"`: Noise Gobo, Image Gobo, and Plane Gobos.
  - `"Studio Planes"`: Linear/Sphere Gradient planes and Translucent planes.
  - `"Env & Effects"`: Dome Light (HDRI) and God Rays.
- **Addon Version**: Bumped version from 2.0.2 to 2.1.0 in `__init__.py` and `blender_manifest.toml`.
- **Documentation**: Updated `README.md` and `README_VN.md` to document all new features.

---

## [2.0.2] - 2026-06-15

### Added
- Centralized visibility toggle buttons (Viewport hide / Render hide) next to lights and collections in the Manage Lights panel.
- Collection Brightness Multiplier slider to scale the brightness of all lights in a collection simultaneously, with a bake/apply checkmark button.
- Support for Blender 4.2+ extensions packaging layout (added `blender_manifest.toml`).

---

## [2.0.0] - 2026-06-15

### Added
- **Split Gradient Light Plane**: Separate operators for Linear Gradient and Sphere Gradient light planes. Added "Transparent Black Gradient" checkbox to render black areas as transparent.
- **Plane Gobo Lights**: Added three new procedural mesh gobo operators: `P.Noise` (Noise), `P.Voronoise` (Voronoi), and `P.Wave` (Wave).
- **Physical Kelvin Blackbody Colors**: Upgraded Black Body color calculator to match Blender's physical light equations.
- **Blender 5.0 compatibility**: Fully updated and tested to ensure seamless performance with Blender 5.0 release.
- **World Brightness Control**: Quickly adjust world/environment strength from the Manage Lights panel.
- **Gobo Light Noise**: Add organic variation and texture to standard lights.
- **Image Gobo Light**: Project images and custom patterns.
