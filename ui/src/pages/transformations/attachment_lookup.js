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

export const loockupSpreadsheet = (app) => {
  if (!app) return;

  let attachments = [];
  let columns = [];

  app.listen('config', async (config) => {
    try {
      const {
        context: {
          stream: { id: streamId },
          available_columns: availableColumns,
        },
        settings,
      } = config;

      attachments = await getAttachments(streamId);
      columns = availableColumns;

      if (settings) {
        const {
          file,
          sheet,
          map_by: {
            input_column: inputColumnName,
            attachment_column: attachmentColumn,
          },
          mapping,
        } = settings;

        const inputColumn = columns.find((item) => item.name === inputColumnName);
        fillSelect(columns, 'input-column', inputColumn.id);
        const attachmentFound = attachments.find((item) => item.file === file);
        let fileId = null;
        if (attachmentFound == null) {
          const fileName = file.split('/').pop();
          showError(`The attached file ${fileName} cannot be found, It might be deleted. Please choose another one.`);
        } else {
          fileId = attachmentFound.id;
        }
        fillSelect(attachments, 'attachment', fileId);
        document.getElementById('attachment-column').value = attachmentColumn;
        document.getElementById('sheet').value = sheet;
        mapping.forEach((item, index) => {
          createMappingRow(index, item.from, item.to);
        });
      } else {
        fillSelect(columns, 'input-column');
        fillSelect(attachments, 'attachment');
        createMappingRow(0);
      }
    } catch (error) {
      showError(error);
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
      const inputColumnId = getRequiredValue('input-column', 'Please select input column');
      const inputColumn = columns.find((item) => item.id === inputColumnId);
      const attachmentColumn = getRequiredValue('attachment-column', 'Please select attachment column');

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
          showError('Please fill all mapping rows');
          throw new Error('Please fill all mapping rows');
        }
      });

      const data = {
        settings: {
          file,
          sheet,
          map_by: {
            input_column: inputColumn.name,
            attachment_column: attachmentColumn,
          },
          mapping,
        },
        columns: {
          input: [inputColumn],
          output: outputColumns,
        },
      };

      const overview = await validate('attachment_lookup', data);
      if (overview.error) {
        throw new Error(overview.error);
      }
      app.emit('save', { data: { ...data, ...overview }, status: 'ok' });
    } catch (error) {
      showError(error);
    }
  });
};

createApp({ }).then(loockupSpreadsheet);
