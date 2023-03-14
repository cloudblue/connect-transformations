/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/

// prepare UI components
export const prepareSettings = (settings) => {
  try {
    return `<p>${JSON.stringify(settings)}</p>`;
  } catch (e) { return ''; }
};

export const prepareTransformations = (transformations) => {
  try {
    return transformations.reduce((list, transformation) => `${list}<li class="list-item">
        <div class="list-item-content">
          <h4>${transformation.id} - ${transformation.name}</h4>
          <p>${transformation.class_fqn}</p>
          <p>${transformation.status}</p>
          <p>${transformation.description}</p>
        </div>
      </li>`, '');
  } catch (e) { return ''; }
};

// render UI components
export const renderSettings = (settings) => {
  const element = document.getElementById('settings');
  element.innerHTML = settings;
};

export const renderTransformations = (transformations) => {
  const element = document.getElementById('transformations');
  element.innerHTML = transformations;
};

// render UI components - show/hide
export const showComponent = (id) => {
  if (!id) return;
  const element = document.getElementById(id);
  element.classList.remove('hidden');
};

export const hideComponent = (id) => {
  if (!id) return;
  const element = document.getElementById(id);
  element.classList.add('hidden');
};
