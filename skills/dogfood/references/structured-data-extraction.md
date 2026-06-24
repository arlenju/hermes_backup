# Structured Data Extraction via browser_console

Extract structured data (tables, lists, JSON) from web pages using `browser_console(expression=...)` with JavaScript.

## When to Use

Replace `web_extract` + `web_search` when:
- The page loads data dynamically (JS-rendered tables, SPAs)
- You need specific structured fields (prices, stats, model lists)
- The page has Cloudflare or anti-bot protection that blocks web_extract
- You need to filter/transform data server-side before it enters your context

## Technique

### Step 1: Navigate to the page
```python
browser_navigate(url="https://example.com/data-page")
```

### Step 2: Run a JS expression to extract the data
```python
browser_console(expression="""\
// Use document.querySelectorAll to grab table rows
const rows = document.querySelectorAll('table tbody tr');
const data = [];
rows.forEach(row => {
  const cells = row.querySelectorAll('td');
  if (cells.length >= 3) {
    data.push({
      name: cells[0].textContent.trim(),
      provider: cells[1].textContent.trim(),
      context: cells[2].textContent.trim()
    });
  }
});
JSON.stringify(data);
""")
```

### Step 3: Process the structured result
The `result` field returns a JSON string — parse and use it directly.

## Patterns

### Table row extraction
```javascript
const rows = document.querySelectorAll('table tbody tr');
JSON.stringify(Array.from(rows).map(row =>
  Array.from(row.querySelectorAll('td')).map(cell => cell.textContent.trim())
));
```

### Link list
```javascript
JSON.stringify(Array.from(document.querySelectorAll('a[href]')).map(a => ({
  text: a.textContent.trim(),
  href: a.href
})));
```

### Nested data with child elements
```javascript
const items = [];
document.querySelectorAll('.card').forEach(card => {
  items.push({
    title: card.querySelector('h3')?.textContent?.trim(),
    desc: card.querySelector('p')?.textContent?.trim(),
    link: card.querySelector('a')?.href
  });
});
JSON.stringify(items);
```

### With filtering
```javascript
const filtered = Array.from(document.querySelectorAll('tr'))
  .filter(row => row.querySelector('.free-badge'))
  .map(row => ({
    name: row.querySelector('td:first-child a')?.textContent?.trim(),
    context: row.querySelector('td:nth-child(3)')?.textContent?.trim()
  }));
JSON.stringify(filtered);
```

## Pitfalls

1. **Variable re-declaration** — If you run multiple expressions in the same page, use fresh variable names each time (`rows1`, `rows2`, `allRows`) to avoid `Identifier has already been declared` errors.

2. **Selector fragility** — Table structures vary across sites. Inspect the actual HTML via `browser_snapshot()` first to understand the DOM structure before writing selectors.

3. **Missing data** — If cells have nested elements (`a`, `span`, `p`), `textContent` on the `td` returns concatenated text. Use more specific selectors like `td:first-child a` instead.

4. **Pagination** — The expression only sees the current page. For multi-page data, extract the first page, then navigate and repeat.

## When to Use Alternatives

| Tool | Best for |
|------|----------|
| `web_extract` | Static pages, markdown, PDFs |
| `browser_console(expression=...)` | Dynamic/JS-rendered tables, structured extraction |
| `browser_vision` | Visual layout inspection, CAPTCHA, screenshot evidence |
