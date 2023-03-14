/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import {
  getSettings,
} from '../src/utils';


global.fetch = jest.fn(() => Promise.resolve({
  json: () => Promise.resolve({}),
}));


describe('utils.js API calls', () => {
  describe('getSettings', () => {
    test('returns settings', async () => {
      fetch.mockImplementationOnce(() => Promise.resolve({
        json: () => Promise.resolve({ someKey: 'someValue' }),
      }));
      const result = await getSettings();
      expect(result).toEqual({ someKey: 'someValue' });
    });

    test('returns error', async () => {
      fetch.mockImplementationOnce(() => Promise.reject(new Error('error')));
      try { await getSettings(); } catch (e) {
        expect(e.message).toBe('error');
      }
    });
  });
});
