/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/

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

export const showError = (message) => {
  const oldError = document.getElementById('error');
  if (oldError) {
    oldError.remove();
  }
  const error = document.createElement('div');
  error.id = 'error';
  error.innerHTML = `<div class="c-alert">${message}</div>`;
  document.getElementsByTagName('body')[0].appendChild(error);
  document.getElementById('error').scrollIntoView();
};

export const hideError = () => {
  const error = document.getElementById('error');
  if (error) {
    error.remove();
  }
};
