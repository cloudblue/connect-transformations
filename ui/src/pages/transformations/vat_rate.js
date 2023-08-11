/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';
import '../../../styles/app.styl';
import '../../../styles/vat_rate.css';
import {
  getColumnLabel,
  validate,
} from '../../utils';

import {
  hideComponent,
  showComponent,
} from '../../components';


const vatRate = (app) => {
  if (!app) {
    return;
  }

  let columns = [];

  app.listen('config', config => {
    const {
      context: { available_columns: availableColumns },
      settings,
    } = config;

    columns = availableColumns;

    const inputColumnSelect = document.getElementById('input-column');
    const outputColumnInput = document.getElementById('output-column');
    columns.forEach(column => {
      const isSelected = settings && column.id === settings.from;
      const colLabel = getColumnLabel(column);
      const option = isSelected
        ? `<option value="${column.id}" selected>${colLabel}</option>`
        : `<option value="${column.id}">${colLabel}</option>`;
      inputColumnSelect.innerHTML += option;
    });

    if (settings) {
      outputColumnInput.value = settings.to;
      if (settings.action_if_not_found === 'leave_empty') {
        document.getElementById('leave_empty').checked = true;
      } else {
        document.getElementById('fail').checked = true;
      }
    } else {
      document.getElementById('leave_empty').checked = true;
    }
    hideComponent('loader');
    showComponent('app');
  });

  app.listen('save', async () => {
    const inputColumnValue = document.getElementById('input-column').value;
    const inputColumn = columns.find(column => column.id === inputColumnValue);
    const outputColumnValue = document.getElementById('output-column').value;
    const actionIfNotFound = document.getElementById('leave_empty').checked ? 'leave_empty' : 'fail';

    if (outputColumnValue === inputColumn.name) {
      app.emit('validation-error', 'This fields may not be equal: columns.input.name, columns.output.name.');
    } else if (outputColumnValue === '' || outputColumnValue === null) {
      app.emit('validation-error', 'Output column name is required.');
    } else {
      const data = {
        settings: {
          from: inputColumn.name,
          to: outputColumnValue,
          action_if_not_found: actionIfNotFound,
        },
        columns: {
          input: [
            inputColumn,
          ],
          output: [
            {
              name: outputColumnValue,
              type: 'integer',
              description: '',
            },
          ],
        },
      };

      try {
        const overview = await validate('vat_rate', data);
        if (overview.error) {
          throw new Error(overview.error);
        }
        app.emit('save', {
          data: { ...data, ...overview },
          status: 'ok',
        });
      } catch (e) {
        app.emit('validation-error', e);
      }
    }
  });
};

createApp({ })
  .then(vatRate);
