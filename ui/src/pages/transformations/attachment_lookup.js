/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';
import '../../../styles/app.styl';
import '../../../styles/attachment_lookup.styl';
import {
  getAddButton,
  getDeleteButton,
  hideComponent,
  hideError,
  showComponent,
  showError,
} from '../../components';

import {
  getAttachments,
  getColumnLabel,
  validate,
} from '../../utils';


export const getRequiredValue = (id, errorMessage) => {
  const { value } = document.getElementById(id);
  if (!value) {
    throw new Error(errorMessage);
  }

  return value;
};

export const fillSelect = (options, id, value) => {
  const select = document.getElementById(id);
  if (value) {
    select.value = value;
  }
  select.innerHTML = '';
  options.forEach((item) => {
    const option = document.createElement('option');
    option.value = item.id;
    option.text = getColumnLabel(item);
    if (item.id === value) {
      option.selected = true;
    }
    select.appendChild(option);
  });
};


export const createLookupRow = (parent, index, options, input, output) => {
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
      <input type="text" placeholder="Attachment Field name" style="width: 35%;" ${output ? `value="${output}"` : ''} />
      <button id="delete-lk-${index}" style="display: initial; width: 20%" class="button delete-button">DELETE</button>
    `;
  parent.appendChild(item);

  document.getElementById(`delete-lk-${index}`).addEventListener('click', () => {
    if (document.getElementsByClassName('list-wrapper').length === 1) {
      showError('You need to have at least one lookup');
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


export const createMappingRow = (index, from, to) => {
  let lastRowIndex = 0;
  // remove existing ADD button and add REMOVE button to last col of the row
  const addButton = document.getElementById('add-button');
  if (addButton) {
    // get data-row-index from the ADD button and add delete button to this row
    lastRowIndex = addButton.getAttribute('data-row-index');
    addButton.remove();
    document
      .getElementById(`row-${lastRowIndex}`)
      .children[3]
      .appendChild(getDeleteButton(lastRowIndex));
  }

  const row = document.createElement('div');
  row.classList.add('row');
  row.id = `row-${index}`;
  row.innerHTML = `
    <div class="col button-col">
    </div>
    <div class="col">
      <input type="text" placeholder="Input column" value="${from || ''}" />
    </div>
    <div class="col">
      <input type="text" placeholder="Output column" value="${to || ''}" />
    </div>
    <div class="col button-col">
    </div>`;
  row.children[0].appendChild(getAddButton(index));
  document.getElementById('mapping').appendChild(row);

  const deleteButton = document.getElementById(`delete-${lastRowIndex}`);
  if (deleteButton) {
    deleteButton.addEventListener('click', () => {
      document.getElementById(`row-${lastRowIndex}`).remove();
      // replace delete button with add button if there is only one row left
      if (document.getElementsByClassName('row').length === 1) {
        document.getElementsByClassName('row')[0].children[0].appendChild(getAddButton(lastRowIndex));
      }
    });
  }
  document.getElementById('add-button').addEventListener('click', () => {
    createMappingRow(index + 1);
  });
};

export const lookupSpreadsheet = (app) => {
  if (!app) return;

  let attachments = [];
  let columns = [];
  let rowIndex = 0;

  app.listen('config', async (config) => {
    try {
      const {
        context: {
          stream: { id: streamId },
          available_columns: availableColumns,
        },
        columns: { input: inputColumns },
        settings,
      } = config;

      attachments = await getAttachments(streamId);
      columns = availableColumns;

      const content = document.getElementById('lookup');

      if (settings) {
        const {
          file,
          sheet,
          map_by: mapBy,
          mapping,
        } = settings;

        (Array.isArray(mapBy) ? mapBy : [mapBy]).forEach((item, i) => {
          const inputColumn = inputColumns.find((col) => col.name === item.input_column);
          const outputColumn = item.attachment_column;
          rowIndex = i;
          createLookupRow(content, rowIndex, columns, inputColumn, outputColumn);
        });

        const attachmentFound = attachments.find((item) => item.file === file);
        let fileId = null;
        if (attachmentFound == null) {
          const fileName = file.split('/').pop();
          app.emit('validation-error', `The attached file ${fileName} cannot be found, It might be deleted. Please choose another one.`);
        } else {
          fileId = attachmentFound.id;
        }
        fillSelect(attachments, 'attachment', fileId);
        document.getElementById('sheet').value = sheet;
        mapping.forEach((item, index) => {
          createMappingRow(index, item.from, item.to);
        });
      } else {
        fillSelect(attachments, 'attachment');
        createMappingRow(0);
        createLookupRow(content, rowIndex, columns);
      }

      document.getElementById('add-lookup-button').addEventListener('click', () => {
        rowIndex += 1;
        createLookupRow(content, rowIndex, columns);
      });
    } catch (error) {
      app.emit('validation-error', error);
    } finally {
      hideComponent('loader');
      showComponent('app');
    }
  });

  app.listen('save', async () => {
    hideError();

    try {
      const fileId = getRequiredValue('attachment', 'Please select attachment');
      const { file } = attachments.find((item) => item.id === fileId);
      const sheet = document.getElementById('sheet').value;

      const inputColumns = [];
      const mapBy = [];
      const lookups = document.querySelectorAll('#lookup .list-wrapper');
      lookups.forEach((lookup) => {
        const inputId = lookup.children[0].value;
        const attchName = lookup.children[1].value;
        const inputColumn = columns.find((column) => column.id === inputId);
        if (inputId && attchName) {
          mapBy.push({ input_column: inputColumn.name, attachment_column: attchName });
          inputColumns.push(inputColumn);
        } else {
          throw new Error('Please fill all mapping rows');
        }
      });

      const outputColumns = [];
      const mapping = [];
      const rows = document.querySelectorAll('#mapping .row');
      rows.forEach((row) => {
        const from = row.children[1].children[0].value;
        const to = row.children[2].children[0].value;
        if (from && to) {
          mapping.push({ from, to });
          outputColumns.push({
            name: to,
          });
        } else {
          throw new Error('Please fill all mapping rows');
        }
      });

      const data = {
        settings: {
          file,
          sheet,
          map_by: mapBy,
          mapping,
        },
        columns: {
          input: inputColumns,
          output: outputColumns,
        },
      };

      const overview = await validate('attachment_lookup', data);
      if (overview.error) {
        throw new Error(overview.error);
      }
      app.emit('save', { data: { ...data, ...overview }, status: 'ok' });
    } catch (error) {
      app.emit('validation-error', error);
    }
  });
};

createApp({ }).then(lookupSpreadsheet);
