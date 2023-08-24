/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';
import '../../../styles/manual.css';
import '../../../styles/app.styl';
import {
  buildOutputColumnInput,
  hideComponent,
  showComponent,
} from '../../components';
import {
  getDataFromOutputColumnInput,
} from '../../utils';


export const createManualOutputRow = (parent, index, column) => {
  const item = document.createElement('div');
  item.classList.add('list-wrapper');
  item.id = `wrapper-${index}`;
  parent.appendChild(item);
  buildOutputColumnInput(item, column, index, true);
};

export const manual = (app) => {
  if (!app) {
    return;
  }

  hideComponent('app');
  hideComponent('loader');

  let availableColumns;
  let rowIndex = 0;

  const descriptionElement = document.getElementById('description-text');
  const settingsElement = document.getElementById('settings-text');

  app.listen('config', (config) => {
    const {
      columns: { input: inputColumns, output: outputColumns },
      context: { available_columns }, // eslint-disable-line camelcase
      overview,
      settings,
    } = config;

    availableColumns = available_columns; // eslint-disable-line camelcase

    descriptionElement.value = overview || '';
    settingsElement.value = settings ? JSON.stringify(settings) : '{}';

    const inputColumnsEditElement = document.getElementById('edit-input-columns');
    availableColumns.forEach((column) => {
      const checked = inputColumns.some((inputColumn) => inputColumn.id === column.id);
      const inputColumnRow = document.createElement('tr');
      inputColumnRow.innerHTML = `
        <td>${column.id.slice(-3)}</td>
        <td>${column.name}</td>
        <td>${column.type}</td>
        <td>${column.description ? column.description : '-'}</td>
        <td><input id="${column.id}" type="checkbox" ${checked ? 'checked' : ''} /></td>
      `;
      inputColumnsEditElement.appendChild(inputColumnRow);
    });

    const outputColumnsElement = document.getElementById('output-columns');

    if (outputColumns.length > 0) {
      outputColumns.forEach((outputColumn, index) => {
        rowIndex = index;
        createManualOutputRow(outputColumnsElement, rowIndex, outputColumn);
      });
    } else {
      createManualOutputRow(outputColumnsElement, rowIndex);
    }

    document.getElementById('add').addEventListener('click', () => {
      rowIndex += 1;
      createManualOutputRow(outputColumnsElement, rowIndex);
    });

    descriptionElement.addEventListener('keyup', () => {
      const maxLength = 2000;
      const currentLength = descriptionElement.value.length;
      const descriptionLabel = document.getElementById('description-label');
      const errorHint = document.getElementById('description-text-hint');
      const descriptionCounter = document.getElementById('description-text-counter');

      descriptionCounter.innerHTML = `${currentLength} / ${maxLength}`;
      app.emit('overview-changed', descriptionElement.value);

      if (currentLength > Number(maxLength)) {
        descriptionLabel.classList.add('error--text');
        descriptionCounter.classList.add('error--text');
        descriptionElement.classList.add('error--input');
        errorHint.classList.remove('text-hidden');
      } else {
        descriptionLabel.classList.remove('error--text');
        descriptionCounter.classList.remove('error--text');
        descriptionElement.classList.remove('error--input');
        errorHint.classList.add('text-hidden');
      }
    });

    hideComponent('loader');
    showComponent('app');
  });

  app.listen('save', () => {
    const data = {
      settings: {},
      columns: {
        input: [],
        output: [],
      },
      overview: '',
    };

    try {
      data.overview = descriptionElement.value;
      data.settings = JSON.parse(settingsElement.value);
      const inputColumns = document.querySelectorAll('#edit-input-columns-table input[type="checkbox"]:checked');
      inputColumns.forEach((inputColumn) => {
        const availableColumn = availableColumns.find((column) => column.id === inputColumn.id);
        data.columns.input.push(availableColumn);
      });

      const outputs = document.getElementsByClassName('output-column-container');
      for (let i = 0; i < outputs.length; i += 1) {
        const index = outputs[i].id;
        data.columns.output.push(getDataFromOutputColumnInput(index));
      }

      app.emit('save', {
        data,
        status: 'ok',
      });
    } catch (e) {
      app.emit('validation-error', e);
    }
  });
};

createApp({ })
  .then(manual);
