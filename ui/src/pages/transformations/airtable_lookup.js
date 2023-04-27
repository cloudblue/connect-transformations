/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';
import '../../../styles/airtable_lookup.css';
import '../../../styles/app.styl';
import {
  hideComponent,
  hideError,
  showComponent,
  showError,
} from '../../components';
import {
  getAirtableBases,
  getAirtableTables,
  validate,
} from '../../utils';


const createCopyRow = (parent, index, options, input, output) => {
  const item = document.createElement('div');
  item.classList.add('list-wrapper');
  item.id = `wrapper-${index}`;
  item.style.width = '100%';
  item.innerHTML = `
      <select class="list" style="width: 35%;" ${input ? `value="${input.id}"` : ''}>
        ${options.map((column) => `
          <option value="${column.id}" ${input && input.id === column.id ? 'selected' : ''}>
            ${column.name}
          </option>`).join(' ')}
      </select>
      <input type="text" placeholder="Copy column name" style="width: 35%;" ${output ? `value="${output.name}"` : ''} />
      <button id="delete-${index}" class="button delete-button">DELETE</button>
    `;
  parent.appendChild(item);

  document.getElementById(`delete-${index}`).addEventListener('click', () => {
    if (document.getElementsByClassName('list-wrapper').length === 1) {
      showError('You need to have at least one row');
    } else {
      document.getElementById(`wrapper-${index}`).remove();
      const buttons = document.getElementsByClassName('delete-button');
      if (buttons.length === 1) {
        buttons[0].disabled = true;
      }
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
};

const createOptions = (selectId, options) => {
  const select = document.getElementById(selectId);
  select.innerHTML = `
        <option disabled selected value>Please select an option</option>
        ${options.map((column) => `
          <option value="${column.id}">
            ${column.name}
          </option>`).join(' ')}
    `;
};

const removeDisabled = selector => document.getElementById(selector).removeAttribute('disabled');

const airtable = (app) => {
  if (!app) return;
  hideComponent('loader');
  showComponent('app');

  let columns = [];
  let airtableColumns = [];
  let apiKey;
  let baseId;
  let tableId;
  let tables;
  let mapInputColumn;
  let mapAirtableColumn;
  const inputColumnSelect = document.getElementById('input-column-select');
  const airtableFieldSelect = document.getElementById('field-select');
  const addButton = document.getElementById('add');

  app.listen('config', (config) => {
    const baseSelect = document.getElementById('base-select');
    const content = document.getElementById('content');
    const tableSelect = document.getElementById('table-select');
    const keyInput = document.getElementById('key-input');
    let airtableBases;
    let rowIndex = 0;
    columns = config.context.available_columns;

    keyInput.addEventListener('input', async () => {
      apiKey = keyInput.value;
      if (apiKey.length < 50) return;

      try {
        airtableBases = await getAirtableBases(apiKey);
        if (airtableBases.error) {
          throw new Error(airtableBases.error);
        }
        hideError();
      } catch (e) {
        showError(e);
      }

      createOptions('base-select', airtableBases);
      removeDisabled('base-select');
    });

    baseSelect.addEventListener('change', async () => {
      baseId = baseSelect.value;
      tables = await getAirtableTables(apiKey, baseId);
      hideError();

      createOptions('table-select', tables);
      removeDisabled('table-select');
    });

    tableSelect.addEventListener('change', () => {
      tableId = tableSelect.value;
      const currentTable = tables.find(x => x.id === tableId);
      airtableColumns = currentTable.columns;
      hideError();

      createOptions('field-select', airtableColumns);
      createOptions('input-column-select', columns);
      removeDisabled('field-select');
      removeDisabled('input-column-select');
    });

    inputColumnSelect.addEventListener('change', () => {
      mapInputColumn = columns.find((column) => column.id === inputColumnSelect.value);
      if (mapAirtableColumn) removeDisabled('add');
      hideError();
    });

    airtableFieldSelect.addEventListener('change', () => {
      mapAirtableColumn = airtableColumns.find((column) => column.id === airtableFieldSelect.value);
      if (mapInputColumn) removeDisabled('add');
      hideError();
    });

    addButton.addEventListener('click', () => {
      rowIndex += 1;
      createCopyRow(content, rowIndex, airtableColumns);
    });
  });

  app.listen('save', async () => {
    let overview = '';
    if (!mapInputColumn || !mapAirtableColumn) {
      showError('Please complete all the fields');

      return;
    }

    const data = {
      settings: {
        api_key: apiKey,
        base_id: baseId,
        table_id: tableId,
        map_by: {
          input_column: mapInputColumn.name,
          airtable_column: mapAirtableColumn.name,
        },
        mapping: [],
      },
      columns: {
        input: [mapInputColumn],
        output: [],
      },
    };

    const form = document.getElementsByClassName('list-wrapper');
    // eslint-disable-next-line no-restricted-syntax
    for (const line of form) {
      const inputId = line.getElementsByTagName('select')[0].value;
      const outputName = line.getElementsByTagName('input')[0].value;

      const inputColumn = airtableColumns.find((column) => column.id === inputId);

      const outputColumn = {
        name: outputName,
        type: 'string',
        description: '',
      };
      const setting = {
        from: inputColumn.name,
        to: outputName,
      };
      data.settings.mapping.push(setting);
      data.columns.output.push(outputColumn);
    }

    try {
      overview = await validate('airtable_lookup', data);
      if (overview.error) {
        throw new Error(overview.error);
      }
      app.emit('save', { data: { ...data, ...overview }, status: 'ok' });
    } catch (e) {
      showError(e);
    }
  });
};

createApp({ })
  .then(airtable);

