import React from 'react';

export function Badge({ variant = 'draft', children }) {
  const variantClass = {
    civic: 'badge-civic',
    demo: 'badge-civic',
    reviewed: 'badge-reviewed',
    draft: 'badge-draft',
    missing: 'badge-missing',
  }[variant] || 'badge-civic';

  return <span className={`badge ${variantClass}`}>{children}</span>;
}
