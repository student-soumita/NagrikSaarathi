import re

with open('frontend/src/pages/SchemeCataloguePage.jsx', 'r', encoding='utf-8') as f:
    s = f.read()

# 1. Search filter toolbar
s = re.sub(
    r'\{\/\* Search & Filter Toolbar \*\/\}\s*<div\s*style=\{\{\s*backgroundColor:\s*[\'"]#FFFFFF[\'"],\s*border:\s*[\'"]1px solid var\(--color-border\)[\'"],\s*borderRadius:\s*[\'"]8px[\'"],\s*padding:\s*[\'"]16px[\'"],\s*marginBottom:\s*[\'"]24px[\'"],\s*boxShadow:\s*[\'"]0 2px 6px rgba\(0,0,0,0\.04\)[\'"],\s*\}\}',
    '''{/* Search & Filter Toolbar */}
      <div
        className="civic-card scheme-filter-toolbar"
        style={{
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '24px',
          boxShadow: '0 2px 6px rgba(0,0,0,0.04)',
        }}''',
    s
)

# 2. Category filter chips
s = re.sub(
    r'<button\s*key=\{cat\.key\}\s*type="button"\s*onClick=\{\(\) => setCategoryFilter\(cat\.key\)\}\s*style=\{\{[^}]*backgroundColor:[^}]*\}\}\s*>',
    '''<button
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
              >''',
    s
)

# 3. Scheme Card wrapper
s = re.sub(
    r'<div\s*key=\{scheme\.id\}\s*style=\{\{\s*backgroundColor:\s*[\'"]#FFFFFF[\'"],\s*border:\s*[\'"]1px solid var\(--color-border\)[\'"],\s*borderRadius:\s*[\'"]8px[\'"],\s*padding:\s*[\'"]20px[\'"],\s*display:\s*[\'"]flex[\'"],\s*flexDirection:\s*[\'"]column[\'"],\s*justifyContent:\s*[\'"]space-between[\'"],\s*boxShadow:\s*[\'"]0 2px 4px rgba\(0,0,0,0\.03\)[\'"],\s*transition:\s*[\'"]transform 0\.15s ease, box-shadow 0\.15s ease[\'"],\s*\}\}\s*>',
    '''<div
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
              >''',
    s
)

# 4. Scheme Badges
s = re.sub(
    r'<span\s*style=\{\{\s*fontSize:\s*[\'"]0\.6875rem[\'"],\s*fontWeight:\s*700,\s*backgroundColor:\s*scheme\.government_level === [\'"]central[\'"] \? [\'"]#EFF6FF[\'"] : [\'"]#F0FDF4[\'"],',
    '''<span
                      className={`scheme-badge-level ${scheme.government_level}`}
                      style={{
                        fontSize: '0.6875rem',
                        fontWeight: 700,
                        padding: '2px 6px',
                        borderRadius: '4px',
                        border: '1px solid var(--color-border)',
                      }}''',
    s
)

# 5. Category badge
s = re.sub(
    r'<span\s*style=\{\{\s*fontSize:\s*[\'"]0\.6875rem[\'"],\s*fontWeight:\s*600,\s*backgroundColor:\s*[\'"]#F1F5F9[\'"],\s*color:\s*[\'"]#475569[\'"],\s*padding:\s*[\'"]2px 6px[\'"],\s*borderRadius:\s*[\'"]4px[\'"],\s*\}\}\s*>\s*\{scheme\.category\?\.toUpperCase\(\) \|\| [\'"]GENERAL[\'"]\}',
    '''<span
                        className="scheme-badge-category"
                        style={{
                          fontSize: '0.6875rem',
                          fontWeight: 600,
                          padding: '2px 6px',
                          borderRadius: '4px',
                        }}
                      >
                        {scheme.category?.toUpperCase() || 'GENERAL'}''',
    s
)

# 6. Verified badge
s = re.sub(
    r'<span\s*style=\{\{\s*fontSize:\s*[\'"]0\.6875rem[\'"],\s*fontWeight:\s*600,\s*backgroundColor:\s*[\'"]#DCFCE7[\'"],\s*color:\s*[\'"]#166534[\'"],\s*padding:\s*[\'"]2px 6px[\'"],\s*borderRadius:\s*[\'"]4px[\'"],\s*\}\}\s*title="Verified against official ministry notification"\s*>',
    '''<span
                        className="scheme-badge-verified"
                        style={{
                          fontSize: '0.6875rem',
                          fontWeight: 600,
                          padding: '2px 6px',
                          borderRadius: '4px',
                        }}
                        title="Verified against official ministry notification"
                      >''',
    s
)

# 7. Scheme Title
s = re.sub(
    r'<h2\s*style=\{\{\s*fontSize:\s*[\'"]1\.125rem[\'"],\s*fontWeight:\s*700,\s*color:\s*[\'"]var\(--color-navy\)[\'"],\s*margin:\s*[\'"]0 0 6px 0[\'"],\s*lineHeight:\s*1\.35,\s*\}\}\s*>',
    '''<h2
                    className="scheme-card-title"
                    style={{
                      fontSize: '1.125rem',
                      fontWeight: 700,
                      margin: '0 0 6px 0',
                      lineHeight: 1.35,
                    }}
                  >''',
    s
)

# 8. Benefit pill
s = re.sub(
    r'<div\s*style=\{\{\s*display:\s*[\'"]inline-flex[\'"],\s*alignItems:\s*[\'"]center[\'"],\s*gap:\s*[\'"]6px[\'"],\s*fontSize:\s*[\'"]0\.8125rem[\'"],\s*fontWeight:\s*700,\s*backgroundColor:\s*[\'"]#ECFDF5[\'"],\s*color:\s*[\'"]#065F46[\'"],\s*border:\s*[\'"]1px solid #A7F3D0[\'"],\s*padding:\s*[\'"]3px 8px[\'"],\s*borderRadius:\s*[\'"]6px[\'"],\s*marginBottom:\s*[\'"]8px[\'"],\s*\}\}\s*>',
    '''<div
                      className="scheme-benefit-pill"
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        fontSize: '0.8125rem',
                        fontWeight: 700,
                        padding: '3px 8px',
                        borderRadius: '6px',
                        marginBottom: '8px',
                      }}
                    >''',
    s
)

# 9. Scheme Department
s = re.sub(
    r'<div\s*style=\{\{\s*fontSize:\s*[\'"]0\.8125rem[\'"],\s*color:\s*[\'"]var\(--color-text-secondary\)[\'"],\s*marginBottom:\s*[\'"]12px[\'"],\s*fontWeight:\s*500,\s*\}\}\s*>',
    '''<div
                    className="scheme-department"
                    style={{
                      fontSize: '0.8125rem',
                      marginBottom: '12px',
                      fontWeight: 500,
                    }}
                  >''',
    s
)

# 10. Scheme Description
s = re.sub(
    r'<p\s*style=\{\{\s*fontSize:\s*[\'"]0\.875rem[\'"],\s*color:\s*[\'"]var\(--color-text-primary\)[\'"],\s*lineHeight:\s*1\.5,\s*marginBottom:\s*[\'"]16px[\'"],\s*display:\s*[\'"]-webkit-box[\'"],\s*WebkitLineClamp:\s*3,\s*WebkitBoxOrient:\s*[\'"]vertical[\'"],\s*overflow:\s*[\'"]hidden[\'"],\s*\}\}\s*>',
    '''<p
                    className="scheme-description"
                    style={{
                      fontSize: '0.875rem',
                      lineHeight: 1.5,
                      marginBottom: '16px',
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                    }}
                  >''',
    s
)

with open('frontend/src/pages/SchemeCataloguePage.jsx', 'w', encoding='utf-8') as f:
    f.write(s)

print("Updated SchemeCataloguePage.jsx successfully!")
