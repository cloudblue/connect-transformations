/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import {
  validate,
} from '../src/utils';


global.fetch = jest.fn(() => Promise.resolve({
  json: () => Promise.resolve({}),
}));


describe('utils.js API calls', () => {
  describe('validate', () => {
    beforeEach(() => {
      fetch.mockClear();
    });
    it('calls the backend API', () => {
      validate({});
      expect(fetch).toHaveBeenCalledTimes(1);
    });
  });
});
