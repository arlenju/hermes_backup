# Editable diagram exports

Use this reference when a user asks for a topology/architecture diagram **and may need to modify it later**.

## Recommended deliverables

Produce both:

1. A presentation/preview image (`.png`) for quick viewing in chat.
2. An editable artifact, preferably `.drawio` for diagrams.net/draw.io. Also provide `.svg` when useful for vector editors.

## Draw.io generation pattern

A `.drawio` file is XML. Create:

- `<mxfile><diagram><mxGraphModel><root>` skeleton
- root cells `id="0"` and `id="1" parent="0"`
- component boxes as `mxCell vertex="1" parent="1"` with `mxGeometry x/y/width/height`
- links as `mxCell edge="1" parent="1" source="..." target="..."` with `mxGeometry relative="1"`

Use stable IDs for important devices so edges can connect to vertices. Keep labels in HTML where useful (`<b>FIREWALL</b><br>HKGNC_FW01`).

## User guidance after delivery

If the user opens the file in diagrams.net and cannot edit individual objects, tell them:

- Press `Esc` to clear whole-diagram selection.
- Double-click text/objects to edit labels.
- If objects are grouped, use `排列 → 取消组合` or `Cmd+Shift+U`.
- Use `Cmd+S` or the red “修改未保存” banner to save.

## Pitfall

Do not only deliver a raster PNG when the user is designing topology. PNG is useful for preview, but network diagrams usually need later edits, so pair it with `.drawio` or another editable vector/source format.

### Feishu delivery of .drawio / .excalidraw files

When sending via Feishu `MEDIA:` protocol, `.drawio` and `.excalidraw` files are silently dropped. Always bundle or rename:

```bash
# Zip them
zip -9 topology_editable.zip topology.drawio topology.excalidraw

# Or rename to .txt
cp topology.drawio topology_drawio.txt
cp topology.excalidraw topology_excalidraw.txt
```

Then send via `MEDIA:`, and tell the user to rename back (remove `.txt`) after downloading.