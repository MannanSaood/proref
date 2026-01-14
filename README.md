# Professional Referencing & Rig UI

**Industry-grade character linking, override management, and rig UI handling for Blender**

![Blender Version](https://img.shields.io/badge/Blender-3.6%2B-orange)
![License](https://img.shields.io/badge/License-GPL--3.0-blue)
![Version](https://img.shields.io/badge/Version-1.0.0-green)

---

## Features

### 🔗 Smart Character Linking
- **One-click linking** with automatic library override creation
- **Auto-make properties editable** — no more teal fields
- **Unique naming** to prevent conflicts with multiple characters
- **Animation Only Mode** — skip mesh overrides for better performance

### 🎨 Rig UI Isolation
- **Automatic rig_ui.py detection** and script isolation
- **Context-aware execution** — each character gets its own UI context
- **Script safety validation** — checks for unsafe Python patterns
- **Auto-execute on link** option for faster workflow

### 🩺 Override Health System
- **One-click health diagnostics** for all library overrides
- **Detect common issues**: missing references, broken paths, locked properties
- **Automated repair tools** with smart issue resolution
- **Targeted resync** — resync single objects without affecting entire hierarchy

### 📚 Reference Manager
- **Visual library overview** with file size and modification dates
- **Missing file detection** with relocate functionality
- **Batch operations** — reload multiple libraries at once
- **Quick actions panel** for selected overrides

---

## Installation

1. Download the latest release ZIP file
2. In Blender, go to **Edit → Preferences → Add-ons**
3. Click **Install...** and select the ZIP file
4. Enable **"Professional Referencing & Rig UI"**

---

## Quick Start

### Linking a Character

1. Open the **Pro Ref** panel in the 3D Viewport sidebar (`N` key)
2. Click **"Smart Link Character"**
3. Browse to your character `.blend` file
4. The character will be linked with automatic overrides

### Running Health Checks

1. Click **"Run Health Check"** in the Override Health panel
2. Review any issues in the health check list
3. Click **"Repair"** to auto-fix common problems

### Executing Rig UI

1. Select your linked character's armature
2. Click **"Execute Rig UI"** in the Rig UI Management panel
3. The rig controls will appear in the Properties → Bone panel

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+L` | Smart Link Character |
| `Ctrl+Shift+H` | Run Health Check |
| `Ctrl+Shift+R` | Execute Rig UI |
| `Ctrl+Shift+E` | Make All Editable |

*Shortcuts can be disabled in addon preferences.*

---

## Addon Preferences

Access via **Edit → Preferences → Add-ons → Professional Referencing & Rig UI**

- **Default Library Path** — Set a default folder for browsing
- **Linking Defaults** — Configure auto-make-editable and animation mode
- **Safety Settings** — Enable/disable script validation
- **Keyboard Shortcuts** — Enable/disable shortcuts

---

## Troubleshooting

### "Cannot find rig_ui.py script"

The addon searches for scripts with "rig_ui" in the name from the same library as the armature. Ensure your character file has a properly named rig UI script.

### "Library file not found"

Use the **Reference Manager → Relocate File** button to point to the new location of your library file.

### "Override properties not editable"

Click **"Make All Editable"** in the Quick Actions panel, or enable **"Auto Make Editable"** in Link Settings before linking.

### Health check shows many issues

Run **"Repair Override"** to automatically fix common issues like missing editable properties and fully-locked bones.

---

## Compatibility

- **Blender 3.6+** (tested up to 4.x)
- Works with **Rigify**, **Auto-Rig Pro**, and custom rigs
- Compatible with rig UI scripts that follow standard patterns

---

## Support

For bug reports and feature requests, please open an issue on the GitHub repository.

---

## License

This addon is licensed under the **GNU General Public License v3.0** (GPL-3.0).

---

## Credits

Developed for professional animation studios and individual artists who need reliable character referencing in Blender.
