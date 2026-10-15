with open('frontend/src/styles/index.css', 'r', encoding='utf-8') as f:
    css = f.read()

extra_css = '''
/* ══════════════════════════════════════════════════════════════════════════
   HIGH-CONTRAST MODE FIXES FOR SCHEME CARDS, CATEGORIES & INLINE SURFACES
   ══════════════════════════════════════════════════════════════════════════ */
.gov-category-chip {
  background-color: #F8FAFC;
  color: var(--color-navy);
  border: 1px solid var(--color-border);
}
.gov-category-chip.active {
  background-color: var(--color-navy);
  color: #FFFFFF;
  border-color: var(--color-navy);
}

html.gov-high-contrast .gov-category-chip {
  background-color: #1E2732 !important;
  color: #FFFFFF !important;
  border: 1px solid #687585 !important;
}

html.gov-high-contrast .gov-category-chip.active {
  background-color: #7DD3FC !important;
  color: #0B0F14 !important;
  border-color: #FFFFFF !important;
  font-weight: 700 !important;
}

html.gov-high-contrast .gov-category-chip:hover {
  background-color: #151B23 !important;
  color: #7DD3FC !important;
  border-color: #7DD3FC !important;
}

/* Force dark card surface on any catalogue cards or containers */
html.gov-high-contrast .scheme-card,
html.gov-high-contrast .civic-card,
html.gov-high-contrast .scheme-filter-toolbar,
html.gov-high-contrast [style*="background-color: #FFFFFF"],
html.gov-high-contrast [style*="background-color: #ffffff"],
html.gov-high-contrast [style*="background-color: rgb(255, 255, 255)"],
html.gov-high-contrast [style*="background-color: white"],
html.gov-high-contrast [style*="background: #FFFFFF"],
html.gov-high-contrast [style*="background: #ffffff"],
html.gov-high-contrast [style*="background: rgb(255, 255, 255)"],
html.gov-high-contrast [style*="background: white"],
html.gov-high-contrast [style*="background-color: #F8FAFC"],
html.gov-high-contrast [style*="background-color: #f8fafc"] {
  background-color: #151B23 !important;
  background: #151B23 !important;
  border-color: #687585 !important;
  color: #FFFFFF !important;
}

/* Scheme Card Typography inside High-Contrast */
html.gov-high-contrast .scheme-card h2,
html.gov-high-contrast .scheme-card-title,
html.gov-high-contrast .civic-card h2,
html.gov-high-contrast .civic-card h3 {
  color: #FFFFFF !important;
}

html.gov-high-contrast .scheme-card p,
html.gov-high-contrast .scheme-description,
html.gov-high-contrast .scheme-department {
  color: #D1D5DB !important;
}

/* High Contrast Badges and Pills */
html.gov-high-contrast [style*="#EFF6FF"],
html.gov-high-contrast [style*="#eff6ff"],
html.gov-high-contrast [style*="#DBEAFE"],
html.gov-high-contrast [style*="#BFDBFE"],
html.gov-high-contrast [style*="#E0F2FE"],
html.gov-high-contrast .scheme-badge-level {
  background-color: #1E2732 !important;
  background: #1E2732 !important;
  color: #7DD3FC !important;
  border: 1px solid #7DD3FC !important;
}

html.gov-high-contrast [style*="#ECFDF5"],
html.gov-high-contrast [style*="#ecfdf5"],
html.gov-high-contrast [style*="#F0FDF4"],
html.gov-high-contrast [style*="#f0fdf4"],
html.gov-high-contrast [style*="#DCFCE7"],
html.gov-high-contrast [style*="#D1FAE5"],
html.gov-high-contrast [style*="#BBF7D0"],
html.gov-high-contrast [style*="#A7F3D0"],
html.gov-high-contrast .scheme-benefit-pill,
html.gov-high-contrast .scheme-badge-verified {
  background-color: #052E16 !important;
  background: #052E16 !important;
  color: #86EFAC !important;
  border: 1px solid #86EFAC !important;
}

html.gov-high-contrast [style*="#FEF3C7"],
html.gov-high-contrast [style*="#fef3c7"],
html.gov-high-contrast [style*="#FFFBEB"],
html.gov-high-contrast [style*="#FDE68A"],
html.gov-high-contrast [style*="#FCD34D"],
html.gov-high-contrast .scheme-btn-benefits {
  background-color: #422006 !important;
  background: #422006 !important;
  color: #FDE047 !important;
  border: 1px solid #FDE047 !important;
}

html.gov-high-contrast [style*="#F1F5F9"],
html.gov-high-contrast [style*="#f1f5f9"],
html.gov-high-contrast [style*="#E2E8F0"],
html.gov-high-contrast [style*="#e2e8f0"],
html.gov-high-contrast .scheme-badge-category {
  background-color: #1E2732 !important;
  background: #1E2732 !important;
  color: #D1D5DB !important;
  border: 1px solid #687585 !important;
}
'''

if 'HIGH-CONTRAST MODE FIXES FOR SCHEME CARDS' not in css:
    css = css + '\n' + extra_css
    with open('frontend/src/styles/index.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print("Successfully appended high-contrast overrides to index.css")
else:
    print("Overrides already present")
