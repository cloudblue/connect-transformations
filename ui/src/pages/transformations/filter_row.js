/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';
import '../../../styles/filter_row.css';
import '../../../styles/app.styl';
import {
  hideComponent,
  showComponent,
} from '../../components';
import {
  getColumnLabel,
  validate,
} from '../../utils';


export const createAdditionalValue = (parent, index, value) => {
  const item = document.createElement('div');
  item.classList.add('list-wrapper');
  item.id = `wrapper-${index}`;
  item.style.width = '100%';
  item.innerHTML = `
      <input type="text" placeholder="Value" style="width: 50%;" ${value ? `value="${value}"` : ''} />
      <button id="delete-${index}" class="button delete-button">DELETE</button>
    `;
  parent.appendChild(item);

  document.getElementById(`delete-${index}`).addEventListener('click', () => {
    document.getElementById(`wrapper-${index}`).remove();
  });
};

export const filterRow = (app) => {
  if (!app) return;

  let columns = [];
  let rowIndex = 0;

  hideComponent('loader');
  showComponent('app');

  app.listen('config', (config) => {
    const {
      context: { available_columns: availableColumns },
      settings,
    } = config;

    showComponent('loader');
    hideComponent('app');

    columns = availableColumns;

    const content = document.getElementById('content');

    availableColumns.forEach((column) => {
      const option = document.createElement('option');
      option.value = column.id;
      option.text = getColumnLabel(column);
      document.getElementById('column').appendChild(option);
    });

    if (settings) {
      document.getElementById('value').value = settings.value;
      const columnId = columns.find((c) => c.name === settings.from).id;
      document.getElementById('column').value = columnId;

      if (settings.match_condition) {
        document.getElementById('match').checked = true;
      } else {
        document.getElementById('mismatch').checked = true;
      }

      if (settings.additional_values) {
        settings.additional_values.forEach((addVal, i) => {
          rowIndex = i;
          createAdditionalValue(content, rowIndex, addVal.value, i);
        });
      }
    } else {
      document.getElementById('match').checked = true;
    }

    document.getElementById('add').addEventListener('click', () => {
      rowIndex += 1;
      createAdditionalValue(content, rowIndex);
    });

    hideComponent('loader');
    showComponent('app');
  });

  app.listen('save', async () => {
    const data = {
      settings: {},
      columns: {
        input: [],
        output: [],
      },
      overview: '',
    };

    showComponent('loader');
    hideComponent('app');

    const inputSelector = document.getElementById('column');
    const inputColumn = columns.find((column) => column.id === inputSelector.value);
    const matchCondition = document.getElementById('match').checked;
    data.columns.input.push(inputColumn);
    data.columns.output.push(
      {
        name: `${inputColumn.name}_INSTRUCTIONS`,
        type: 'string',
        output: false,
      },
    );

    const inputValue = document.getElementById('value');
    data.settings = {
      from: inputColumn.name,
      value: inputValue.value,
      match_condition: matchCondition,
      additional_values: [],
    };

    const form = document.getElementsByClassName('list-wrapper');
    // eslint-disable-next-line no-restricted-syntax
    for (const line of form) {
      const val = line.getElementsByTagName('input')[0].value;
      const addVal = {
        value: val,
      };
      data.settings.additional_values.push(addVal);
    }

    try {
      const overview = await validate('filter_row', data);
      if (overview.error) {
        throw new Error(overview.error);
      }

      if (data.columns.output.length === 0) {
        throw new Error('No output columns defined');
      }
      app.emit('save', { data: { ...data, ...overview }, status: 'ok' });
    } catch (e) {
      app.emit('validation-error', e);
      showComponent('app');
      hideComponent('loader');
    }
  });
};

createApp({ })
  .then(filterRow);
