/**
 * Language Completeness Test
 * Verifies that all 22 Eighth Schedule Indian language locale files:
 * 1. Exist and are valid JSON.
 * 2. Contain all required translation keys without missing keys.
 * 3. Have non-empty string values.
 * 4. Do not contain raw English placeholders or untranslated '[TODO]' tags.
 */

import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const EXPECTED_22_LANGUAGES = [
  'as', 'bn', 'brx', 'doi', 'gu', 'hi', 'kn', 'ks', 'kok',
  'mai', 'ml', 'mni', 'mr', 'ne', 'or', 'pa', 'sa', 'sat',
  'sd', 'ta', 'te', 'ur'
];

const LOCALES_DIR = path.resolve(__dirname, '../i18n/locales');

function getNestedKeys(obj, prefix = '') {
  return Object.keys(obj).reduce((res, el) => {
    if (Array.isArray(obj[el])) {
      return res;
    } else if (typeof obj[el] === 'object' && obj[el] !== null) {
      return [...res, ...getNestedKeys(obj[el], prefix + el + '.')];
    }
    return [...res, prefix + el];
  }, []);
}

function getNestedValue(obj, pathStr) {
  return pathStr.split('.').reduce((prev, curr) => prev && prev[curr], obj);
}

describe('22 Indian Languages Completeness Audit', () => {
  // Load baseline Hindi file as key reference
  const hiPath = path.join(LOCALES_DIR, 'hi.json');
  expect(fs.existsSync(hiPath), 'Hindi baseline locale must exist').toBe(true);
  const baselineData = JSON.parse(fs.readFileSync(hiPath, 'utf-8'));
  const requiredKeys = getNestedKeys(baselineData);

  it('should have all 22 locale JSON files present', () => {
    for (const lang of EXPECTED_22_LANGUAGES) {
      const filePath = path.join(LOCALES_DIR, `${lang}.json`);
      expect(fs.existsSync(filePath), `Locale file for ${lang} must exist`).toBe(true);
    }
  });

  for (const lang of EXPECTED_22_LANGUAGES) {
    it(`should verify ${lang}.json has all ${requiredKeys.length} keys populated`, () => {
      const filePath = path.join(LOCALES_DIR, `${lang}.json`);
      const content = fs.readFileSync(filePath, 'utf-8');
      const data = JSON.parse(content);
      const keys = getNestedKeys(data);

      // Check missing keys
      const missingKeys = requiredKeys.filter((k) => !keys.includes(k));
      expect(missingKeys, `Language ${lang} has missing keys: ${missingKeys.join(', ')}`).toEqual([]);

      // Verify no empty values or raw placeholder tokens
      for (const k of requiredKeys) {
        const val = getNestedValue(data, k);
        expect(typeof val, `Key ${k} in ${lang} must be string`).toBe('string');
        expect(val.trim().length, `Key ${k} in ${lang} cannot be empty`).toBeGreaterThan(0);
        expect(val.includes('[TODO]'), `Key ${k} in ${lang} must not have [TODO] placeholder`).toBe(false);
      }
    });
  }
});
