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
  showError,
} from '../../components';
import {
  validate,
} from '../../utils';


const filterRow = (app) => {
  if (!app) return;

  let columns = [];

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

    availableColumns.forEach((column) => {
      const option = document.createElement('option');
      option.value = column.id;
      option.text = column.name;
      document.getElementById('column').appendChild(option);
    });

    if (settings) {
      document.getElementById('value').value = settings.value;
      const columnId = columns.find((c) => c.name === settings.from).id;
      document.getElementById('column').value = columnId;
    }
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
    const selectedColumn = inputSelector.options[inputSelector.selectedIndex].text;
    const inputColumn = columns.find((column) => column.id === inputSelector.value);
    data.columns.input.push(inputColumn);
    data.columns.output.push(
      {
        name: `${selectedColumn}_INSTRUCTIONS`,
        type: 'string',
        output: false,
      },
    );

    const inputValue = document.getElementById('value');
    data.settings = {
      from: selectedColumn,
      value: inputValue.value,
    };

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
      showError(e);
      showComponent('app');
      hideComponent('loader');
    }
  });
};

createApp({ })
  .then(filterRow);
