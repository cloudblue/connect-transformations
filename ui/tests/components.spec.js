/*
Copyright (c) 2022, CloudBlue LLC
All rights reserved.
*/
import {
  hideComponent,
  prepareSettings,
  prepareTransformations,
  renderSettings,
  renderTransformations,
  showComponent,
} from '@/components';


describe('components.js', () => {
  describe('prepareSettings', () => {
    test('returns "" if settings are empty', () => {
      const result = prepareSettings({});
      expect(result).toBe(`<p>{}</p>`);
    });

    test('returns a representation of settings', () => {
      const result = prepareSettings({
        token: 'ABC', markerplaces: [],
      });
      expect(result).toBe(`<p>{"token":"ABC","markerplaces":[]}</p>`);
    });
  });

  describe('prepareTransformations', () => {
    test('returns a list of transformations', () => {
      const result = prepareTransformations([{
        id: 'TR-001', name: 'name', status: 'active',
        description: 'description', class_fqn: 'package.Class',
      }]);
      expect(result).toBe(`<li class="list-item">
        <div class="list-item-content">
          <h4>TR-001 - name</h4>
          <p>package.Class</p>
          <p>active</p>
          <p>description</p>
        </div>
      </li>`);
    });
  });

  describe('renderSettings', () => {
    test('renders a settings', () => {
      document.body.innerHTML = '<div id="settings"></div>';
      renderSettings('<p>Bee</p>');
      expect(document.getElementById('settings').innerHTML).toBe('<p>Bee</p>');
    });
  });

  describe('renderTransformations', () => {
    test('renders a list of transformations', () => {
      document.body.innerHTML = '<div id="transformations"></div>';
      renderTransformations('<li>item</li>');
      expect(document.getElementById('transformations').innerHTML).toBe('<li>item</li>');
    });
  });

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