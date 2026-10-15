with open('frontend/src/pages/SchemeCataloguePage.jsx', 'r', encoding='utf-8') as f:
    s = f.read()

# 1. Search & Filter Toolbar
old_toolbar = '''      {/* Search & Filter Toolbar */}
      <div
        style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '24px',
          boxShadow: '0 2px 6px rgba(0,0,0,0.04)',
        }}
      >'''

new_toolbar = '''      {/* Search & Filter Toolbar */}
      <div
        className="civic-card scheme-filter-toolbar"
        style={{
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '24px',
          boxShadow: '0 2px 6px rgba(0,0,0,0.04)',
        }}
      >'''

if old_toolbar in s:
    s = s.replace(old_toolbar, new_toolbar)
    print("Replaced toolbar")
else:
    print("Toolbar already replaced or pattern not found")

# 2. Category filter chips
old_chip = '''              <button
                key={cat.key}
                type="button"
                onClick={() => setCategoryFilter(cat.key)}
                style={{
                  padding: '6px 12px',
                  borderRadius: '16px',
                  fontSize: '0.8125rem',
                  fontWeight: isSelected ? 700 : 500,
                  border: isSelected ? '1px solid var(--color-navy)' : '1px solid var(--color-border)',
                  backgroundColor: isSelected ? 'var(--color-navy)' : '#F8FAFC',
                  color: isSelected ? '#FFFFFF' : 'var(--color-text-primary)',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.15s ease',
                }}
              >'''

new_chip = '''              <button
                key={cat.key}
                type="button"
                onClick={() => setCategoryFilter(cat.key)}
                className={`gov-category-chip ${isSelected ? 'active' : ''}`}
                style={{
                  padding: '6px 14px',
                  borderRadius: '16px',
                  fontSize: '0.8125rem',
                  fontWeight: isSelected ? 700 : 600,
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.15s ease',
                }}
              >'''

if old_chip in s:
    s = s.replace(old_chip, new_chip)
    print("Replaced category chips")
else:
    print("Category chips already replaced or pattern not found")

# 3. Scheme Card wrapper
old_card = '''              <div
                key={scheme.id}
                style={{
                  backgroundColor: '#FFFFFF',
                  border: '1px solid var(--color-border)',
                  borderRadius: '8px',
                  padding: '20px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.03)',
                  transition: 'transform 0.15s ease, box-shadow 0.15s ease',
                }}
              >'''

new_card = '''              <div
                key={scheme.id}
                className="civic-card scheme-card"
                style={{
                  borderRadius: '8px',
                  padding: '20px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.03)',
                  transition: 'transform 0.15s ease, box-shadow 0.15s ease',
                }}
              >'''

if old_card in s:
    s = s.replace(old_card, new_card)
    print("Replaced scheme card wrapper")
else:
    print("Scheme card wrapper already replaced or pattern not found")

with open('frontend/src/pages/SchemeCataloguePage.jsx', 'w', encoding='utf-8') as f:
    f.write(s)

print("Saved SchemeCataloguePage.jsx")
