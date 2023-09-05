/*
Copyright (c) 2023, CloudBlue LLC
All rights reserved.
*/
import createApp from '@cloudblueconnect/connect-ui-toolkit';
import '@fontsource/roboto/500.css';
import '../../../styles/index.css';
import '../../../styles/split_column.css';
import '../../../styles/app.styl';
import {
  getColumnLabel,
  getDataFromOutputColumnInput,
  getGroups,
  validate,
} from '../../utils';
import {
  buildOutputColumnInput,
  hideComponent,
  showComponent,
} from '../../components';


function getCurrentGroups() {
  const outputContainers = document.getElementsByClassName('output-column-container');
  const currentGroups = {};

  for (let i = 0; i < outputContainers.length; i += 1) {
    const index = outputContainers[i].id;
    currentGroups[index] = getDataFromOutputColumnInput(index);
  }

  return currentGroups;
}

function buildGroups(groups) {
  const parent = document.getElementById('output');
  parent.innerHTML = '';

  Object.keys(groups).forEach(index => {
    const column = groups[index];
    const item = document.createElement('div');
    item.classList.add('list-wrapper');
    parent.appendChild(item);
    buildOutputColumnInput({
      column,
      index,
      parent: item,
      showDelete: false,
    });
  });
}

export const createGroupRows = async (app) => {
  const groups = getCurrentGroups();
  const pattern = document.getElementById('pattern').value;
  app.emit('validation-error', '');
  if (pattern) {
    const body = { pattern, groups };
    const response = await getGroups(body);
    if (response.error) {
      app.emit('validation-error', response.error);
    } else {
      buildGroups(response.groups);
    }
  } else {
    app.emit('validation-error', 'The regular expression is empty');
  }
};

export const splitColumn = (app) => {
  if (!app) return;

  let columns = [];

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
      option.text = getColumnLabel(column);
      document.getElementById('column').appendChild(option);
    });

    if (settings) {
      document.getElementById('pattern').value = settings.regex.pattern;
      const columnId = columns.find((c) => c.name === settings.from).id;
      document.getElementById('column').value = columnId;
      buildGroups(settings.regex.groups);
    }

    document.getElementById('refresh').addEventListener('click', () => {
      createGroupRows(app);
    });
    hideComponent('loader');
    showComponent('app');
  });

  app.listen('save', async () => {
    const data = {
      settings: {
        regex: {
          groups: {},
        },
      },
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
    data.columns.input.push(inputColumn);

    const groups = getCurrentGroups();

    Object.entries(groups).forEach(([i, group]) => {
      data.columns.output.push(group);
      data.settings.regex.groups[i] = { name: group.name };
    });

    data.settings.from = inputColumn.name;
    data.settings.regex.pattern = document.getElementById('pattern').value;

    try {
      const overview = await validate('split_column', data);
      if (overview.error) {
        throw new Error(overview.error);
      }

      if (data.columns.output.length === 0) {
        throw new Error('No output columns defined');
      }
      app.emit('save', { data: { ...data, ...overview }, status: 'ok' });
    } catch (e) {
      hideComponent('loader');
      showComponent('app');

      app.emit('validation-error', e);
    }
  });
};

createApp({ })
  .then(splitColumn);
