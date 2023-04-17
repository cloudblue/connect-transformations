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
  getGroups,
  validate,
} from '../../utils';
import {
  hideComponent,
  showComponent,
  showError,
} from '../../components';


function getCurrentGroups(parent) {
  const descendents = parent.getElementsByTagName('input');
  const currentGroups = {};
  for (let i = 0; i < descendents.length; i += 1) {
    const element = descendents[i];
    currentGroups[element.id] = element.value;
  }

  return currentGroups;
}

function buildGroups(groups) {
  const parent = document.getElementById('output');
  parent.innerHTML = '';
  Object.values(groups).forEach(element => {
    Object.keys(element).forEach(groupKey => {
      const groupValue = element[groupKey];
      const item = document.createElement('div');
      item.style.width = '200px';
      item.innerHTML = `
      <input
      type="text" class="output-input" id="${groupKey}"
      placeholder="${groupKey} value"
      style="width: 100%;" value="${groupValue}"/>
      `;
      parent.appendChild(item);
    });
  });
}

export const createGroupRows = async () => {
  const parent = document.getElementById('output');
  const groups = getCurrentGroups(parent);
  const pattern = document.getElementById('pattern').value;
  if (pattern) {
    const body = { pattern, groups };
    const response = await getGroups(body);
    if (response.error) {
      showError(response.error);
    } else {
      buildGroups(response.groups);
    }
  } else {
    showError('The regular expression is empty');
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
      option.text = column.name;
      document.getElementById('column').appendChild(option);
    });

    if (settings) {
      document.getElementById('pattern').value = settings.regex.pattern;
      const columnId = columns.find((c) => c.name === settings.from).id;
      document.getElementById('column').value = columnId;
      buildGroups(settings.regex.groups);
    }

    document.getElementById('refresh').addEventListener('click', () => {
      createGroupRows();
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
    const selectedColumn = inputSelector.options[inputSelector.selectedIndex].text;
    const inputColumn = columns.find((column) => column.id === inputSelector.value);
    data.columns.input.push(inputColumn);

    const selector = document.getElementById('output');
    const options = selector.getElementsByTagName('input');
    for (let i = 0; i < options.length; i += 1) {
      const option = options[i];
      data.columns.output.push({
        name: option.value,
        type: inputColumn.type,
        description: '',
      });
    }

    data.settings = {
      from: selectedColumn,
      regex: {
        pattern: document.getElementById('pattern').value,
        groups: getCurrentGroups(document.getElementById('output')),
      },
    };

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
      showError(e);
      showComponent('app');
      hideComponent('loader');
    }
  });
};

createApp({ })
  .then(splitColumn);
