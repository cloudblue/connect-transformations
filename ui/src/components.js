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

export const getAddSvg = () => '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24"><path d="M0 0h24v24H0z" fill="none"/><path d="M19 13H13v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>';

export const getDeleteSvg = () => '<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 0 24 24" width="24"><path d="M0 0h24v24H0z" fill="none"/><path d="M0 0h24v24H0V0z" fill="none"/><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zm2.46-7.12l1.41-1.41L12 12.59l2.12-2.12 1.41 1.41L13.41 14l2.12 2.12-1.41 1.41L12 15.41l-2.12 2.12-1.41-1.41L10.59 14l-2.13-2.12zM15.5 4l-1-1h-5l-1 1H5v2h14V4z"/></svg>';

export const getAddButton = (index) => {
  const button = document.createElement('button');
  button.classList.add('add-button');
  button.id = 'add-button';
  button.setAttribute('data-row-index', index);
  button.innerHTML = getAddSvg();

  return button;
};

export const getDeleteButton = (index) => {
  const button = document.createElement('button');
  button.classList.add('delete-button');
  button.id = `delete-${index}`;
  button.setAttribute('data-row-index', index);
  button.innerHTML = getDeleteSvg();

  return button;
};


export const buildOutputColumnInput = ({
  parent,
  column,
  index,
  additionalInputs,
  showName = true,
  showType = true,
  showDelete = true,
}) => {
  const container = document.createElement('div');
  container.id = index;
  container.classList.add('output-column-container');

  parent.appendChild(container);

  if (showName) {
    const nameInput = document.createElement('input');
    nameInput.classList.add('output-column-name');
    nameInput.type = 'text';
    nameInput.id = `name-${container.id}`;
    nameInput.placeholder = 'Column name';
    nameInput.value = column?.name || '';
    container.appendChild(nameInput);
  }

  if (showType) {
    const typeSelect = document.createElement('select');
    typeSelect.classList.add('output-column-type');
    typeSelect.style.flexGrow = '1';
    typeSelect.id = `type-${container.id}`;
    typeSelect.innerHTML = `
      <option value="string" selected>String</option>
      <option value="integer">Integer</option>
      <option value="decimal">Decimal</option>
      <option value="boolean">Boolean</option>
      <option value="datetime">Datetime</option>
    `;
    typeSelect.value = column?.type || 'string';
    container.appendChild(typeSelect);

    const precisionSelect = document.createElement('select');
    precisionSelect.classList.add('output-column-precision');
    precisionSelect.id = `precision-${container.id}`;
    typeSelect.style.flexShrink = '100';
    precisionSelect.innerHTML = `
      <option value="auto" selected>Auto</option>
      <option value="1">1 decimal</option>
      <option value="2">2 decimals</option>
      <option value="3">3 decimals</option>
      <option value="4">4 decimals</option>
      <option value="5">5 decimals</option>
      <option value="6">6 decimals</option>
      <option value="7">7 decimals</option>
      <option value="8">8 decimals</option>
    `;

    if (column?.type === 'decimal') {
      precisionSelect.style.display = 'block';
      precisionSelect.value = column.constraints?.precision || 'auto';
    } else {
      precisionSelect.style.display = 'none';
      precisionSelect.value = null;
    }

    container.appendChild(precisionSelect);

    typeSelect.addEventListener('change', () => {
      if (typeSelect.value === 'decimal') {
        precisionSelect.style.display = 'block';
        precisionSelect.value = 'auto';
      } else {
        precisionSelect.style.display = 'none';
        precisionSelect.value = null;
      }
    });
  }

  additionalInputs?.forEach(customInput => container.appendChild(customInput));

  if (showDelete) {
    const deleteButton = document.createElement('button');
    deleteButton.id = `delete-${container.id}`;
    deleteButton.classList.add('button', 'delete-button', 'output-column-delete');
    deleteButton.innerHTML = 'DELETE';
    container.appendChild(deleteButton);

    deleteButton?.addEventListener('click', () => {
      parent.remove();
      const buttons = document.getElementsByClassName('delete-button');
      if (buttons.length === 1) {
        buttons[0].disabled = true;
      }
    });

    const buttons = document.getElementsByClassName('delete-button');
    for (let i = 0; i < buttons.length; i += 1) {
      if (buttons.length === 1) {
        buttons[i].disabled = true;
      } else {
        buttons[i].disabled = false;
      }
    }
  }
};
