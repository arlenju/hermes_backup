# Editable Diagram Deliverables

When a user asks for a topology/architecture diagram they may need a *source file*, not only a rendered PNG. Prefer delivering at least one editable format alongside the preview.

## Recommended formats

- `.drawio` — best default for network/topology diagrams. Opens in diagrams.net/draw.io and preserves separately editable nodes, edges, labels, containers, and colors.
- `.svg` — useful as a vector asset for docs/slides; editable in Figma/Illustrator/Inkscape if objects are separate SVG elements.
- `.html` — good for presentation/preview but not ideal as a source file unless the user explicitly wants browser-rendered SVG.
- `.pptx` — useful when the user wants PowerPoint-native editing; create with shape primitives when possible.

## Draw.io generation pattern

A useful `.drawio` file is XML with:

- `<mxfile><diagram><mxGraphModel><root>` structure
- root cells `id="0"` and `id="1" parent="0"`
- each box/device as an `mxCell vertex="1" parent="1"` with `mxGeometry x/y/width/height`
- each connection as an `mxCell edge="1" parent="1" source="..." target="..."`
- style strings for fill, stroke, font, dashed lines, rounded rectangles, hexagons, etc.

Important: do **not** embed one large PNG or one monolithic SVG inside draw.io when the user asks for editability. That opens as a single object and is not useful. Build the source from separate mxCells.

## Verification

After writing editable files:

1. Parse them as XML to catch malformed markup.
2. Check file sizes and paths.
3. If possible, also render/export a PNG preview for quick visual inspection.
4. Send the editable source file(s), not just the preview.

## User handoff tips for draw.io

If the user asks how to edit in diagrams.net/draw.io:

- Press `Esc` to cancel whole-diagram selection.
- Double-click text to edit labels.
- Select a node/line and drag to move or reroute.
- If an imported object behaves like one big group: `排列 → 取消组合` or `Cmd/Ctrl + Shift + U`.
- Save with `Cmd/Ctrl + S` or click the red “修改未保存” banner.
