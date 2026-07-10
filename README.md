# Custom Lights


**Professional Lighting Setup Made Easy in Blender.**

Custom Lights is a smart addon designed to streamline and accelerate your lighting workflow in Blender. By combining quick light creation tools with a centralized management interface, it allows you to set up professional lighting scenes in seconds, saving you valuable time to focus on the creative aspects of your detailed 3D work.

## Support & Purchase

- **Get the Addon:** [Gumroad](https://manhdesigns.gumroad.com/l/customlights)
- **Support Development:** [Buy Me a Coffee](https://coffee.manhhuynh.work)

### 🎥 [Watch Version 2.0 Demo](https://youtube.com/shorts/s9AEGNVPpMQ) | [v1 Demo](https://www.youtube.com/shorts/VkU7IYyqykY)

---

## What's New in Custom Lights 2.0

### 🎥 [Watch v2.0 Features Demo](https://youtube.com/shorts/s9AEGNVPpMQ)

### 🚀 Blender 5.0 Compatible
Fully updated and tested to ensure seamless performance with the latest Blender 5.0 release.

### 🌍 World Brightness Control
Quickly adjust your scene's world/environment brightness directly from the Manage Lights panel.

### 🎚️ Collection Brightness Multiplier
New slider on each collection header to multiply brightness of all lights in that collection. Click the ✓ button to apply and reset.

### 🎨 Split Gradient Light Plane
The Gradient Light Plane is now split into two dedicated operators:
- **Linear Gradient** - Creates linear gradient emission planes
- **Sphere Gradient** - Creates spherical gradient emission planes

Both include a new **"Transparent Black Gradient"** checkbox that makes black areas of the gradient transparent.

### ✨ Plane Gobo Lights
Three new plane gobo operators for quick light texture effects:
- **P.Noise** - Noise-based gobo texture
- **P.Voronoise** - Voronoi noise pattern
- **P.Wave** - Wave pattern gobo

### 🌡️ Accurate Black Body Colors
Updated Black Body color values to align perfectly with Blender's physical light calculations.

### ⚡ Quick Access Shortcut "L"
Press **"L"** to instantly open the parameters popup menu when lights are selected (supporting multi-light editing at once), or open the Viewport Pie Menu if no lights are selected.

### 🌐 Light Dome Updates
Significant improvements to the Light Dome feature for better environmental lighting.

### 🔦 Gobo Light Enhancements
- **Gobo Light Noise:** Add organic variation and texture to your lights.
- **Image Gobo Light:** Project images and patterns for complex lighting effects.

### 🎨 UI & Manage Light Updates
- **Clean Filter Tabs:** Filter lights inside the N-panel by type (All, Base Lights, Mesh Lights, Gobos).
- **Light Solo / Isolate:** Focus on a single light source by checking the solo icon. All other lights will be hidden temporarily, and restored when disabled.
- **Collection View Layer Handling:** Check/uncheck collections directly from the panel and avoid Python exceptions when attempting to select objects inside excluded collections.
- **Quick Deletion:** Delete any light directly from the Manage Lights list with a dedicated trash button.

### ☀️ HDRI Z-Rotation Control
Directly rotate environment textures (HDRI) from the World panel using the Z-rotation slider.

### 🎛️ Real-time Gobo Parameter Panel
Adjust Noise, Voronoi, Wave, Image, Mapping, and ColorRamp settings of Gobo objects directly from the N-Panel without opening the Shader Editor.

### 🥧 Viewport Pie Menu ("L" Key with no selection)
Quickly add basic or custom lights, toggle active light Solo mode, or bring up parameters directly under your mouse cursor in the 3D viewport. Pressing **"L"** when no lights are selected will trigger this menu.

---

## Key Features

### 1. Add Base Lights
Rapidly create standard Blender lights at your cursor's position.
- **Types:** Point, Sun, Spot, Area (Rectangle/Ellipse).
- **Auto-Organization:** Automatically groups lights into collections.

### 2. Custom Lights & Tools
Advanced lighting tools for complex scenarios.

- **Tracker Light:** Area lights that automatically track a target object.
- **Linear/Sphere Gradient Plane:** Emissive planes with adjustable gradients and transparent black option.
- **Translucent Light Plane:** Diffusion plane to soften shadows and create studio effects.
- **Simple God Rays:** Volumetric "God Ray" effects for Spot lights.
- **Plane Gobos:** Quick noise, voronoise, and wave pattern gobos.
- **Track to Selected:** Apply "Track To" constraint to multiple objects.
- **Make Emission Mesh:** Convert any mesh into a light source.
- **Input Blackbody Color:** Set light color using Kelvin temperature values.

### 3. Manage Lights
Your command center for all lighting in the scene.
- **Centralized View:** All lights and emissive meshes organized by collection.
- **Collection Brightness:** Multiply brightness of all lights in a collection.
- **World Brightness:** Control environment lighting strength.
- **Direct Control:** Adjust Color, Brightness/Power, and Size/Shape from the list.
- **Selection:** Click names to select lights or entire collections.
- **Visibility:** Toggle Viewport, Render, and Camera visibility.

---

## Installation & Getting Started

1.  **Install:**
    - Download the `custom_light.zip` file.
    - Open Blender and go to **Edit > Preferences > Add-ons**.
    - Click **Install...**, select the zip file, and enable "Custom Lights".

2.  **Location:**
    - In the 3D Viewport, press **"N"** to open the Sidebar.
    - Click on the **"Custom Lights"** tab.

3.  **Start Lighting:**
    - Use the panels to add lights, apply effects, or manage your scene's illumination.

---

## Changelog

For a full list of changes, see [CHANGELOG.md](file:///e:/BLENDER/ADDON/Custom-light/custom_light/CHANGELOG.md).

### [2.1.4] - 2026-06-17
- **Enhanced Hotkey Customization UI**: Custom layout row in Preferences that hides internal operator names/identifiers and exposes clean modifier toggle buttons directly.
- **Addon Website URL**: Configured the official repository URL in both manifest and legacy metadata.
- **Fixed Preferences Panel Crash**: Changed layout label icon from `KEYBOARD_KEY` to `PREFERENCES` to resolve Blender startup crash.
- **Fixed Visibility Setting Resets**: Added `is_initializing` flag to prevent Cycles ray visibility settings from resetting to default values when summoning the Quick Adjust menu (`L` key).

### [2.1.3] - 2026-06-15
- **UI Feasibility Checks for Gradients**: The "Flip Gradient" and "Rotate Gradient" options in the Quick Adjust Menu (`L` key popup) are now displayed conditionally based on node presence.
- **Blender Crash Prevention**: Changed Flip and Rotate operators to `INTERNAL` to prevent Blender from crashing (`MSVCP140.dll` / `wm_block_redo_cb`) when executing them from within transient popup menus. Undo states are pushed manually using Python's `undo_push()`.
- **Solo Light Behavior Fix**: Switching selections to another light after explicitly turning off Solo Light for the active light via the popup no longer automatically re-activates Solo Mode.

### [2.1.2] - 2026-06-15
- **Multi-Light Quick Adjust**: Pressing `L` when multiple managed lights are selected now opens a multi-light parameter adjustment popup.
- **Dynamic Property Grouping**: The multi-light adjustment menu dynamically detects light types in the selection (e.g. Area, Spot, Point) and only displays fields relevant to the selected types.
- **Realtime Synchronization**: Adjusting sliders/parameters updates all selected lights of the corresponding type in realtime.

### [2.1.1] - 2026-06-15
- **Target Collection Selection**: Configure the parent collection directly from the panel (type a new name or select from existing).
- **Smart Shortcut Dispatcher (`L` key)**: Opens the parameter adjustment popup if a light is active, or the viewport Pie Menu if not.
- **Auto View Layer Activation**: Automatically activates/includes excluded target collections when creating new lights to avoid Blender RuntimeErrors.
- **Bug Fix**: Resolved an `AttributeError` on `select_collection_all` that caused the "Manage Lights" panel to go blank.

### [2.1.0] - 2026-06-15
- **Viewport Pie Menu** for quick creation, soloing, and parameter adjustments.
- **World HDRI Z-Rotation Control** directly from the World panel.
- **Real-time Gobo Parameter Panel** in the N-panel (including ColorRamp).
- **Light Solo / Isolate Mode** to focus on a single light source.
- **Excluded Collection Handling** with direct checkbox to include/exclude.
- **Filter Tabs** (All, Base Lights, Mesh Lights, Gobos) at the top of Manage Lights.
- **Quick Deletion** (trash button) next to lights.
- **Consolidated Auto-Collection Logic** to reduce Outliner clutter.

---

*Happy Lighting!*
