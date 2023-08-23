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
  getColumnLabel,
  validate,
} from '../../utils';


const cleanCopyRows = parent => {
  parent.innerHTML = '';
};


const createCopyRow = (parent, index, options, input, output) => {
  const item = document.createElement('div');
  item.classList.add('list-wrapper');
  item.id = `wrapper-${index}`;
  item.innerHTML = `
      <select class="list" style="width: 35%;" ${input ? `value="${input.id}"` : ''}>
        ${options.map((column) => `
          <option value="${column.id}" ${input && input.id === column.id ? 'selected' : ''}>
            ${getColumnLabel(column)}
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

const cleanField = elem => {
  elem.setAttribute('disabled', '');
  elem.value = '';
};

const airtable = (app) => {
  if (!app) return;
  hideComponent('loader');
  showComponent('app');

  let airtableColumns = [];
  let apiKey;
  let baseId;
  let tableId;
  let tables;
  let mapInputColumn;
  let mapAirtableColumn;
  const baseSelect = document.getElementById('base-select');
  const content = document.getElementById('content');
  const tableSelect = document.getElementById('table-select');
  const keyInput = document.getElementById('key-input');
  const inputColumnSelect = document.getElementById('input-column-select');
  const airtableFieldSelect = document.getElementById('field-select');
  const addButton = document.getElementById('add');

  app.listen('config', async (config) => {
    const {
      context: { available_columns: availableColumns },
      columns: { output: outputColumns },
      settings,
    } = config;

    let airtableBases;
    let rowIndex = 0;

    keyInput.addEventListener('input', async () => {
      cleanField(baseSelect);
      cleanField(tableSelect);
      cleanField(inputColumnSelect);
      cleanField(airtableFieldSelect);
      cleanCopyRows(content);
      apiKey = keyInput.value;
      if (apiKey.length < 50) return;

      try {
        airtableBases = await getAirtableBases(apiKey);
        if (airtableBases.error) {
          throw new Error(airtableBases.error);
        }
        hideError();
      } catch (e) {
        app.emit('validation-error', e);
      }

      createOptions('base-select', airtableBases);
      removeDisabled('base-select');
    });

    baseSelect.addEventListener('change', async () => {
      cleanField(tableSelect);
      cleanField(inputColumnSelect);
      cleanField(airtableFieldSelect);
      cleanCopyRows(content);

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
      createOptions('input-column-select', availableColumns);
      removeDisabled('field-select');
      removeDisabled('input-column-select');
    });

    inputColumnSelect.addEventListener('change', () => {
      mapInputColumn = availableColumns.find((column) => column.id === inputColumnSelect.value);
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

    if (settings) {
      showComponent('loader');
      apiKey = settings.api_key;
      baseId = settings.base_id;
      tableId = settings.table_id;

      try {
        airtableBases = await getAirtableBases(apiKey);
        tables = await getAirtableTables(apiKey, settings.base_id);

        if (airtableBases.error) {
          throw new Error(airtableBases.error);
        }
        hideError();
      } catch (e) {
        app.emit('validation-error', e);
      }

      const currentTable = tables.find(x => x.id === settings.table_id);
      airtableColumns = currentTable.columns;

      createOptions('base-select', airtableBases);
      createOptions('table-select', tables);
      createOptions('field-select', airtableColumns);
      createOptions('input-column-select', availableColumns);

      keyInput.value = settings.api_key;
      baseSelect.value = settings.base_id;
      tableSelect.value = settings.table_id;

      mapInputColumn = availableColumns
        .find((column) => column.name === settings.map_by.input_column);
      inputColumnSelect.value = mapInputColumn.id;

      mapAirtableColumn = airtableColumns
        .find((column) => column.name === settings.map_by.airtable_column);
      airtableFieldSelect.value = mapAirtableColumn.id;

      removeDisabled('base-select');
      removeDisabled('table-select');
      removeDisabled('field-select');
      removeDisabled('input-column-select');
      removeDisabled('add');

      settings.mapping.forEach((mapping, i) => {
        const inputColumn = airtableColumns.find((column) => column.name === mapping.from);
        const outputColumn = outputColumns.find((column) => column.name === mapping.to);
        rowIndex = i;
        createCopyRow(content, rowIndex, airtableColumns, inputColumn, outputColumn);
      });
      hideComponent('loader');
    }
  });

  app.listen('save', async () => {
    let overview = '';
    if (!mapInputColumn || !mapAirtableColumn) {
      app.emit('validation-error', 'Please complete all the fields');

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
      app.emit('validation-error', e);
    }
  });
};

createApp({ })
  .then(airtable);
