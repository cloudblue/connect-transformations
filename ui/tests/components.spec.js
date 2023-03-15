/*
Copyright (c) 2022, CloudBlue LLC
All rights reserved.
*/
import {
  hideComponent,
  showComponent,
} from '@/components';


describe('components.js', () => {
  describe('showLoader', () => {
    beforeEach(() => {
      document.body.innerHTML = '<div id="loader" class="hidden"></div>';
      showComponent('loader');
    });
    it('shows a loader', () => {
      expect(document.getElementById('loader').classList.contains('hidden')).toBe(false);
    });
  });

  describe('showComponent without passing id', () => {
    beforeEach(() => {
      document.body.innerHTML = '<div id="component" class="hidden"></div>';
      showComponent();
    });
    it('does not show a component', () => {
      expect(document.getElementById('component').classList.contains('hidden')).toBe(true);
    });
  });

  describe('hideLoader', () => {
    beforeEach(() => {
      document.body.innerHTML = '<div id="loader"></div>';
      hideComponent('loader');
    });
    it('hides a loader', () => {
      expect(document.getElementById('loader').classList.contains('hidden')).toBe(true);
    });
  });

  describe('hideComponent without passing id', () => {
    beforeEach(() => {
      document.body.innerHTML = '<div id="component"></div>';
      hideComponent();
    });
    it('does not hide a component', () => {
      expect(document.getElementById('component').classList.contains('hidden')).toBe(false);
    });
  });
});