# Browser Console JS Extraction

Use `browser_console` with JavaScript to extract structured data from web pages.

## Pattern: Extract Table Data

```javascript
// Unique variable name each time to avoid redeclaration error
const myRows = document.querySelectorAll('table tbody tr');
const results = [];
myRows.forEach(row => {
  const cells = row.querySelectorAll('td');
  if (cells.length >= 3) {
    results.push({
      name: cells[0].textContent.trim(),
      value: cells[1].textContent.trim()
    });
  }
});
JSON.stringify(results);
```

## Pattern: Extract List Data

```javascript
const items = document.querySelectorAll('.list-item');
const data = [];
items.forEach(item => {
  data.push({
    title: item.querySelector('.title')?.textContent?.trim() || '',
    desc: item.querySelector('.desc')?.textContent?.trim() || ''
  });
});
JSON.stringify(data);
```

## Pitfalls

1. **Variable redeclaration.** `const rows = ...` fails on second call — use unique names (`rows1`, `rows2`, `myRows`).
2. **Selector fragility.** Page structure changes — prefer `.querySelectorAll` with class names over nth-child.
3. **Empty results.** The page may not have rendered the data yet — try after `browser_scroll`.
4. **Vision fallback.** When `browser_console` expressions fail or DOM is complex, use `browser_vision` with `annotate=true` for labelled screenshots.
